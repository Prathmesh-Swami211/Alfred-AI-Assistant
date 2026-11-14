import os
import threading
import time
import webbrowser

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

from google import genai
from groq import Groq

from voice import listen_once
from system_control import execute_system_command


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# GEMINI
# ============================================================

gemini_client = None

if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )
    except Exception as error:
        print("Gemini initialization error:")
        print(error)


# ============================================================
# GROQ
# ============================================================

groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(
            api_key=GROQ_API_KEY
        )
    except Exception as error:
        print("Groq initialization error:")
        print(error)


# ============================================================
# TTS
# ============================================================

tts_lock = threading.Lock()
tts_engine = None
tts_thread = None
tts_stop_event = threading.Event()


def stop_speaking():

    global tts_engine

    tts_stop_event.set()

    with tts_lock:

        if tts_engine is not None:

            try:
                tts_engine.stop()

            except Exception:
                pass


def speak(text):

    global tts_engine

    tts_stop_event.clear()

    engine = None

    try:

        import pyttsx3

        engine = pyttsx3.init()

        with tts_lock:
            tts_engine = engine

        engine.setProperty(
            "rate",
            175
        )

        engine.setProperty(
            "volume",
            1.0
        )

        engine.say(
            str(text)
        )

        engine.runAndWait()

    except Exception as error:

        print("TTS error:")
        print(error)

    finally:

        try:

            if engine is not None:
                engine.stop()

        except Exception:
            pass

        with tts_lock:

            if tts_engine is engine:
                tts_engine = None

        tts_stop_event.clear()


def speak_async(text):

    global tts_thread

    stop_speaking()

    tts_thread = threading.Thread(
        target=speak,
        args=(text,),
        daemon=True
    )

    tts_thread.start()


# ============================================================
# GEMINI AI
# ============================================================

def ask_gemini(prompt):

    if gemini_client is None:
        raise RuntimeError(
            "Gemini API is not configured."
        )

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text.strip()


# ============================================================
# GROQ AI
# ============================================================

def ask_groq(prompt):

    if groq_client is None:
        raise RuntimeError(
            "Groq API is not configured."
        )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()


# ============================================================
# AI ROUTER
# ============================================================

def ask_ai(user_message):

    prompt = f"""
You are Alfred, a futuristic personal AI assistant.

Answer the user's request clearly, naturally and helpfully.

User:
{user_message}
"""

    # --------------------------------------------------------
    # GEMINI PRIMARY
    # --------------------------------------------------------

    try:

        answer = ask_gemini(prompt)

        return {
            "answer": answer,
            "provider": "GEMINI"
        }

    except Exception as gemini_error:

        print()
        print("Gemini failed:")
        print(gemini_error)

    # --------------------------------------------------------
    # GROQ FALLBACK
    # --------------------------------------------------------

    try:

        answer = ask_groq(prompt)

        return {
            "answer": answer,
            "provider": "GROQ"
        }

    except Exception as groq_error:

        print()
        print("Groq failed:")
        print(groq_error)

    # --------------------------------------------------------
    # OFFLINE FALLBACK
    # --------------------------------------------------------

    return {
        "answer": (
            "I'm sorry, but both my AI systems are "
            "currently unavailable."
        ),
        "provider": "OFFLINE"
    }


# ============================================================
# SYSTEM COMMAND DETECTOR
# ============================================================

