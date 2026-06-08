import Levenshtein
import re
from jamo import h2j, j2hcj

# --- CONFIGURATION DES COULEURS ---
COLOR_PERFECT = "#27ae60"  # Vert (match parfait des jamos)
COLOR_GOOD = "#f39c12"     # Orange (match partiel, ex: bonne consonne mais mauvaise voyelle)
COLOR_ERROR = "#c0392b"    # Rouge (erreur complète ou jamo manquant)
COLOR_DEFAULT = "#7f8c8d"  # Gris (ponctuation, espaces, non évalué)

def get_jamo_text(text):
    if not text:
        return ""
    # Nettoyage : garde lettres et chiffres, enlève ponctuation/espaces
    text = re.sub(r'[^\w]', '', text)
    return j2hcj(h2j(text))

def count_korean_syllables(text: str) -> int:
    """Compte les blocs syllabiques coréens."""
    return len(re.findall(r'[\uac00-\ud7a3]', text))

def is_korean_block(char: str) -> bool:
    """Vérifie si un caractère est un bloc syllabique coréen complet."""
    if len(char) != 1: return False
    return 0xAC00 <= ord(char) <= 0xD7A3

def compare_texts(target: str, recognized: str, audio_duration: float = None) -> dict:
    """Compare le texte attendu et reconnu, incluant la fluidité et la coloration."""
    
    # --- 1. JAMO-LEVEL ANALYSIS (PRONONCIATION DÉTAILLÉE) ---
    expected_jamo = get_jamo_text(target)
    obtained_jamo = get_jamo_text(recognized)
    
    dist_jamo = Levenshtein.distance(expected_jamo, obtained_jamo)
    max_len = max(len(expected_jamo), len(obtained_jamo))
    score_jamo = (1 - (dist_jamo / max_len)) * 100 if max_len > 0 else 100
    
    # --- 2. ALIGNEMENT POU COLORATION (CARACTÈRE PAR CARACTÈRE) ---
    # Cette liste stockera la couleur associée à chaque caractère de 'target'
    char_colors = []
    
    # Nous utilisons l'alignement de Levenshtein pour savoir quelle partie de 'recognized'
    # correspond à quelle partie de 'target'.
    # On compare les Jamos, caractère par caractère.
    
    ptr_obs = 0  # Pointeur dans obtained_jamo
    
    for char_target in target:
        # Si ce n'est pas du coréen (espace, ., !), on garde la couleur par défaut
        if not is_korean_block(char_target):
            char_colors.append(COLOR_DEFAULT)
            continue
            
        # Sinon, on décompose ce caractère cible en Jamos
        target_jamos = j2hcj(h2j(char_target))
        
        # On essaie d'extraire la même quantité de Jamos depuis la reconnaissance
        if ptr_obs < len(obtained_jamo):
            # On prend les 'len(target_jamos)' Jamos suivants
            obs_jamos_segment = obtained_jamo[ptr_obs : ptr_obs + len(target_jamos)]
            
            # Comparaison de ce bloc de Jamos précis
            j_dist = Levenshtein.distance(target_jamos, obs_jamos_segment)
            j_max = len(target_jamos)
            
            # --- LOGIQUE DE COLORATION PEDAGOGIQUE ---
            # Match parfait de tous les jamos du bloc
            if j_dist == 0:
                char_colors.append(COLOR_PERFECT)
            # Match partiel (ex: ㄱ pronounce ㄲ, ou ㅏ pronounce ㅓ)
            elif j_dist < j_max:
                char_colors.append(COLOR_GOOD)
            # Erreur totale ou jamo manquant
            else:
                char_colors.append(COLOR_ERROR)
                
            # On avance notre pointeur d'observation
            ptr_obs += len(target_jamos)
            
        else:
            # Plus rien n'a été reconnu, c'est une omission
            char_colors.append(COLOR_ERROR)
            
    # --- 3. FLUIDITY ANALYSIS (SPEECH RATE) ---
    # (Exactement le même code que dans l'étape précédente)
    score_fluidity = 100.0
    speech_rate = 0.0
    if audio_duration and audio_duration > 0:
        syllable_count = count_korean_syllables(target)
        if syllable_count > 0:
            speech_rate = syllable_count / audio_duration
            if 2.0 <= speech_rate <= 4.0: score_fluidity = 100.0
            elif speech_rate < 2.0: score_fluidity = max(10.0, 100.0 - (2.0 - speech_rate) * 45)
            else: score_fluidity = max(10.0, 100.0 - (speech_rate - 4.0) * 30)
                
    # --- 4. SCORE GLOBAL COMBINÉ ---
    final_score = (score_jamo * 0.70) + (score_fluidity * 0.30)
    
    # Ajout des données de coloration au résultat
    return {
        "target": target,
        "recognized": recognized,
        "score": round(float(final_score), 2),
        "pronunciation_score": round(float(score_jamo), 2),
        "fluidity_score": round(float(score_fluidity), 2),
        "speech_rate": round(float(speech_rate), 2),
        # --- BONUS : La liste des couleurs caractère par caractère ---
        "char_colors": char_colors
    }