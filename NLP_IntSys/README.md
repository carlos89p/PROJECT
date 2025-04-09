# 🧭 Extracción Automática de Ciudades en Texto con NER

Este proyecto detecta automáticamente ciudades mencionadas en textos o transcripciones de voz y las clasifica como `inicio` y `destino`, utilizando modelos de reconocimiento de entidades nombradas (NER) de Hugging Face.

---

## ⚙️ Tecnologías y librerías

- **Python 3**
- **Transformers**: Librería de Hugging Face utilizada para cargar modelos preentrenados de PLN.
- **PyTorch**: Backend utilizado para la ejecución del modelo.
- **Modelo NER**: [`AventIQ-AI/roberta-named-entity-recognition`](https://huggingface.co/AventIQ-AI/roberta-named-entity-recognition), entrenado para identificar entidades como ubicaciones (`LOC`), personas (`PER`) u organizaciones (`ORG`).

Opcionalmente:
- **Whisper**: Puede usarse para transcribir archivos de audio a texto, sobre el cual luego se aplica NER.

---

## 🚀 ¿Cómo funciona?

1. Se toma como entrada un texto libre o una transcripción.
2. El modelo NER identifica automáticamente entidades de tipo `LOC` (ubicaciones).
3. Según cuántas ciudades se detecten:
   - Si hay **una sola ciudad**, se asigna a la variable `destino`.
   - Si hay **dos o más**, se asignan a `inicio` y `destino` respectivamente (en orden de aparición).
4. Las entidades extraídas se pueden mostrar o guardar para procesamiento posterior.

---

## 📁 Estructura actual del proyecto

- `notebook_final.ipynb`: Contiene la implementación actual del reconocimiento de entidades y extracción de ciudades desde texto.
- `whisper_token.ipynb`: Incluye un ejemplo de transcripción con Whisper (si se integra audio).
  
---

## 📦 Instalación

Instala las dependencias necesarias:

```bash
pip install transformers torch

---

## 🧪 Ejemplo de uso

Este proyecto se encuentra implementado en un entorno tipo Jupyter Notebook. Una vez cargado el modelo, puedes pasarle cualquier texto libre y el sistema extraerá las ciudades mencionadas. A partir del número de ciudades detectadas, se asignan a las variables `inicio` y `destino`.

---

## ✅ Funcionalidades actuales

- Detección automática de entidades de tipo ubicación (`LOC`) sin necesidad de listas predefinidas.
- Clasificación automática de ciudades en variables `inicio` y `destino`.
- Preparado para integrarse con Whisper y procesar transcripciones desde audio.
- Compatible con texto libre en lenguaje natural.

---
