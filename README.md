# Alfred — AI Desktop Assistant

An AI-powered desktop assistant built with Python, designed to make everyday computer interactions easier through voice and text.

## Features

- **AI conversations:** Interact with AI using Gemini and Groq.
- **Voice input:** Speak to Alfred using your microphone.
- **Voice responses:** Alfred can respond using text-to-speech.
- **Desktop control:** Open supported applications, websites, and folders.
- **Web search:** Search the web for information.
- **Modern interface:** A dedicated frontend for interacting with Alfred.
- **Local server:** Runs through a local Flask server.

## Project Structure

```text
Alfred/
│
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── main.py
├── server.py
├── voice.py
├── system_control.py
├── pc_monitor.py
├── test_system_control.py
│
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```

*The frontend filenames above are illustrative; adjust them to match your actual files.*

## Requirements

- Windows 10 or Windows 11
- Python 3
- Git
- Microphone (for voice input)
- Internet connection
- API key for your chosen AI provider

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Prathmesh-Swami211/Alfred-AI-Assistant.git
```

### 2. Enter the project directory

```bash
cd Alfred-AI-Assistant
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Install dependencies

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Configure API keys

Create a `.env` file in the project directory.

Add your own API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Never publish your actual API keys.

### 6. Run Alfred

Use the project's configured startup command or run:

```bash
python server.py
```

Open the local address displayed by the server in your browser.

## Security and Privacy

- API keys should remain in your local `.env` file.
- Never commit passwords, tokens, or private credentials.
- Computer-control features should use restricted, predefined actions.
- Review commands before allowing operations that modify or delete files.
- Voice recognition and AI providers may process data through external services. Avoid speaking or submitting sensitive information.

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Google Gemini API
- Groq API
- SpeechRecognition
- SoundDevice
- pyttsx3

## Project Status

Alfred is an ongoing personal project. New features, improvements, and interface updates are being developed.

## Author

**Prathmesh Swami**

GitHub: [@Prathmesh-Swami211](https://github.com/Prathmesh-Swami211)

---

*Built with curiosity, Python, and a vision to create a smarter desktop assistant.*