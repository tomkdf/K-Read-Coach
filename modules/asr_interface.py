"""
ASR (Automatic Speech Recognition) Interface Module

This module provides the transcription interface for the K-Read Coach application.
Currently a mock implementation that returns a fixed Korean greeting.

ASR Implementation Guide:
  To replace this mock implementation with actual ASR functionality:
  1. Keep the function signature: transcribe_audio(audio_path: str) -> str
  2. Replace the function body with your actual ASR logic
  3. No changes needed in app.py or other modules - this interface is self-contained
  4. The function should accept an audio file path and return the transcribed text as a string
"""


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text.

    Mock Implementation:
      Currently returns a fixed Korean greeting regardless of input.
      This serves as a placeholder until actual ASR implementation is integrated.

    Args:
        audio_path: Path to the audio file (currently ignored in mock mode)

    Returns:
        Transcribed text as a string. In mock mode, always returns "안녕하세요"

    Note:
        ASR team: Replace the return statement below with your ASR implementation.
        The function signature and return type must remain unchanged.
    """
    return "안녕하세요"
