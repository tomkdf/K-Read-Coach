import Levenshtein
import re
from jamo import h2j, j2hcj

def get_jamo_text(text):
    if not text:
        return ""
    # Nettoyage : garde uniquement les caractères alphanumériques coréens
    text = re.sub(r'[^\w]', '', text)
    return j2hcj(h2j(text))

def compare_texts(target: str, recognized: str, audio_duration: float = 1.0) -> dict:
    # 1. Analyse au niveau des Jamos pour la prononciation
    expected_jamo = get_jamo_text(target)
    obtained_jamo = get_jamo_text(recognized)
    
    dist_jamo = Levenshtein.distance(expected_jamo, obtained_jamo)
    max_len = max(len(expected_jamo), len(obtained_jamo))
    
    # Calcul du score de prononciation
    pronunciation_score = (1 - (dist_jamo / max_len)) * 100 if max_len > 0 else 100
    pronunciation_score = max(0.0, min(100.0, pronunciation_score))
    
    # 2. Analyse du rythme pour la fluidité (Speech Rate)
    # On compte le nombre de syllabes réelles dans la phrase cible (sans espaces/ponctuation)
    clean_target = re.sub(r'[^\w]', '', target)
    num_syllables = len(clean_target)
    
    # Vitesse d'élocution (syllabes par seconde)
    speech_rate = num_syllables / audio_duration if audio_duration > 0 else 0
    
    # Score de fluidité : un rythme naturel en lecture se situe entre 2.5 et 3.5 syllabes/sec
    if 2.2 <= speech_rate <= 3.8:
        fluidity_score = 100.0
    elif speech_rate < 2.2:
        # Trop lent (pénalité douce)
        fluidity_score = max(30.0, 100.0 - (2.2 - speech_rate) * 25)
    else:
        # Trop rapide
        fluidity_score = max(40.0, 100.0 - (speech_rate - 3.8) * 20)
        
    # Score général (Moyenne pondérée : 70% prononciation, 30% fluidité)
    final_score = (pronunciation_score * 0.7) + (fluidity_score * 0.3)
    
    return {
        "target": target,
        "recognized": recognized,
        "pronunciation_score": round(float(pronunciation_score), 2),
        "fluidity_score": round(float(fluidity_score), 2),
        "speech_rate": round(float(speech_rate), 2),
        "score": round(float(final_score), 2)
    }