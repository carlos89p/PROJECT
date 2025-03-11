import tensorflow as tf
import numpy as np
import cv2
import os
import argparse
import matplotlib.pyplot as plt

# Ruta del modelo entrenado y dataset
MODEL_PATH = "traffic_classifier.h5"
DATASET_PATH = "archive/traffic_Data/DATA"
IMG_SIZE = (64, 64)
OUTPUT_IMAGE_PATH = "classified_image.jpg"

# Cargar el modelo
model = tf.keras.models.load_model(MODEL_PATH)

# Obtener clases
data_gen = tf.keras.preprocessing.image.ImageDataGenerator()
train_data = data_gen.flow_from_directory(DATASET_PATH, target_size=IMG_SIZE, batch_size=1)
classes = list(train_data.class_indices.keys())
print("Clases detectadas:", classes)

# Función para preprocesar la imagen
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, IMG_SIZE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
    image = image.astype("float32") / 255.0  # Normalización
    image = np.expand_dims(image, axis=0)  # Añadir dimensión de lote
    return image

# Clasificar imagen y etiquetar resultado
def classify(image_path, output_path=OUTPUT_IMAGE_PATH):
    image = preprocess_image(image_path)
    prediction = model.predict(image)
    class_index = np.argmax(prediction)
    class_name = classes[class_index]
    confidence = prediction[0][class_index]
    print(f"Predicción: {class_name} ({confidence:.2f})")
    
    # Cargar imagen original
    original_image = cv2.imread(image_path)
    height, width, _ = original_image.shape
    
    # Dibujar etiqueta sobre la imagen
    label = f"{class_name} ({confidence:.2f})"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(width, height) / 500  # Ajustar tamaño del texto
    thickness = 2
    text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    text_x, text_y = 10, text_size[1] + 10  # Posición superior izquierda
    
    # Dibujar fondo para la etiqueta
    cv2.rectangle(original_image, (text_x - 5, text_y - text_size[1] - 5),
                  (text_x + text_size[0] + 5, text_y + 5), (0, 255, 0), -1)
    
    # Dibujar el texto
    cv2.putText(original_image, label, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)
    
    # Guardar y mostrar imagen
    cv2.imwrite(output_path, original_image)
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clasificar una imagen de tráfico usando el modelo entrenado y etiquetarla.")
    parser.add_argument("image_path", type=str, help="Ruta de la imagen a clasificar")
    args = parser.parse_args()
    classify(args.image_path)