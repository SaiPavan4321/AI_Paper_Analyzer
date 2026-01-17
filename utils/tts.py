import pyttsx3
import tempfile
import os

def speak_output(username, module_name, content):
    if not content:
        return None

    # Convert dict/list output to readable text
    if isinstance(content, dict):
        content = " ".join(str(v) for v in content.values())
    elif isinstance(content, list):
        content = " ".join(map(str, content))
    else:
        content = str(content)

    # Text to speak
    speech_text = (
        f"Hello {username}. "
        f"This is the {module_name} output. "
        f"{content}. "
        f"Thank you."
    )

    engine = pyttsx3.init()

    # ---------------- VOICE SELECTION ----------------
    voices = engine.getProperty("voices")

    female_voice = None
    for voice in voices:
        voice_name = voice.name.lower()
        voice_id = voice.id.lower()

        if (
            "female" in voice_name
            or "woman" in voice_name
            or "zira" in voice_name     # Windows female voice
            or "susan" in voice_name
        ):
            female_voice = voice.id
            break

    # Fallback (if no female found)
    if female_voice:
        engine.setProperty("voice", female_voice)
    else:
        engine.setProperty("voice", voices[0].id)

    # ---------------- VOICE TUNING ----------------
    engine.setProperty("rate", 180)     # ~1.2x speed (default ~150)
    engine.setProperty("volume", 1.0)

    # ---------------- SAVE AUDIO ----------------
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_path = tmp_file.name
    tmp_file.close()

    engine.save_to_file(speech_text, audio_path)
    engine.runAndWait()
    engine.stop()

    return audio_path
