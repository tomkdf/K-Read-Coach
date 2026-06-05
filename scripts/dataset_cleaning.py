"""
Скрипт очистки и автоматического перевода датасета для K-Read Coach
"""

import pandas as pd
import os
from deep_translator import GoogleTranslator  # Библиотека для автоматического перевода

def process_dataset(transcript_file, output_file, num_sentences=100):
    """
    Обработка исходного файла и автоматический перевод английского текста на русский.
    """
    if not os.path.exists(transcript_file):
        print(f"❌ Ошибка: Файл {transcript_file} не найден!")
        return

    # Загружаем исходный файл (где последняя колонка всё еще на английском)
    cols = ['path', 'original', 'script', 'expanded', 'duration', 'english_text']
    df = pd.read_csv(transcript_file, sep='|', names=cols, header=None, encoding='utf-8')

    # --- КЛЮЧЕВЫЕ СЛОВА ДЛЯ ФИЛЬТРАЦИИ ---
    keywords = [
        '학교', '선생님', '수업', '교실', '숙제', '시험', '공부', '학생', '도서관',
        '커피', '메뉴', '주문', '추천', '포장', '먹어', '맛있', '식당', '계산', '카드',
        '버스', '지하철', '택시', '정거장', '역', '어ди', '어떻게', '멀어', '가까워',
        '얼ма', '비싸', '싸요', '할인', '세일', '사이즈', '입어', '환불', '교환',
        '아па', '병원', '약국', '감기', '머ри', '배', '열나요',
        '오늘', '내일', '어제', '지금', '언제', '약속', '주말', '집', '자다', '일어나'
    ]
    
    pattern = '|'.join(keywords)
    daily_df = df[df['original'].str.contains(pattern, na=False)].copy()

    # Фильтр по длине
    daily_df['text_length'] = daily_df['original'].str.len()
    filtered_df = daily_df[(daily_df['text_length'] >= 5) & (daily_df['text_length'] <= 25)]

    if len(filtered_df) >= num_sentences:
        processed_df = filtered_df.sample(n=num_sentences, random_state=42).copy()
    else:
        processed_df = filtered_df.copy()

    # --- ЭТАП НАСТОЯЩЕГО ПЕРЕВОДА ---
    print("⏳ Перевод текста с английского на русский (это может занять немного времени)...")
    translator = GoogleTranslator(source='en', target='ru')
    
    # Переводим каждую строчку из колонки английского текста
    russian_translations = []
    for text in processed_df['english_text']:
        try:
            # Переводим и убираем лишние пробелы
            translated = translator.translate(str(text)).strip()
            russian_translations.append(translated)
        except Exception as e:
            print(f"⚠️ Ошибка перевода строки '{text}': {e}")
            russian_translations.append(text) # В случае сбоя оставляем оригинал
            
    processed_df['russian_translation'] = russian_translations

    # Функция категоризации
    def categorize(text):
        if any(word in text for word in ['점심', '식당', '주문', '먹어', '포장', '맛있']):
            return 'Еда и рестораны (음식 & 식당)'
        if any(word in text for word in ['버스', '역', '정류장', '어디', '지하철', '택시']):
            return 'Транспорт (교통)'
        if any(word in text for word in ['학교', '수업', '시험', '공부', '숙제']):
            return 'Учеба и работа (학교 & 직장)'
        if any(word in text for word in ['어제', '오늘', '내일', '시간', '주말', '지금']):
            return 'Время и расписание (시간 & 일정)'
        if any(word in text for word in ['얼ма', '비싸', '세일', '사이즈', '카드']):
            return 'Покупки (쇼핑)'
        return 'Повседневная жизнь (일상 생활)'

    processed_df['categories'] = processed_df['original'].apply(categorize)

    # Формируем финальный датасет
    final_df = processed_df[['path', 'original', 'russian_translation', 'categories']]
    final_df.columns = ['path', 'sentence', 'russian_translation', 'categories']
    
    # Создаем папку data, если её нет
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Датасет успешно создан! {len(final_df)} предложений теперь переведены на РУССКИЙ язык.")

if __name__ == "__main__":
    # Замените 'transcript.txt' на точный путь к вашему исходному файлу, если он лежит в другой папке
    process_dataset('transcript.txt', 'data/k_read_coach_dataset.csv')