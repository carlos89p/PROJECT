import tkinter as tk
from tkinter import scrolledtext
import requests
import subprocess
import time
import threading

OLLAMA_MODEL_NAME = "copilot-llm"

def start_model_if_not_running():
    try:
        requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": "ping", "stream": False},
            timeout=2
        )
        return
    except:
        pass

    subprocess.Popen(
        ["ollama", "run", OLLAMA_MODEL_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)

def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return
    update_chat("You", user_input)
    entry.delete(0, tk.END)
    threading.Thread(target=get_response_from_model, args=(user_input,), daemon=True).start()

def update_chat(sender, text):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"{sender}:\n{text}\n\n")
    chat_area.config(state="disabled")
    chat_area.yview(tk.END)

def get_response_from_model(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": prompt, "stream": False}
        )
        reply = response.json().get("response", "").strip()
        root.after(0, update_chat, "Copilot", reply)
    except Exception as e:
        root.after(0, update_chat, "Error", str(e))

def initial_message():
    # Aquí empieza la conversación de verdad, no la descripción
    get_response_from_model(
        "Hello! I'm ready to help a user prepare their trip. Let's begin the full assistant conversation as instructed, step by step, starting with the welcome and asking if the user is ready."
    )

# Inicia el modelo si no está activo
start_model_if_not_running()

# Crear la ventana principal
root = tk.Tk()
root.title("🚗 Copilot LLM")
root.geometry("800x600")
root.configure(bg="#f5f5f5")

# Área de chat
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 14), bg="white", fg="black")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.config(state="disabled")

# Zona de entrada
input_frame = tk.Frame(root, bg="#f5f5f5")
input_frame.pack(fill=tk.X, padx=10, pady=10)

entry = tk.Entry(input_frame, font=("Helvetica", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
entry.bind("<Return>", lambda e: send_message())

send_button = tk.Button(input_frame, text="Send", font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white", command=send_message)
send_button.pack(side=tk.RIGHT, ipadx=10, ipady=4)

# Lanzar primer mensaje del modelo en un hilo
threading.Thread(target=initial_message, daemon=True).start()

# Lanzar interfaz
root.mainloop()
