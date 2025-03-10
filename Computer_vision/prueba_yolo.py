import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Ruta a los datos
dataset_path = 'archive/traffic_Data/DATA'

# Cargar modelo YOLO preentrenado (puedes entrenar el tuyo con los datos)
yolo_model = YOLO('yolov8n.pt')  # O entrena el tuyo y pon el path al modelo entrenado

# Cargar modelo de clasificación de señales de tráfico (asume que ya está entrenado)
classifier_model_path = "traffic_classifier.h5"  # Cambia a tu modelo entrenado
classifier = load_model(classifier_model_path)

# Lista de clases del dataset
classes = sorted(os.listdir(dataset_path))  # Extrae las clases de las carpetas

# Función para preprocesar la imagen para la clasificación
def preprocess_for_classification(image, size=(32, 32)):
    image = cv2.resize(image, size)
    image = image.astype("float32") / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# Función para detectar y clasificar señales en una imagen
def detect_and_classify(image_path):
    image = cv2.imread(image_path)
    results = yolo_model(image)[0]  # Detectar objetos con YOLO
    
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = box.conf[0].item()
        
        if confidence > 0.5:  # Umbral de confianza
            cropped_img = image[y1:y2, x1:x2]
            processed_img = preprocess_for_classification(cropped_img)
            
            prediction = classifier.predict(processed_img)
            class_index = np.argmax(prediction)
            class_name = classes[class_index]
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{class_name} ({confidence:.2f})", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()

# Prueba con una imagen de ejemplo
detect_and_classify("prueba.jpeg")
