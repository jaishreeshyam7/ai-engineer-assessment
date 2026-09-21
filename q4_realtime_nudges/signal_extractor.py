"""
Question 4: Real-Time Audio Insights - Low-Latency Signal Extractor
Extracts compliance risks, sentiment degradation, missed cross-sell opportunities,
and detects ambiguous or noisy speech to prevent hallucinated alerts.
"""

import re
from typing import List, Optional
from .models import AudioChunk, Speaker, SignalType, DetectedSignal

class SignalExtractor:
    """
    Sub-50ms rule and keyword-vector signal extractor for real-time call audio streams:
    - Compliance Gap: Checks if agent failed mandatory recording disclosure by turn 2
    - Missed Cross-Sell: Captures mentions of family, secondary vehicles, mortgages
    - Rising Frustration: Tracks escalation language, repeated complaints, vocal distress
    - Payment Difficulty: Identifies financial distress or unemployment cues
    - Ambiguous Noise: Flags low-information or noisy inputs
    """

    MANDATORY_DISCLOSURES = [
        "recorded for quality",
        "recorded for quality assurance",
        "recorded for training",
        "recorded line"
    ]

    CROSS_SELL_TRIGGERS = [
        (r"\b(?:second|another|2nd)\s+(?:car|vehicle|auto|truck)\b", "Second Vehicle mentioned"),
        (r"\b(?:my\s+wife|my\s+husband|spouse|my\s+kid|my\s+daughter|my\s+son)\b", "Family Dependent mentioned"),
        (r"\b(?:bought\s+a\s+house|new\s+home|apartment|mortgage)\b", "Home / Property mentioned"),
        (r"\b(?:small\s+business|freelance|own\s+company)\b", "Commercial / Business asset mentioned")
    ]

    FRUSTRATION_TRIGGERS = [
        (r"\b(?:ridiculous|unacceptable|wasting\s+my\s+time|pissed\s+off|terrible\s+service)\b", 0.95),
        (r"\b(?:third\s+time|called\s+yesterday|nobody\s+called\s+me\s+back|transferred\s+three\s+times)\b", 0.90),
        (r"\b(?:talk\s+to\s+a\s+manager|give\s+me\s+a\s+supervisor|cancel\s+everything)\b", 0.95),
        (r"\b(?:frustrated|annoying|fed\s+up)\b", 0.85)
    ]

    PAYMENT_DIFFICULTY_TRIGGERS = [
        (r"\b(?:lost\s+my\s+job|laid\s+off|unemployed|no\s+income)\b", 0.92),
        (r"\b(?:can't\s+afford|too\s+expensive|no\s+money|behind\s+on\s+bills)\b", 0.88),
        (r"\b(?:hospital\s+bills|medical\s+emergency)\b", 0.82)
    ]

    NOISY_AMBIGUOUS_PATTERNS = [
        r"^(?:uh|um|hmm|yeah|okay|mhm|ah)+$",
        r"^(?:static|background\s+chatter|unclear|inaudible|muffled)+$"
    ]

    def __init__(self):
        self.disclosure_made = False
        self.agent_turn_count = 0

    def extract_signals(self, chunk: AudioChunk) -> List[DetectedSignal]:
        signals: List[DetectedSignal] = []
        text = chunk.text.strip()
        text_lower = text.lower()

        # Track agent compliance disclosures
        if chunk.speaker == Speaker.AGENT:
            self.agent_turn_count += 1
            if any(disc in text_lower for disc in self.MANDATORY_DISCLOSURES):
                self.disclosure_made = True

            # If agent has taken 2+ turns and still hasn't made mandatory disclosure
            if self.agent_turn_count >= 2 and not self.disclosure_made:
                signals.append(DetectedSignal(
                    signal_type=SignalType.COMPLIANCE_GAP,
                    confidence=0.96,
                    trigger_utterance=text,
                    speaker=Speaker.AGENT,
                    timestamp_offset_ms=chunk.timestamp_offset_ms,
                    metadata={"reason": "Mandatory call recording disclosure omitted by Agent by turn 2"}
                ))

        # Check for ambiguous / noisy chunks
        if any(re.search(pat, text_lower) for pat in self.NOISY_AMBIGUOUS_PATTERNS) or len(text.split()) <= 1:
            signals.append(DetectedSignal(
                signal_type=SignalType.AMBIGUOUS_NOISE,
                confidence=0.45,  # Low confidence -> should be suppressed by nudge controller
                trigger_utterance=text,
                speaker=chunk.speaker,
                timestamp_offset_ms=chunk.timestamp_offset_ms,
                metadata={"reason": "Acoustic noise or single non-semantic filler token"}
            ))
            return signals

        # Scan customer utterances
        if chunk.speaker == Speaker.CUSTOMER:
            # 1. Missed Cross-Sell Opportunities
            for pattern, trigger_desc in self.CROSS_SELL_TRIGGERS:
                match = re.search(pattern, text_lower)
                if match:
                    signals.append(DetectedSignal(
                        signal_type=SignalType.MISSED_CROSS_SELL,
                        confidence=0.91,
                        trigger_utterance=match.group(0),
                        speaker=Speaker.CUSTOMER,
                        timestamp_offset_ms=chunk.timestamp_offset_ms,
                        metadata={"trigger": trigger_desc, "entity": match.group(0)}
                    ))

            # 2. Rising Frustration / Sentiment Risk
            for pattern, conf in self.FRUSTRATION_TRIGGERS:
                match = re.search(pattern, text_lower)
                if match:
                    signals.append(DetectedSignal(
                        signal_type=SignalType.RISING_FRUSTRATION,
                        confidence=conf,
                        trigger_utterance=match.group(0),
                        speaker=Speaker.CUSTOMER,
                        timestamp_offset_ms=chunk.timestamp_offset_ms,
                        metadata={"risk_phrase": match.group(0)}
                    ))

            # 3. Payment Difficulty
            for pattern, conf in self.PAYMENT_DIFFICULTY_TRIGGERS:
                match = re.search(pattern, text_lower)
                if match:
                    signals.append(DetectedSignal(
                        signal_type=SignalType.PAYMENT_DIFFICULTY,
                        confidence=conf,
                        trigger_utterance=match.group(0),
                        speaker=Speaker.CUSTOMER,
                        timestamp_offset_ms=chunk.timestamp_offset_ms,
                        metadata={"hardship_phrase": match.group(0)}
                    ))

        return signals
