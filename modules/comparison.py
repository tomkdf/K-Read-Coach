import Levenshtein
import re
from jamo import h2j, j2hcj

def get_jamo_text(text):
    if not text:
        return ""
    # Nettoyage : garde lettres et chiffres, enlève ponctuation/espaces
    text = re.sub(r'[^\w]', '', text)
    return j2hcj(h2j(text))

def compare_texts(target: str, recognized: str) -> dict:
    # --- JAMO-LEVEL ANALYSIS ---
    expected_jamo = get_jamo_text(target)
    obtained_jamo = get_jamo_text(recognized)
    
    # Calcul de la distance de Levenshtein sur les jamos
    dist_jamo = Levenshtein.distance(expected_jamo, obtained_jamo)
    
    # Calcul du score final
    max_len = max(len(expected_jamo), len(obtained_jamo))
    score_jamo = (1 - (dist_jamo / max_len)) * 100 if max_len > 0 else 100
    
    return {
        "target": target,
        "recognized": recognized,
        "score": round(float(score_jamo), 2)
    }
    