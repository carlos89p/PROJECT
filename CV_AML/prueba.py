import os
import json
import cv2
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm  # NUEVO: barra de progreso

# === RUTAS ===
json_path = "archive/train_dataset/train.json"
images_dir = "archive/train_dataset/train_images"
output_dir = "./dataset"
video_path = "traffic_sequence.mp4"

# === CREAR CARPETAS ===
os.makedirs(output_dir, exist_ok=True)
for label in ["red", "yellow", "green"]:
    os.makedirs(os.path.join(output_dir, label), exist_ok=True)

# === PROCESAR JSON Y GUARDAR RECORTES DESDE inbox ===
print("[INFO] Procesando anotaciones y generando recortes...")
with open(json_path, "r") as f:
    data = json.load(f)

contador = 0
for ann in tqdm(data["annotations"], desc="Recortando imágenes"):
    if "inbox" not in ann or len(ann["inbox"]) == 0:
        continue
    filename = ann["filename"].replace("\\", "/").split("/")[-1]
    img_path = os.path.join(images_dir, filename)
    if not os.path.exists(img_path):
        continue

    try:
        img = Image.open(img_path).convert("RGB")
        width, height = img.size
        for light in ann["inbox"]:
            color = light["color"]
            if color not in ["red", "yellow", "green"]:
                continue
            box = light["bndbox"]
            xmin = max(0, min(box["xmin"], width))
            ymin = max(0, min(box["ymin"], height))
            xmax = max(0, min(box["xmax"], width))
            ymax = max(0, min(box["ymax"], height))
            if xmax - xmin < 5 or ymax - ymin < 5:
                continue
            cropped = img.crop((xmin, ymin, xmax, ymax))
            save_path = os.path.join(output_dir, color, f"{contador:05d}.jpg")
            cropped.save(save_path)
            contador += 1
    except Exception as e:
        continue

print(f"[INFO] Recortes guardados: {contador}")

# === ENTRENAMIENTO DEL MODELO ===
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

dataset = datasets.ImageFolder(output_dir, transform=transform)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 16 * 16, 64), nn.ReLU(),
            nn.Linear(64, 3)
        )
    def forward(self, x):
        return self.fc(self.conv(x))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("[INFO] Entrenando el modelo...")
for epoch in range(10):
    model.train()
    total_loss = 0
    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/10"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # Validación
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (preds == labels).sum().item()
    print(f"[Epoch {epoch+1}] Loss: {total_loss:.4f} | Val Accuracy: {correct/total:.2%}")

torch.save(model.state_dict(), "traffic_light_classifier.pt")
print("[INFO] Modelo guardado como 'traffic_light_classifier.pt'")

# === USO EN VIDEO (detección simulada en región central) ===
model.eval()
to_tensor = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ No se pudo abrir el video.")
else:
    print("[INFO] Ejecutando clasificación en tiempo real...")
    class_names = ["red", "yellow", "green"]
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w, _ = frame.shape
        roi = frame[h//3:h//3+100, w//2-50:w//2+50]
        pil_img = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        input_tensor = to_tensor(pil_img).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = torch.max(output, 1)
            label = class_names[predicted.item()]
        msg = {"red": "STOP", "yellow": "SLOW DOWN", "green": "CONTINUE"}[label]
        color = {"red": (0, 0, 255), "yellow": (0, 255, 255), "green": (0, 255, 0)}[label]
        cv2.rectangle(frame, (w//2-50, h//3), (w//2+50, h//3+100), color, 2)
        cv2.putText(frame, msg, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        cv2.imshow("Traffic Light Classifier", frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
