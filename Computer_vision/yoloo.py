import os
import random
import shutil
from pathlib import Path
import cv2
import yaml
from tqdm import tqdm

# Rutas del dataset
DATASET_PATH = "archive/traffic_Data/DATA"
OUTPUT_PATH = "dataset_yolo"
TRAIN_RATIO = 0.8  # 80% para entrenamiento, 20% para validación

# Crear carpetas de salida
for folder in ["train", "val"]:
    for sub in ["images", "labels"]:
        Path(f"{OUTPUT_PATH}/{folder}/{sub}").mkdir(parents=True, exist_ok=True)

# Obtener clases
classes = sorted([d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))])
with open(f"{OUTPUT_PATH}/classes.txt", "w") as f:
    f.write("\n".join(classes))

# Generar etiquetas en formato YOLO
def convert_to_yolo(image_path, class_id, output_label_path):
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    x_center, y_center, width, height = 0.5, 0.5, 1.0, 1.0  # Suponer bounding box completo
    
    with open(output_label_path, "w") as f:
        f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

# Convertir dataset
all_files = []
for class_id, class_name in enumerate(classes):
    class_path = os.path.join(DATASET_PATH, class_name)
    images = [os.path.join(class_path, img) for img in os.listdir(class_path) if img.endswith(".png") or img.endswith(".jpg")]
    all_files.extend([(img, class_id) for img in images])

random.shuffle(all_files)
split_idx = int(len(all_files) * TRAIN_RATIO)
train_files = all_files[:split_idx]
val_files = all_files[split_idx:]

def process_files(file_list, folder):
    for img_path, class_id in tqdm(file_list, desc=f"Processing {folder}"):
        img_name = os.path.basename(img_path)
        img_dest = f"{OUTPUT_PATH}/{folder}/images/{img_name}"
        label_dest = f"{OUTPUT_PATH}/{folder}/labels/{img_name.replace('.jpg', '.txt').replace('.png', '.txt')}"
        
        shutil.copy(img_path, img_dest)
        convert_to_yolo(img_path, class_id, label_dest)

process_files(train_files, "train")
process_files(val_files, "val")

# Crear archivo de configuración YOLO
yaml_data = {
    "train": f"{OUTPUT_PATH}/train/images",
    "val": f"{OUTPUT_PATH}/val/images",
    "nc": len(classes),
    "names": classes
}

with open(f"{OUTPUT_PATH}/data.yaml", "w") as f:
    yaml.dump(yaml_data, f)

print("✅ Dataset convertido a formato YOLO correctamente.")
