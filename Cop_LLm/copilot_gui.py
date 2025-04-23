import tkinter as tk
from tkinter import scrolledtext
import requests
import subprocess
import time
import threading

OLLAMA_MODEL_NAME = "copilot-llm"

conversation_state = {
    "step": 0,
    "car_model": None,
    "tire_condition": None,
    "tire_pressure": None,
    "season": None,
    "weather": None,
    "road_type": None
}

questions = [
    "What is your car's make and model?",
    "What is the current condition of your tires?",
    "What is the current tire pressure?",
    "What season are we currently in?",
    "What is the weather like today?",
    "What kind of road will you drive on, and how long is the trip?"
]

field_keys = [
    "car_model",
    "tire_condition",
    "tire_pressure",
    "season",
    "weather",
    "road_type"
]

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

    step = conversation_state["step"]
    if step < len(field_keys):
        conversation_state[field_keys[step]] = user_input
        conversation_state["step"] += 1
        ask_next_question()
    else:
        threading.Thread(target=send_summary_to_model, daemon=True).start()

def update_chat(sender, text):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"{sender}:\n{text}\n\n")
    chat_area.config(state="disabled")
    chat_area.yview(tk.END)

def ask_next_question():
    step = conversation_state["step"]
    if step < len(questions):
        update_chat("Copilot", questions[step])
    else:
        update_chat("Copilot", "Thanks! Let me analyze your info and give you a summary.")
        threading.Thread(target=send_summary_to_model, daemon=True).start()

def send_summary_to_model():
    summary = (
        f"The user is driving a {conversation_state['car_model']}. "
        f"The tires are in '{conversation_state['tire_condition']}' condition with a pressure of {conversation_state['tire_pressure']}. "
        f"The season is {conversation_state['season']} and the weather is {conversation_state['weather']}. "
        f"The trip will be on {conversation_state['road_type']}. "
        "Based on this, give your final advice."
    )
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": summary, "stream": False}
        )
        reply = response.json().get("response", "").strip()
        root.after(0, update_chat, "Copilot", reply)
    except Exception as e:
        root.after(0, update_chat, "Error", str(e))

def initial_message():
    update_chat("Copilot", "Hello! I’ll ask you a few questions to help prepare your trip safely. Are you ready?")

# Inicia el modelo si no está activo
start_model_if_not_running()

# Crear la ventana principal
root = tk.Tk()
root.title("🚗 Copilot LLM (Guided Mode)")
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

# Lanzar mensaje inicial
threading.Thread(target=initial_message, daemon=True).start()

# Lanzar interfaz
root.mainloop()
