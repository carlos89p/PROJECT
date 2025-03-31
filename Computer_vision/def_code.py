import os
import shutil
import random
from pathlib import Path
from ultralytics import YOLO
import cv2

# === CONFIGURACIÓN ===
DATASET_DIR = "dataset_yolo"
TRAIN_RATIO = 0.8
VIDEO_INPUT = "input_video.mp4"
VIDEO_OUTPUT = "output_video.mp4"
EPOCHS = 50
MODEL_SIZE = "yolov8n.yaml"  # Cambia por yolov8s.yaml o yolov8m.yaml si quieres
MODEL_NAME = "yolo_signs_v1"

# === 1. PREPARAR carpetas ===
dataset_path = Path(DATASET_DIR).resolve()
images_dir = dataset_path / "train" / "images"
labels_dir = dataset_path / "train" / "labels"
val_images_dir = dataset_path / "val" / "images"
val_labels_dir = dataset_path / "val" / "labels"
val_images_dir.mkdir(parents=True, exist_ok=True)
val_labels_dir.mkdir(parents=True, exist_ok=True)

# === 2. HACER SPLIT TRAIN / VAL ===
image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
random.shuffle(image_files)
train_count = int(len(image_files) * TRAIN_RATIO)
train_files = image_files[:train_count]
val_files = image_files[train_count:]

for file in val_files:
    label_file = labels_dir / f"{file.stem}.txt"
    if label_file.exists():
        shutil.move(str(file), val_images_dir / file.name)
        shutil.move(str(label_file), val_labels_dir / label_file.name)

# === 3. CREAR data.yaml con RUTA ABSOLUTA ===
yaml_path = dataset_path / "data.yaml"
with open(yaml_path, "w") as f:
    f.write(f"""path: {dataset_path}
train: train/images
val: val/images
nc: 58
names: [{', '.join([f"'{i}'" for i in range(58)])}]
""")

# === 4. ENTRENAR EL MODELO YOLOv8 ===
model = YOLO(MODEL_SIZE)
model.train(
    data=str(yaml_path),
    epochs=EPOCHS,
    imgsz=640,
    batch=16,
    name=MODEL_NAME
)

# === 5. DETECCIÓN EN VÍDEO CON MODELO ENTRENADO ===
model_path = f"runs/detect/{MODEL_NAME}/weights/best.pt"
model = YOLO(model_path)

cap = cv2.VideoCapture(VIDEO_INPUT)
if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir el vídeo: {VIDEO_INPUT}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(VIDEO_OUTPUT, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame)
    annotated = results[0].plot()
    out.write(annotated)

cap.release()
out.release()

print(f"✅ Entrenamiento finalizado y vídeo procesado guardado en: {VIDEO_OUTPUT}")
