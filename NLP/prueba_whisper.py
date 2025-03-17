import whisper
import pandas as pd

# Cargar modelo de Whisper (elige "tiny", "base", "small", "medium" o "large")
model = whisper.load_model("small")  # Puedes cambiar el tamaño del modelo


# Ruta del archivo de audio (modifica con tu archivo)
audio_path = "audio_test_2.mp3"  # Puede ser .mp3, .wav, .m4a, .ogg, etc.

# Transcribir el audio
result = model.transcribe(audio_path)

# Extraer el texto transcrito
transcription = result["text"]

# Guardar en un CSV
df = pd.DataFrame({"Texto": [transcription]})
df.to_csv("transcripcion.csv", index=False)

# Imprimir la transcripción
print("Transcripción completada y guardada en 'transcripcion.csv':")
print(transcription)