def detect_system_command(user_message):

    prompt = f"""
You are Alfred's computer command classifier.

Your ONLY job is to determine whether the user wants Alfred
to open an application, website, folder, or the Alfred project.

Return EXACTLY ONE command from this list:

OPEN_CALCULATOR
OPEN_NOTEPAD
OPEN_PAINT
OPEN_EXPLORER
OPEN_VSCODE
OPEN_YOUTUBE
OPEN_GOOGLE
OPEN_GMAIL
OPEN_GITHUB
OPEN_PW
OPEN_DOCUMENTS
OPEN_DOWNLOADS
OPEN_DESKTOP
OPEN_PICTURES
OPEN_VIDEOS
OPEN_MUSIC
OPEN_ALFRED_PROJECT
NONE

APPLICATION COMMANDS

"open calculator"
"launch calculator"
"start calculator"
=> OPEN_CALCULATOR

"open notepad"
"launch notepad"
"start notepad"
=> OPEN_NOTEPAD

"open paint"
"launch paint"
"start paint"
=> OPEN_PAINT

"open file explorer"
"open explorer"
"launch file explorer"
=> OPEN_EXPLORER

"open vscode"
"open vs code"
"launch vscode"
=> OPEN_VSCODE

WEBSITES

"open youtube"
"launch youtube"
"go to youtube"
=> OPEN_YOUTUBE

"open google"
"launch google"
"go to google"
=> OPEN_GOOGLE

"open gmail"
"launch gmail"
"go to gmail"
=> OPEN_GMAIL

"open github"
"launch github"
"go to github"
=> OPEN_GITHUB


FOLDERS

"open documents"
"open my documents"
"open the documents folder"
=> OPEN_DOCUMENTS

"open downloads"
"open my downloads"
"open the downloads folder"
=> OPEN_DOWNLOADS

"open desktop"
"open my desktop"
"open the desktop folder"
=> OPEN_DESKTOP

"open pictures"
"open my pictures"
"open the pictures folder"
=> OPEN_PICTURES

"open videos"
"open my videos"
"open the videos folder"
=> OPEN_VIDEOS

"open music"
"open my music"
"open the music folder"
=> OPEN_MUSIC

ALFRED PROJECT

"open alfred"
"open alfred project"
"open my alfred project"
"open alfred folder"
=> OPEN_ALFRED_PROJECT

If the user is NOT asking Alfred to open or launch
something, return:

NONE

User message:
{user_message}
"""

    allowed_commands = {
        "OPEN_CALCULATOR",
        "OPEN_NOTEPAD",
        "OPEN_PAINT",
        "OPEN_EXPLORER",
        "OPEN_VSCODE",
        "OPEN_YOUTUBE",
        "OPEN_GOOGLE",
        "OPEN_GMAIL",
        "OPEN_GITHUB",
        "OPEN_DOCUMENTS",
        "OPEN_DOWNLOADS",
        "OPEN_DESKTOP",
        "OPEN_PICTURES",
        "OPEN_VIDEOS",
        "OPEN_MUSIC",
        "OPEN_ALFRED_PROJECT",
        "NONE"
    }

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        result = ask_gemini(prompt)

        command = result.strip().upper()

        if command in allowed_commands:
            return command

    except Exception as error:

        print()
        print("Gemini command detection failed:")
        print(error)

    # --------------------------------------------------------
    # GROQ
    # --------------------------------------------------------

    try:

        result = ask_groq(prompt)

        command = result.strip().upper()

        if command in allowed_commands:
            return command

    except Exception as error:

        print()
        print("Groq command detection failed:")
        print(error)

    return "NONE"


# ============================================================
# COMMAND MAP
# ============================================================

