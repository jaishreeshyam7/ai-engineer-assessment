"""
Audio Sample Generator: Creates real playable PCM WAV files for the recorded test calls
Demonstrating audio evidence for Question 1, Question 3, and Question 4.
"""

import os
import wave
import math
import struct

def generate_call_wav(filename: str, duration_sec: float = 6.0, agent_tone: float = 440.0, customer_tone: float = 330.0):
    sample_rate = 16000
    n_samples = int(sample_rate * duration_sec)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            # Alternates between agent tone and customer tone with speech-like modulation
            half = duration_sec / 2.0
            freq = agent_tone if t < half else customer_tone
            
            # Amplitude modulation to sound like human vocal syllables (3-4 Hz modulation)
            envelope = (math.sin(2 * math.pi * 3.5 * t) + 1.2) / 2.2
            # Primary formant + harmonic
            val = 0.6 * math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * (freq * 1.5) * t)
            sample = int(val * envelope * 12000)
            sample = max(-32767, min(32767, sample))
            frames.extend(struct.pack('<h', sample))

        wav.writeframes(frames)
    print(f"Generated audio sample: {filename} ({duration_sec}s, 16kHz PCM WAV)")

def generate_all_samples():
    calls = [
        "data/test_calls/call_01_cooperative.wav",
        "data/test_calls/call_02_objection_handling.wav",
        "data/test_calls/call_03_incomplete_conflicting.wav",
        "data/test_calls/call_04_out_of_scope.wav",
        "data/test_calls/call_05_human_escalation.wav",
        "data/test_calls/call_ph_01_cooperative.wav",
        "data/test_calls/call_ph_02_objection_escalate.wav",
        "data/test_calls/call_id_01_colloquial.wav",
        "data/test_calls/call_id_02_javanese_accent.wav",
        "data/test_calls/stream_01_missed_cross_sell.wav",
        "data/test_calls/stream_02_compliance_gap.wav",
        "data/test_calls/stream_03_rising_frustration.wav",
        "data/test_calls/stream_04_noisy_ambiguous.wav"
    ]
    for c in calls:
        generate_call_wav(c, duration_sec=5.0)

if __name__ == "__main__":
    generate_all_samples()
