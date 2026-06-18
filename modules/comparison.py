import Levenshtein
import re
from jamo import h2j, j2hcj

def get_jamo_text(text):
    if not text:
        return ""
    # Clean non-alphanumeric characters (spaces, punctuation)
    text = re.sub(r'[^\w]', '', text)
    return j2hcj(h2j(text))

def compare_texts(target: str, recognized: str, audio_duration: float = 1.0) -> dict:
    expected_jamo = get_jamo_text(target)
    obtained_jamo = get_jamo_text(recognized)
    
    dist_jamo = Levenshtein.distance(expected_jamo, obtained_jamo)
    max_len = max(len(expected_jamo), len(obtained_jamo))
    
    if max_len == 0:
        pronunciation_score = 100.0
    else:
        ratio_erreur = dist_jamo / max_len
        
        # --- NEW FRIENDLY NOTATION LOGIC ---
        # Instead of dropping fast, we use a friendly linear scale.
        # We give a small grace cushion for minor AI/ASR detection variations.
        if ratio_erreur <= 0.10:
            # Minor mistakes (under 10% error): Very high score (90 to 100)
            pronunciation_score = 100.0 - (ratio_erreur * 100)
        else:
            # Larger mistakes: Standard gradual drop instead of a sudden crash
            pronunciation_score = 100.0 - (ratio_erreur * 110)

    # Keep pronunciation score strictly between 0 and 100
    pronunciation_score = max(0.0, min(100.0, pronunciation_score))
    
    # --- NEW FORGIVING FLUENCY LOGIC ---
    # We count the number of syllables in the target sentence
    syllables_count = len(target)
    speech_rate = syllables_count / audio_duration if audio_duration > 0 else 0
    
    # We widened the ideal window to 1.8 - 5.0 syllables/sec 
    # This ensures slow-reading kids (turtles 🐢) don't lose massive points!
    if 1.8 <= speech_rate <= 5.0:
        fluidity_score = 100.0
    elif speech_rate < 1.8:
        # Soft penalty for slow reading (minimum score is 50 instead of 30)
        fluidity_score = max(50.0, 100.0 - (1.8 - speech_rate) * 20)
    else:
        # Soft penalty for abnormally fast reading
        fluidity_score = max(50.0, 100.0 - (speech_rate - 5.0) * 15)

    # Global Score (Weighted average: 70% Pronunciation, 30% Fluency)
    final_score = (pronunciation_score * 0.7) + (fluidity_score * 0.3)
        
    return {
        "target": target,
        "recognized": recognized,
        "pronunciation_score": round(float(pronunciation_score), 2),
        "fluidity_score": round(float(fluidity_score), 2),
        "speech_rate": round(float(speech_rate), 2),
        "score": round(float(final_score), 2)
    }