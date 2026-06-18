"""
Скрипт очистки и автоматического перевода датасета для K-Read Coach
"""

import pandas as pd
import os
from deep_translator import GoogleTranslator

def process_dataset(transcript_file, output_file, num_sentences=100):
    if not os.path.exists(transcript_file):
        print(f"❌ Ошибка: Файл {transcript_file} не найден!")
        return

    print(f"📂 Создание новой чистой базы данных на основе {transcript_file}...")

    # Нам не нужно загружать старые данные, так как мы пересоздаём всё с нуля
    cols = ['path', 'original', 'script', 'expanded', 'duration', 'english_text']
    df = pd.read_csv(transcript_file, sep='|', names=cols, header=None, encoding='utf-8')

    # --- КЛЮЧЕВЫЕ СЛОВА ДЛЯ ФИЛЬТРАЦИИ ---
    keywords = [
        '학교', '선생님', '수업', '교실', '숙제', '시험', '공부', '학생', '도서관',
        '커пи', '메뉴', '주문', '추천', '포장', '먹어', '맛있', '식당', '계산', '카드',
        '버스', '지하철', '택시', '정거장', '역', '어ди', '어떻게', '멀어', '가까워',
        '얼ма', '비싸', '싸요', '할인', '세일', '사이즈'
    ]
    pattern = '|'.join(keywords)
    filtered_df = df[df['original'].str.contains(pattern, na=False, case=False)]

    # Берём первые 100 уникальных строк
    processed_df = filtered_df.drop_duplicates(subset=['original']).head(num_sentences).copy()
    
    if processed_df.empty:
        print("❌ Не найдено фраз, соответствующих фильтрам.")
        return

    print(f"🔄 Автоматический перевод {len(processed_df)} фраз на русский язык...")
    
    translator = GoogleTranslator(source='en', target='ru')
    russian_translations = []
    
    for idx, eng_text in enumerate(processed_df['english_text']):
        try:
            translated = translator.translate(str(eng_text))
            russian_translations.append(translated)
        except Exception as e:
            russian_translations.append("Ошибка перевода")

    processed_df['russian_translation'] = russian_translations

    # Категоризация фраз
    def categorize(text):
        if any(word in text for word in ['점심', '식당', '주문', '먹어', '포장', '맛있', '커피', '메뉴']):
            return 'Еда и рестораны (음식 & 식당)'
        if any(word in text for word in ['버스', '역', '정류장', '어ди', '지하철', '택시']):
            return 'Транспорт (교통)'
        if any(word in text for word in ['학교', '수업', '시험', '공부', '숙제', '학생', '도서관']):
            return 'Учеба и работа (학교 & 직장)'
        if any(word in text for word in ['어제', '오늘', '내일', '시간', '주말', '지금']):
            return 'Время и расписание (시간 & 일정)'
        if any(word in text for word in ['얼ма', '비싸', '세일', '사이즈', '카드', '계산']):
            return 'Покупки (쇼핑)'
        return 'Повседневная жизнь (일상 생활)'

    processed_df['categories'] = processed_df['original'].apply(categorize)

    # Формируем структуру данных (сохраняем оригинальный относительный путь KSS для копирования)
    final_df = processed_df[['path', 'original', 'russian_translation', 'categories']].copy()
    final_df.columns = ['path', 'sentence', 'russian_translation', 'categories']
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ Новый файл базы данных успешно создан! Всего фраз: {len(final_df)}")

if __name__ == "__main__":
    process_dataset("kss/transcript.v1.txt", "data/k_read_coach_dataset.csv", num_sentences=100)
