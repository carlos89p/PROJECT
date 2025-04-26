import streamlit as st
import requests
import subprocess
import time

# streamlit run copilot_streamlit.py

# Configuración inicial
OLLAMA_MODEL_NAME = "copilot-llm"

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

# Estado inicial usando Streamlit
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

# Función para iniciar el modelo si no está corriendo
def start_model_if_not_running():
    try:
        requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": "ping", "stream": False},
            timeout=2
        )
    except:
        subprocess.Popen(
            ["ollama", "run", OLLAMA_MODEL_NAME],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

# Función para enviar mensaje al modelo
def send_summary_to_model():
    summary = f"""
    You are an expert driving assistant specialized in preparing cars and drivers for trips.
    Analyze the following information about the user carefully:

    - Car model: {st.session_state.answers.get('car_model')}
    - Tire condition: {st.session_state.answers.get('tire_condition')}
    - Tire pressure: {st.session_state.answers.get('tire_pressure')}
    - Season: {st.session_state.answers.get('season')}
    - Weather: {st.session_state.answers.get('weather')}
    - Road type and trip length: {st.session_state.answers.get('road_type')}

    Your tasks:
    1. Detect if there are any potential risks (bad tires, low/high pressure, bad weather, etc.).
    2. Give clear, actionable advice to prepare the car and the driver.
    3. If everything looks good, congratulate and still give at least 2 safety tips.
    4. Keep the answer friendly but concise (max 200 words).

    Start your advice directly without repeating the input information.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL_NAME, "prompt": summary, "stream": False}
        )
        reply = response.json().get("response", "").strip()
        st.session_state.conversation.append(("Copilot", reply))
    except Exception as e:
        st.session_state.conversation.append(("Error", str(e)))


# Función para manejar envío de input
def handle_input(user_input):
    if not user_input.strip():
        return

    st.session_state.conversation.append(("You", user_input))
    
    step = st.session_state.step

    # 👇 Si es la primera vez, simplemente iniciar el cuestionario
    if step == 0 and len(st.session_state.answers) == 0:
        # No guardar este "hi" como respuesta de coche, solo usarlo como "ready"
        st.session_state.conversation.append(("Copilot", questions[0]))
        st.session_state.answers["ready"] = user_input  # Guardar ready opcionalmente
    else:
        if step < len(field_keys):
            st.session_state.answers[field_keys[step]] = user_input
            st.session_state.step += 1

            if st.session_state.step < len(questions):
                st.session_state.conversation.append(("Copilot", questions[st.session_state.step]))
            else:
                st.session_state.conversation.append(("Copilot", "Thanks! Let me analyze your info and give you a summary."))
                send_summary_to_model()



# Iniciar modelo si no está activo
start_model_if_not_running()

# Título e introducción
st.set_page_config(page_title="🚗 Copilot LLM (Streamlit Version)", page_icon="🚗")
st.title("🚗 Car Copilot LLM")
st.caption("Your personal driving preparation assistant powered by Copilot-LLM. Using a Mistral model.")

# 👇 ATENCIÓN: Agregar el mensaje de bienvenida ANTES de pintar nada
if st.session_state.step == 0 and not st.session_state.conversation:
    st.session_state.conversation.append(("Copilot", "Hello! I’ll ask you a few questions to help prepare your trip safely. Are you ready?"))
    st.rerun()  # 👉 Fuerza recarga para que se vea ya mismo

# Mostrar conversación previa (después de asegurar que el mensaje inicial existe)
for sender, message in st.session_state.conversation:
    if sender == "You":
        st.chat_message("user").markdown(message)
    else:
        st.chat_message("assistant").markdown(message)

# Entrada del usuario
user_message = st.chat_input("Type your message...")

if user_message:
    handle_input(user_message)
    st.rerun()

