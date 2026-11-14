import os
import time
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from google import genai

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY was not found in .env")

# =========================
# ALFRED AI
# =========================

client = genai.Client()

# =========================
# VOICE OUTPUT
# =========================

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

# =========================
# SPEECH RECOGNITION
# =========================

recognizer = sr.Recognizer()

SAMPLE_RATE = 16000
RECORD_SECONDS = 5


def speak(text):
    print("\nALFRED:", text)

    engine.say(text)
    engine.runAndWait()


def listen():
    print("\n🎤 Listening...")

    try:

        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio = sr.AudioData(
            recording.tobytes(),
            SAMPLE_RATE,
            2
        )

        print("🔎 Understanding...")

        text = recognizer.recognize_google(audio)

        return text

    except sr.UnknownValueError:

        return ""

    except sr.RequestError as e:

        print("Speech recognition error:", e)
        return ""

    except Exception as e:

        print("Microphone error:", e)
        return ""


def ask_alfred(user_text):

    for attempt in range(3):

        try:

            interaction = client.interactions.create(
                model="gemini-3.8-flash",

                input=f"""
You are Alfred, a helpful personal AI assistant.

You are running on the user's Windows computer.

Rules:
- Be intelligent and helpful.
- Keep normal answers concise.
- Speak naturally.
- Do not say that you are a chatbot.
- Your name is Alfred.

User:
{user_text}
"""
            )

            return interaction.output_text

        except Exception as e:

            if "503" in str(e) and attempt < 2:

                print("Gemini is temporarily busy. Retrying...")
                time.sleep(3)

            else:

                print("Gemini error:", e)
                return "I'm having trouble connecting to my AI system."

    return "I couldn't process that request."


# =========================
# START ALFRED
# =========================

print("================================")
print("        ALFRED IS ONLINE")
print("================================")
print()
print("🎤 Alfred is listening continuously.")
print("Press CTRL+C to stop.")
print()

speak("Alfred is online. How may I help you?")

while True:

    try:

        user = listen()

        if not user:
            continue

        print("YOU:", user)

        answer = ask_alfred(user)

        speak(answer)

        print("\n🎤 Waiting for your next command...")

    except KeyboardInterrupt:

        print("\n\nAlfred shutting down.")
        speak("Goodbye.")
        break

    except Exception as e:

        print("System error:", e)
        time.sleep(1)