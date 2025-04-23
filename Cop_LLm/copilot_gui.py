import tkinter as tk
from tkinter import scrolledtext
import requests
import subprocess
import time

OLLAMA_MODEL_NAME = "copilot-llm"

def start_model_if_not_running():
    try:
        # Probar si responde el endpoint
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": "ping", "stream": False},
            timeout=2
        )
        if response.status_code == 200:
            return  # Ya está funcionando
    except:
        pass

    # Si no está corriendo, arrancamos Ollama
    subprocess.Popen(
        ["ollama", "run", OLLAMA_MODEL_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Le damos unos segundos para arrancar

def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return
    chat_history.insert(tk.END, f"You: {user_input}\n", "user")
    entry.delete(0, tk.END)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL_NAME,
                "prompt": user_input,
                "stream": False
            }
        )
        data = response.json()
        reply = data.get("response", "").strip()
        chat_history.insert(tk.END, f"Copilot: {reply}\n", "bot")
    except Exception as e:
        chat_history.insert(tk.END, f"Error: {str(e)}\n", "error")

    chat_history.yview(tk.END)

# 🟢 Inicializa el modelo si es necesario
start_model_if_not_running()

# GUI Setup
root = tk.Tk()
root.title("🚗 Copilot LLM")
root.geometry("600x500")

chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Helvetica", 12))
chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_history.tag_config("user", foreground="blue")
chat_history.tag_config("bot", foreground="green")
chat_history.tag_config("error", foreground="red")

frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill=tk.X)

entry = tk.Entry(frame, font=("Helvetica", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(frame, text="Send", command=send_message, font=("Helvetica", 12))
send_button.pack(side=tk.RIGHT)

root.mainloop()
