import pandas as pd
import shutil
import os

# --- PATH CONFIGURATION ---
# The CSV containing our 29 selected sentences and their KSS subfolder paths
csv_path = 'data/k_read_coach_dataset.csv'

# Path to the full KSS dataset on your local machine
source_folder = 'kss/' 

# The target folder for our app's specific audio clips (flattened)
destination_folder = 'data/clips/'

# --- CLEANUP STEP ---
# We wipe the destination folder to ensure no old or 'crab-shell' files remain
if os.path.exists(destination_folder):
    print(f"Cleaning out old files from {destination_folder}...")
    shutil.rmtree(destination_folder)

# Recreate the clean folder
os.makedirs(destination_folder)

# --- EXTRACTION & FLATTENING STEP ---
try:
    # Load our curated dataset
    df = pd.read_csv(csv_path)
    print(f"Loaded CSV. Processing {len(df)} files...")
    
    # This list will store the new, simplified paths (just filenames)
    updated_paths = []

    for index, row in df.iterrows():
        # KSS original paths are like '1/1_0000.wav'
        original_rel_path = row['path'] 
        
        # Remove the '1/' prefix to keep only the filename (e.g., '1_0000.wav')
        filename = os.path.basename(original_rel_path)
        
        # Construct full source and target paths
        source_path = os.path.join(source_folder, original_rel_path)
        dest_path = os.path.join(destination_folder, filename)
        
        # Copy the file only if it exists in the source KSS directory
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            
            # Store the new filename so we can update our CSV later
            updated_paths.append(filename)
            print(f"✅ Flattened: {filename}")
        else:
            # Alert if a path in the CSV doesn't match the actual local files
            print(f"❌ Not found: {original_rel_path}")
            updated_paths.append(original_rel_path) 

    # --- CSV SYNC STEP ---
    # We update the 'path' column in our dataframe to use the new flat filenames
    df['path'] = updated_paths
    
    # Save the updated CSV (overwriting the old one) with UTF-8-SIG for Korean support
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\nFinished! All files are now in {destination_folder}")
    print(f"The CSV has been updated with the new flat file paths.")

except Exception as e:
    # Basic error handling to catch permission issues or missing CSVs
    print(f"An error occurred: {e}")