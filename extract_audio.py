import pandas as pd
import shutil
import os

# --- PATH CONFIGURATION ---
csv_path = 'data/k_read_coach_dataset.csv'
source_folder = '/mnt/c/Users/tomke/Documents/archive/kss/' 
destination_folder = 'data/clips/'

if os.path.exists(destination_folder):
    print(f"Cleaning out old files from {destination_folder}...")
    shutil.rmtree(destination_folder)
os.makedirs(destination_folder)

try:
    df = pd.read_csv(csv_path)
    print(f"Loaded CSV. Processing {len(df)} files...")
    
    updated_paths = []

    for index, row in df.iterrows():
        original_rel_path = row['path'] # e.g., '1/1_0000.wav'
        
        # Get just the filename (e.g., '1_0000.wav')
        filename = os.path.basename(original_rel_path)
        
        source_path = os.path.join(source_folder, original_rel_path)
        dest_path = os.path.join(destination_folder, filename)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            # Update the path in our list to be just the filename
            updated_paths.append(filename)
            print(f"✅ Flattened: {filename}")
        else:
            print(f"❌ Not found: {original_rel_path}")
            updated_paths.append(original_rel_path) # Keep original if not found

    # Update the dataframe and save it back to CSV
    df['path'] = updated_paths
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\nFinished! All files are now in {destination_folder}")

except Exception as e:
    print(f"An error occurred: {e}")