import os
import json
import shutil
from PIL import Image
from tqdm import tqdm

# === RUTAS DE TU DATASET ORIGINAL ===
json_path = "archive/train_dataset/train.json"
images_src_dir = "archive/train_dataset/train_images"

# === NUEVA ESTRUCTURA DE YOLOv8 ===
output_base = "yolo_dataset"
img_out_dir = os.path.join(output_base, "images", "train")
lbl_out_dir = os.path.join(output_base, "labels", "train")

os.makedirs(img_out_dir, exist_ok=True)
os.makedirs(lbl_out_dir, exist_ok=True)

# === CLASES (se usarán como índices en YOLO) ===
classes = {"red": 0, "yellow": 1, "green": 2}

# === PROCESAR EL JSON Y CREAR ANOTACIONES ===
with open(json_path, "r") as f:
    data = json.load(f)

generadas = 0
saltadas = 0

for ann in tqdm(data["annotations"], desc="Procesando anotaciones"):
    filename = ann["filename"].replace("\\", "/").split("/")[-1]
    src_img_path = os.path.join(images_src_dir, filename)
    dst_img_path = os.path.join(img_out_dir, filename)
    label_txt_path = os.path.join(lbl_out_dir, filename.replace(".jpg", ".txt"))

    if not os.path.exists(src_img_path):
        saltadas += 1
        continue

    try:
        img = Image.open(src_img_path)
        width, height = img.size
        yolo_lines = []

        if "inbox" not in ann or len(ann["inbox"]) == 0:
            continue

        for item in ann["inbox"]:
            color = item["color"]
            if color not in classes:
                continue
            bbox = item["bndbox"]
            xmin, ymin, xmax, ymax = bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]

            # Normalizar coordenadas
            x_center = ((xmin + xmax) / 2) / width
            y_center = ((ymin + ymax) / 2) / height
            box_width = (xmax - xmin) / width
            box_height = (ymax - ymin) / height

            yolo_lines.append(f"{classes[color]} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")

        if yolo_lines:
            shutil.copyfile(src_img_path, dst_img_path)
            with open(label_txt_path, "w") as f:
                f.write("\n".join(yolo_lines))
            generadas += 1
    except Exception as e:
        print(f"[ERROR] {filename}: {e}")
        saltadas += 1

# === RESUMEN ===
print(f"\n✅ Anotaciones YOLO generadas: {generadas}")
print(f"❌ Imágenes saltadas: {saltadas}")
print(f"[INFO] Dataset guardado en: {output_base}")
