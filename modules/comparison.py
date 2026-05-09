from rapidfuzz import fuzz


def compare_texts(target: str, recognized: str) -> dict:
    """
    Compare two texts and calculate their similarity score.

    Args:
        target: The reference text
        recognized: The recognized/transcribed text

    Returns:
        A dictionary containing:
        - target: The reference text
        - recognized: The recognized/transcribed text
        - score: Similarity score between 0.0 and 100.0
    """
    score = fuzz.ratio(target, recognized)
    return {
        "target": target,
        "recognized": recognized,
        "score": score
    }
