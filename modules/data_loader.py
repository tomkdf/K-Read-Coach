import pandas as pd
import os

def get_mock_dataset() -> pd.DataFrame:
    """
    Тестовый датасет на случай отсутствия основного CSV-файла.
    """
    data = {
        'path': ['greeting_01.wav', 'school_01.wav', 'food_01.wav'],
        'sentence': ['안녕하세요', '학교에 갑니다', '커피 한 잔 주세요'],
        'russian_translation': ['Здравствуйте', 'Я иду в школу', 'Дайте одну чашку кофе, пожалуйста'],
        'categories': ['Приветствия (인사)', 'Учеба (학교)', 'Еда (음식)']
    }
    return pd.DataFrame(data)

def load_dataset(csv_path: str) -> tuple[pd.DataFrame, bool]:
    if not os.path.exists(csv_path):
        return (get_mock_dataset(), False)

    df = pd.read_csv(csv_path)

    # Требуемые поля исключают английский язык и теперь строго привязаны к русскому переводу
    required_fields = ['path', 'sentence', 'russian_translation', 'categories']
    missing_fields = sorted(set(required_fields) - set(df.columns))

    if missing_fields:
        raise ValueError(f"Отсутствуют обязательные поля в файле данных: {', '.join(missing_fields)}")

    return (df, True)

def get_categories(df: pd.DataFrame) -> list[str]:
    return sorted(df['categories'].unique())

def get_sentences_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    return df[df['categories'] == category]