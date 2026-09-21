"""Question 3 Native-Language Voice Bots Package"""
from .philippines_bot import PhilippinesVoiceBot, PH_LOCALIZATION_SHOWCASE
from .indonesia_bot import IndonesiaVoiceBot, ID_LOCALIZATION_SHOWCASE
from .asr_tts_analysis import ASR_EVALUATIONS, TTS_EVALUATIONS

__all__ = [
    "PhilippinesVoiceBot", "PH_LOCALIZATION_SHOWCASE",
    "IndonesiaVoiceBot", "ID_LOCALIZATION_SHOWCASE",
    "ASR_EVALUATIONS", "TTS_EVALUATIONS"
]
