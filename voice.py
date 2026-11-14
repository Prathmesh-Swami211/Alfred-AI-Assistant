import io
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr


SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio(duration=6):
    """
    Records audio from the computer microphone.
    Returns a WAV file in memory.
    """

    print()
    print("🎙️ LISTENING...")
    print(f"Speak now... ({duration} seconds)")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    print("🎙️ Recording finished.")

    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wav_file:

        wav_file.setnchannels(CHANNELS)

        wav_file.setsampwidth(2)

        wav_file.setframerate(SAMPLE_RATE)

        wav_file.writeframes(
            recording.tobytes()
        )

    wav_buffer.seek(0)

    return wav_buffer


def listen_once(duration=6):

    recognizer = sr.Recognizer()

    wav_buffer = record_audio(duration)

    try:

        with sr.AudioFile(wav_buffer) as source:

            audio = recognizer.record(source)

        print("🧠 Processing speech...")

        text = recognizer.recognize_google(audio)

        print("👤 YOU:", text)

        return text

    except sr.UnknownValueError:

        print("❌ Could not understand the speech.")

        return ""

    except sr.RequestError as error:

        print("❌ Speech recognition service error:")
        print(error)

        return ""

    except Exception as error:

        print("❌ Microphone error:")
        print(error)

        return ""


def test_microphone():

    print()
    print("=" * 50)
    print("MICROPHONE TEST")
    print("=" * 50)

    try:

        devices = sd.query_devices()

        print(devices)

        print()
        print("Default input device:")
        print(sd.query_devices(kind="input"))

        print()
        print("Microphone system is available.")

        return True

    except Exception as error:

        print()
        print("❌ MICROPHONE ERROR")
        print(error)

        return False