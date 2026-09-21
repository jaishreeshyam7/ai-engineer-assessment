"""
Question 4: Real-Time Audio Insights & Nudges - Data Models
Defines streaming audio chunks, signals, actionable agent nudges, and latency metrics.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime

class Speaker(str, Enum):
    AGENT = "Agent"
    CUSTOMER = "Customer"

class SignalType(str, Enum):
    COMPLIANCE_GAP = "COMPLIANCE_GAP"
    MISSED_CROSS_SELL = "MISSED_CROSS_SELL"
    RISING_FRUSTRATION = "RISING_FRUSTRATION"
    PAYMENT_DIFFICULTY = "PAYMENT_DIFFICULTY"
    CHURN_RISK = "CHURN_RISK"
    AMBIGUOUS_NOISE = "AMBIGUOUS_NOISE"

class NudgeSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AudioChunk(BaseModel):
    chunk_id: str
    chunk_index: int
    speaker: Speaker
    text: str
    duration_ms: int = 1500
    timestamp_offset_ms: int
    audio_format: str = "pcm_16k"

class DetectedSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:6]}")
    signal_type: SignalType
    confidence: float
    trigger_utterance: str
    speaker: Speaker
    timestamp_offset_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentNudge(BaseModel):
    nudge_id: str = Field(default_factory=lambda: f"ndg_{uuid.uuid4().hex[:6]}")
    signal_type: SignalType
    severity: NudgeSeverity
    headline: str
    recommendation: str
    rationale: str
    priority: int  # 1 (Highest) to 5 (Lowest)
    timestamp_offset_ms: int
    cooldown_key: str
    expires_in_seconds: int = 40
    is_suppressed: bool = False
    suppression_reason: Optional[str] = None

class LatencyReport(BaseModel):
    chunk_id: str
    asr_ms: float
    signal_ms: float
    nudge_ms: float
    delivery_ms: float
    total_e2e_ms: float
