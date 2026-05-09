def generate_feedback(score: float) -> str:
    if score >= 90:
        return "Excellent! Your pronunciation is very accurate."
    elif score >= 75:
        return "Good job! You're getting close to the target pronunciation."
    elif score >= 50:
        return "Keep practicing! Focus on the highlighted differences."
    else:
        return "Don't give up! Try listening to the reference audio again."
