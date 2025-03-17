import whisper
import pandas as pd
import os

# Cargar modelo de Whisper (elige "tiny", "base", "small", "medium" o "large")
model = whisper.load_model("small")  # Puedes cambiar el tamaño del modelo

# Ruta del archivo de audio (modifica con tu archivo)
audio_path = "audio_test_2.mp3"  # Puede ser .mp3, .wav, .m4a, .ogg, etc.

# Transcribir el audio
result = model.transcribe(audio_path)

# Extraer el texto transcrito
transcription = result["text"]

# Definir nombre del archivo CSV
csv_file = "transcripciones.csv"

# Verificar si el archivo existe para escribir encabezados solo si es la primera vez
file_exists = os.path.isfile(csv_file)

# Crear DataFrame con la nueva transcripción
df = pd.DataFrame({"Texto": [transcription]})

# Guardar en el CSV sin sobrescribir datos anteriores (modo 'a' de append)
df.to_csv(csv_file, mode='a', header=not file_exists, index=False, encoding='utf-8')

# Imprimir la transcripción
print("Transcripción agregada a 'transcripciones.csv':")
print(transcription)