COMMAND_MAP = {

    "OPEN_CALCULATOR":
        "open calculator",

    "OPEN_NOTEPAD":
        "open notepad",

    "OPEN_PAINT":
        "open paint",

    "OPEN_EXPLORER":
        "open file explorer",

    "OPEN_VSCODE":
        "open vscode",

    "OPEN_YOUTUBE":
        "open youtube",

    "OPEN_GOOGLE":
        "open google",

    "OPEN_GMAIL":
        "open gmail",

    "OPEN_GITHUB":
        "open github",

    "OPEN_DOCUMENTS":
        "open documents",

    "OPEN_DOWNLOADS":
        "open downloads",

    "OPEN_DESKTOP":
        "open desktop",

    "OPEN_PICTURES":
        "open pictures",

    "OPEN_VIDEOS":
        "open videos",

    "OPEN_MUSIC":
        "open music",

    "OPEN_ALFRED_PROJECT":
        "open alfred project"
}


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(user_message):

    user_message = user_message.strip()

    if not user_message:

        return {
            "answer": "I didn't hear anything.",
            "provider": "SYSTEM"
        }

    # --------------------------------------------------------
    # SYSTEM COMMAND
    # --------------------------------------------------------

    system_command = detect_system_command(
        user_message
    )

    print()
    print("Detected command:", system_command)

    # --------------------------------------------------------
    # EXECUTE SYSTEM COMMAND
    # --------------------------------------------------------

    if system_command != "NONE":

        command = COMMAND_MAP.get(
            system_command
        )

        if command:

            success, message = execute_system_command(
                command
            )

            if success:

                speak_async(message)

                return {
                    "answer": message,
                    "provider": "SYSTEM CONTROL",
                    "command": system_command
                }

            return {
                "answer": message,
                "provider": "SYSTEM CONTROL",
                "command": system_command
            }

    # --------------------------------------------------------
    # NORMAL AI
    # --------------------------------------------------------

    result = ask_ai(
        user_message
    )

    speak_async(
        result["answer"]
    )

    return result


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        "frontend",
        "index.html"
    )


# ============================================================
# CSS
# ============================================================

@app.route("/style.css")
def style():

    return send_from_directory(
        "frontend",
        "style.css"
    )


# ============================================================
# JAVASCRIPT
# ============================================================

@app.route("/script.js")
def script():

    return send_from_directory(
        "frontend",
        "script.js"
    )


# ============================================================
# CHAT API
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    stop_speaking()

    try:

        data = request.get_json(
            silent=True
        ) or {}

        message = data.get(
            "message",
            ""
        )

        result = process_message(
            message
        )

        return jsonify(result)

    except Exception as error:

        print()
        print("CHAT ERROR:")
        print(error)

        return jsonify({
            "answer":
                "An error occurred while processing your request.",
            "provider":
                "ERROR"
        }), 500


# ============================================================
# VOICE API
# ============================================================

@app.route(
    "/api/voice",
    methods=["POST"]
)
def voice():

    stop_speaking()

    try:

        text = listen_once(
            duration=6
        )

        if not text:

            return jsonify({
                "answer":
                    "I couldn't understand you.",
                "provider":
                    "VOICE"
            })

        result = process_message(
            text
        )

        result["transcript"] = text

        return jsonify(result)

    except Exception as error:

        print()
        print("VOICE ERROR:")
        print(error)

        return jsonify({
            "answer":
                "There was a problem with voice recognition.",
            "provider":
                "VOICE ERROR"
        }), 500


# ============================================================
# STOP SPEAKING
# ============================================================

@app.route(
    "/api/stop",
    methods=["POST"]
)
def stop():

    stop_speaking()

    return jsonify({
        "status":
            "stopped"
    })


# ============================================================
# SYSTEM MONITOR
# ============================================================

@app.route(
    "/api/system",
    methods=["GET"]
)
def system():

    try:

        from pc_monitor import get_system_stats

        stats = get_system_stats()

        return jsonify(stats)

    except Exception as error:

        print()
        print("SYSTEM MONITOR ERROR:")
        print(error)

        return jsonify({
            "error":
                str(error)
        }), 500


# ============================================================
# OPEN BROWSER
# ============================================================

def open_alfred_browser():

    time.sleep(2)

    try:

        webbrowser.open_new_tab(
            "http://127.0.0.1:5000"
        )

    except Exception as error:

        print("Browser error:")
        print(error)


# ============================================================
# START ALFRED
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # OPEN BROWSER IN BACKGROUND
    # --------------------------------------------------------

    browser_thread = threading.Thread(
        target=open_alfred_browser,
        daemon=True
    )

    browser_thread.start()

    # --------------------------------------------------------
    # START FLASK
    # --------------------------------------------------------

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )