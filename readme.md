# 🚘 Autonomous Driving Assistant

A modular, privacy-preserving intelligent assistant for autonomous driving — combining speech recognition, natural language processing, route optimization, and real-time object detection.

## 🧠 Overview

This project integrates state-of-the-art AI technologies into a unified system to enhance autonomous driving assistance through:

- 🔊 **Conversational Interaction**: A locally-deployed Large Language Model (LLM) provides real-time recommendations based on vehicle and environment conditions.
- 🗺️ **Speech-Based Route Planning**: Transcribes spoken origin/destination, extracts cities using Named Entity Recognition (NER), corrects with Levenshtein distance, and computes routes using Greedy Best-First Search.
- 🧍‍♂️ **Visual Perception**: Real-time object detection using YOLOv8 models for pedestrians and traffic signs.

All components run **fully locally**, ensuring privacy and autonomy.

---

## ⚙️ Technologies Used

| Module                    | Technology                                                                 |
|--------------------------|----------------------------------------------------------------------------|
| Speech Recognition       | [OpenAI Whisper](https://github.com/openai/whisper)                        |
| Named Entity Recognition | [Hugging Face Transformers (Roberta NER)](https://huggingface.co/AventIQ-AI/roberta-named-entity-recognition) |
| String Matching          | Levenshtein Distance (fuzzy matching)                                      |
| Route Planning           | Greedy Best-First Search on a custom city graph                            |
| Object Detection         | [YOLOv8](https://github.com/ultralytics/ultralytics) via Roboflow datasets |
| LLM Assistant            | [Mistral](https://mistral.ai) deployed locally                             |
| Interface (optional)     | [Streamlit](https://streamlit.io/)                                         |

---