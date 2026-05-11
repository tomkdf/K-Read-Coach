import pandas as pd
from faster_whisper import WhisperModel
import Levenshtein
import os
import re
from jamo import h2j, j2hcj

# --- JAMO DECOMPOSITION FUNCTION ---
def get_jamo_text(text):
    if not text:
        return ""
    # Cleaning: keep letters and numbers, remove spaces and punctuation
    text = re.sub(r'[^\w]', '', text)
    # h2j transforms blocks into jamo (e.g., 죽 -> ㅈㅜㄱ), j2hcj separates them properly
    return j2hcj(h2j(text))

# --- CONFIGURATION ---
single_audio_path = "path/to/the/audio.wav" 
expected_sentence = "Expected senctence in Korean"

# CSV configuration
# csv_path = "/data/Documents/Audacity/k_read_coach_dataset.csv"
# audio_folder = "/data/Documents/Audacity/"

model = WhisperModel("small", device="cpu", compute_type="int8")

# --- CSV LOADING AND LOOPING ---
# df = pd.read_csv(csv_path)
# results = []
# print("Analysis in progress (Blocks + Jamos)...")
# # Testing on the first 20 rows as an example
# for index, row in df.head(20).iterrows():
#     audio_file = os.path.join(audio_folder, row['path'])

print(f"Processing single file: {single_audio_path}")

# Check if the specific file exists
if os.path.exists(single_audio_path):
    # Transcription process
    segments, _ = model.transcribe(single_audio_path, language="ko")
    transcribed_text = "".join([s.text for s in segments]).strip()
    
    # --- BLOCK-LEVEL ANALYSIS (HANGUL) ---
    expected_block = re.sub(r'[^\w]', '', expected_sentence)
    obtained_block = re.sub(r'[^\w]', '', transcribed_text)
    dist_block = Levenshtein.distance(expected_block, obtained_block)
    
    # --- JAMO-LEVEL ANALYSIS (PHONETIC) ---
    expected_jamo = get_jamo_text(expected_sentence)
    obtained_jamo = get_jamo_text(transcribed_text)
    dist_jamo = Levenshtein.distance(expected_jamo, obtained_jamo)
    
    # Calculate Jamo similarity score (more accurate for pronunciation accuracy)
    max_len = max(len(expected_jamo), len(obtained_jamo))
    score_jamo = (1 - (dist_jamo / max_len)) * 100 if max_len > 0 else 100
    
    # --- DISPLAY RESULTS ---
    print("\n--- ANALYSIS RESULTS ---")
    print(f"Expected    : {expected_sentence}")
    print(f"Transcribed : {transcribed_text}")
    print(f"Block Dist  : {dist_block}")
    print(f"Jamo Dist   : {dist_jamo}")
    print(f"Phonetic Score: {round(score_jamo, 2)}%")
    print("------------------------")

    # --- APPENDING TO RESULTS LIST ---
    # results.append({
    #     "File": single_audio_path,
    #     "Expected": expected_sentence,
    #     "Transcribed": transcribed_text,
    #     "Block_Dist": dist_block,
    #     "Jamo_Dist": dist_jamo,
    #     "Phonetic_Score_%": round(score_jamo, 2)
    # })
else:
    print(f"Error: File not found at {single_audio_path}")

# --- SAVE RESULTS TO CSV ---
# results_df = pd.DataFrame(results)
# results_df.to_csv("analyse_jamo_complete.csv", index=False)
# print("\nFinished! The file 'analyse_jamo_complete.csv' now contains the phonetic analysis.")