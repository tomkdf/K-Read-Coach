from faster_whisper import WhisperModel
import streamlit as st

# On charge le modèle une seule fois (cache)
@st.cache_resource
def get_model():
    # "small" est rapide, "int8" réduit la consommation de mémoire
    return WhisperModel("small", device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    if not audio_path:
        return ""
    
    model = get_model()
    # Transcription forcée en coréen
    segments, _ = model.transcribe(audio_path, language="ko")
    # On rassemble les morceaux de texte
    return "".join([s.text for s in segments]).strip()