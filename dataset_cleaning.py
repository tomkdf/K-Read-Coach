import pandas as pd
import os


def clean_dataset(input_file, output_file, num_sentences=29):

    #Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return

    # Load the dataset
    df = pd.read_csv(input_file, sep='\t', encoding='utf-8')

    # Remove missing values (Missing text or file path)
    df = df.dropna(subset=['sentence', 'path'])

    # We keep only clips with positive up-votes and no down-votes to ensure clear audio
    quality_df = df[(df['up_votes'] >= 2) & (df['down_votes'] == 0)]

    # Filter for simplicity
    # We target short sentences to keep the tool beiginner-friendly
    quality_df['text_length'] = quality_df['sentence'].str.len()

    # Sort by shortest sentences and take the top candidates
    processed_df = quality_df.sort_values(by='text_length').head(num_sentences).copy()

    # Prepare colums for the Project Goals
    # We add placeholders for the English translation and categories
    processed_df['english_translation'] = "TBD" #To be translated
    processed_df['categories'] = "General" # To be categorized

    #Save the final curated dataset
    columns_to_save = ['path','sentence', 'english_translation', 'categories','up_votes']
    processed_df[columns_to_save].to_csv(output_file, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    clean_dataset('validated.tsv', 'data/k_read_coach_dataset.csv')