import pandas as pd
import os

def process_dataset(transcript_file, output_file, num_sentences=29):
    # We name the columns based on the format you provided
    cols = ['path', 'original', 'script', 'expanded', 'duration', 'english_translation']
    
    df = pd.read_csv(transcript_file, sep='|', names=cols, header=None, encoding='utf-8')

    # --- THEMES FILTER ---
    
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
    
    
    pattern = '|'.join(keywords)
    daily_df = df[df['original'].str.contains(pattern, na=False)].copy()

    # Filter for reasonable length (between 10 and 30 characters)
    daily_df['text_length'] = daily_df['original'].str.len()
    filtered_df = daily_df[(daily_df['text_length'] >= 5) & (daily_df['text_length'] <= 20)]

    # Take 29 random samples
    if len(filtered_df) >= num_sentences:
        processed_df = filtered_df.sample(n=num_sentences, random_state=42).copy()
    else:
        processed_df = filtered_df

    # Add Categories based on keywords (Optional but helpful)
    def categorize(text):
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

    processed_df['categories'] = processed_df['original'].apply(categorize)

    # Save to your project format
    # Note: KSS paths often look like '1/1_0000.wav', ensure your folder structure matches
    final_df = processed_df[['path', 'original', 'english_translation', 'categories']]
    final_df.columns = ['path', 'sentence', 'english_translation', 'categories']
    
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Created dataset with {len(final_df)} high-quality daily sentences.")

if __name__ == "__main__":
    # Point this to your transcript file
    process_dataset('transcript.txt', 'data/k_read_coach_dataset.csv')