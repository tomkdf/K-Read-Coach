import pandas as pd
import os


def get_mock_dataset() -> pd.DataFrame:
    data = {
        'path': ['greeting_01.wav', 'school_01.wav'],
        'sentence': ['안녕하세요', '학교에 갑니다'],
        'english_translation': ['Hello', 'I go to school'],
        'categories': ['Greeting', 'School']
    }
    return pd.DataFrame(data)


def load_dataset(csv_path: str) -> tuple[pd.DataFrame, bool]:
    if not os.path.exists(csv_path):
        return (get_mock_dataset(), False)

    df = pd.read_csv(csv_path)

    required_fields = ['path', 'sentence', 'english_translation', 'categories']
    missing_fields = sorted(set(required_fields) - set(df.columns))

    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return (df, True)


def get_categories(df: pd.DataFrame) -> list[str]:
    return sorted(df['categories'].unique())


def get_sentences_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    return df[df['categories'] == category]
