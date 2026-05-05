"""
Dataset Cleaning Script for K-Read Coach

This script processes a Korean speech transcript dataset to create a curated subset
of daily conversation sentences suitable for language learning applications.
It filters transcripts based on relevant keywords, categorizes them by topic,
and outputs a clean CSV file with Korean sentences, English translations, and categories.
"""

import pandas as pd
import os

def process_dataset(transcript_file, output_file, num_sentences=29):
    """
    Process the raw transcript file to create a filtered dataset.
    
    Args:
        transcript_file (str): Path to the input transcript CSV file
        output_file (str): Path where the processed dataset will be saved
        num_sentences (int): Number of sentences to sample (default: 29)
    
    Returns:
        None: Saves the processed dataset to output_file
    """
    # Define column names for the transcript file
    # Expected format: path|original|script|expanded|duration|english_translation
    cols = ['path', 'original', 'script', 'expanded', 'duration', 'english_translation']
    
    # Load the transcript data
    df = pd.read_csv(transcript_file, sep='|', names=cols, header=None, encoding='utf-8')

    # --- THEMES FILTER ---
    # Define keywords for filtering daily conversation topics
    # These Korean words represent common everyday situations
    
    keywords = [
        # School & Education
        '학교', '선생님', '수업', '교실', '숙제', '시험', '공부', '학생', '도서관',
        
        # Food & Ordering (Cafes/Restaurants)
        '커피', '메뉴', '주문', '추천', '포장', '먹어', '맛있', '식당', '계산', '카드', '현금',
        
        # Transportation & Directions
        '버스', '지하철', '택시', '정거장', '역', '어디', '어떻게', '멀어', '가까워', '타다',
        
        # Shopping & Prices
        '얼마', '비싸', '싸요', '할인', '세일', '사이즈', '입어', '환불', '교환',
        
        # Health & Body (Vital for students/parents)
        '아파', '병원', '약국', '감기', '머리', '배', '열나요', '처방전',
        
        # Social Media & Modern Slang
        '진짜', '대박', '맞팔', '좋아요', '인스타', '사진', '동영상', '링크', '메시지',
        
        # Time & Daily Routine
        '오늘', '내일', '어제', '지금', '언제', '약속', '주말', '집', '자다', '일어나'
    ]
    
    
    # Create regex pattern from keywords and filter rows containing any keyword
    pattern = '|'.join(keywords)
    daily_df = df[df['original'].str.contains(pattern, na=False)].copy()

    # Filter for reasonable sentence length (5-20 characters for learning purposes)
    daily_df['text_length'] = daily_df['original'].str.len()
    filtered_df = daily_df[(daily_df['text_length'] >= 5) & (daily_df['text_length'] <= 20)]

    # Randomly sample the specified number of sentences
    if len(filtered_df) >= num_sentences:
        processed_df = filtered_df.sample(n=num_sentences, random_state=42).copy()
    else:
        processed_df = filtered_df

    # Add Categories based on keywords (Optional but helpful)
    def categorize(text):
        """
        Categorize a Korean sentence based on its content keywords.
        
        Args:
            text (str): The Korean sentence to categorize
            
        Returns:
            str: Category name
        """
        # Food & Dining
        if any(word in text for word in ['점심', '식당', '주문', '계란', '포장', '배불러']):
            return 'Food & Dining'
        
        # Transportation
        if any(word in text for word in ['버스', '역', '정류장', '어디', '가요']):
            return 'Transportation'
        
        # School & Work
        if any(word in text for word in ['학교', '수업', '시험', '일', '공부']):
            return 'School & Work'
        
        # Weather
        if any(word in text for word in ['날씨', '기온', '봄', '여름', '가을', '겨울', '비', '눈', '맑음']):
            return 'Weather'

        # Time & Calendar
        if any(word in text for word in ['어제', '오늘', '내일', '달력', '시간', '요일', '시', '분']):
            return 'Time'
        
        # Shopping & Fashion
        if any(word in text for word in ['백화점', '옷', '입어', '향기', '얼마', '사이즈']):
            return 'Shopping & Fashion'
        
        # Social & Emotions
        if any(word in text for word in ['안부', '잘 지내', '성함', '세상에', '정신', '출소']):
            return 'Social & Emotions'
        
        # Default category
        return 'Daily Life'

    # Apply categorization to each sentence
    processed_df['categories'] = processed_df['original'].apply(categorize)

    # Prepare final dataset with required columns
    # Note: KSS paths often look like '1/1_0000.wav', ensure your folder structure matches
    final_df = processed_df[['path', 'original', 'english_translation', 'categories']]
    final_df.columns = ['path', 'sentence', 'english_translation', 'categories']
    
    # Save the processed dataset
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Created dataset with {len(final_df)} high-quality daily sentences.")

if __name__ == "__main__":
    # Main execution: process the transcript file and create the dataset
    process_dataset('transcript.txt', 'data/k_read_coach_dataset.csv')