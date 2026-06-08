import Levenshtein
import re
from jamo import h2j, j2hcj
import math

def get_jamo_text(text):
    if not text:
        return ""
    # Nettoyage des caractères non-alphanumériques
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
        
        # --- NOUVELLE LOGIQUE DE NOTATION ---
        if ratio_erreur <= 0.05:
            # Sévérité Faible : Si l'erreur est infime (<5%), c'est un natif ou une micro-erreur de l'ASR.
            # On maintient un score très élevé (au-dessus de 90).
            pronunciation_score = 100.0 - (ratio_erreur * 200) 
        else:
            # Sévérité Forte : Si l'erreur dépasse 5%, la courbe chute très vite (Loi de puissance / Exponentielle stricte).
            # Un débutant qui fait plusieurs fautes va voir son score descendre drastiquement.
            pronunciation_score = math.exp(-4.5 * ratio_erreur) * 100

    # Limitation stricte entre 0 et 100
    pronunciation_score = max(0.0, min(100.0, pronunciation_score))
    
    # --- CALCUL DE LA FLUIDITÉ (Exemple pour correspondre à ton app.py) ---
    # On calcule le nombre de syllabes par seconde
    syllables_count = len(target)
    speech_rate = syllables_count / audio_duration if audio_duration > 0 else 0
    
    # Score de fluidité idéal entre 2.5 et 4.5 syllabes/sec
    if 2.5 <= speech_rate <= 5.0:
        fluidity_score = 100.0
    else:
        # Pénalité si trop lent (débutant) ou anormalement rapide
        fluidity_score = max(30.0, 100.0 - abs(speech_rate - 3.5) * 20)

    # Note globale (Moyenne pondérée : 70% Prononciation, 30% Fluidité)
    final_score = (pronunciation_score * 0.7) + (fluidity_score * 0.3)
        
    return {
        "target": target,
        "recognized": recognized,
        "pronunciation_score": round(float(pronunciation_score), 2),
        "fluidity_score": round(float(fluidity_score), 2),
        "speech_rate": round(float(speech_rate), 2),
        "score": round(float(final_score), 2)
    }
