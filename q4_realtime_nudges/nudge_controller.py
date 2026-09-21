"""
Question 4: Real-Time Audio Insights - Nudge Controller & Suppression Engine
Enforces confidence thresholds, duplicate suppression, cooldown timers,
topic priority rules, and logs false-positive audit trails.
"""

from typing import List, Dict, Optional, Tuple, Any
from .models import DetectedSignal, SignalType, AgentNudge, NudgeSeverity

class NudgeController:
    """
    Nudge Controller that shields human agents from cognitive overload:
    - Confidence Threshold: Suppresses low-confidence signals (< 0.70)
    - Duplicate Suppression: Rejects repetitive alerts for the same underlying topic
    - Cooldown Timers: Enforces 30-second cooldown per topic
    - Priority Assignment: CRITICAL (Compliance) > WARNING (Frustration, Hardship) > INFO (Cross-sell)
    - False-Positive Auditing: Records reasons when alerts are safely squashed
    """

    COOLDOWN_WINDOW_MS = 30000  # 30 seconds
    CONFIDENCE_THRESHOLD = 0.70

    def __init__(self):
        self.active_nudges: List[AgentNudge] = []
        self.cooldown_tracker: Dict[str, int] = {}  # key -> last_fired_timestamp_ms
        self.suppressed_log: List[Dict[str, Any]] = []

    def evaluate_signal(self, signal: DetectedSignal) -> Optional[AgentNudge]:
        """
        Evaluates a detected signal and returns an AgentNudge if passed,
        or None if suppressed by rules.
        """
        # Rule 1: Confidence threshold check (prevents noisy / ambiguous false alarms)
        if signal.confidence < self.CONFIDENCE_THRESHOLD or signal.signal_type == SignalType.AMBIGUOUS_NOISE:
            self.suppressed_log.append({
                "signal_id": signal.signal_id,
                "type": signal.signal_type.value,
                "confidence": signal.confidence,
                "reason": "LOW_CONFIDENCE_SUPPRESSION: Below threshold 0.70",
                "timestamp_ms": signal.timestamp_offset_ms
            })
            return None

        cooldown_key = f"{signal.signal_type.value}"

        # Rule 2: Cooldown & Duplicate Check
        last_fired = self.cooldown_tracker.get(cooldown_key, -999999)
        time_since_last = signal.timestamp_offset_ms - last_fired

        if time_since_last < self.COOLDOWN_WINDOW_MS:
            self.suppressed_log.append({
                "signal_id": signal.signal_id,
                "type": signal.signal_type.value,
                "confidence": signal.confidence,
                "reason": f"COOLDOWN_ACTIVE: {time_since_last}ms since last nudge (min 30000ms)",
                "timestamp_ms": signal.timestamp_offset_ms
            })
            return None

        # Build appropriate actionable nudge based on signal
        nudge = self._create_nudge_from_signal(signal, cooldown_key)
        if nudge:
            self.cooldown_tracker[cooldown_key] = signal.timestamp_offset_ms
            self.active_nudges.append(nudge)
            return nudge

        return None

    def _create_nudge_from_signal(self, signal: DetectedSignal, cooldown_key: str) -> Optional[AgentNudge]:
        if signal.signal_type == SignalType.COMPLIANCE_GAP:
            return AgentNudge(
                signal_type=signal.signal_type,
                severity=NudgeSeverity.CRITICAL,
                headline="⚠️ COMPLIANCE RISK: Recording Disclosure Missing",
                recommendation="Read mandatory statement immediately: 'Please note this call is recorded for quality and compliance purposes.'",
                rationale="Regulatory mandate: Call recording disclosure must be given within the first two agent speaking turns.",
                priority=1,
                timestamp_offset_ms=signal.timestamp_offset_ms,
                cooldown_key=cooldown_key,
                expires_in_seconds=30
            )

        elif signal.signal_type == SignalType.MISSED_CROSS_SELL:
            entity = signal.metadata.get("entity", "asset")
            return AgentNudge(
                signal_type=signal.signal_type,
                severity=NudgeSeverity.INFO,
                headline=f"💡 CROSS-SELL OPPORTUNITY: {signal.metadata.get('trigger', 'Secondary Need')}",
                recommendation=f"Customer mentioned '{entity}'. Offer our Multi-Vehicle / Family Umbrella bundle for 15% combined savings.",
                rationale="Customer showed organic buying intent for additional insurable assets.",
                priority=3,
                timestamp_offset_ms=signal.timestamp_offset_ms,
                cooldown_key=cooldown_key,
                expires_in_seconds=45
            )

        elif signal.signal_type == SignalType.RISING_FRUSTRATION:
            return AgentNudge(
                signal_type=signal.signal_type,
                severity=NudgeSeverity.WARNING,
                headline="🚨 CUSTOMER FRUSTRATION DETECTED",
                recommendation="Pause sales script. Acknowledge caller's delay/frustration: 'I sincerely apologize for the runaround you experienced; let me take personal ownership of this.'",
                rationale="Elevated sentiment risk. Failure to de-escalate will trigger churn or formal complaint.",
                priority=2,
                timestamp_offset_ms=signal.timestamp_offset_ms,
                cooldown_key=cooldown_key,
                expires_in_seconds=40
            )

        elif signal.signal_type == SignalType.PAYMENT_DIFFICULTY:
            return AgentNudge(
                signal_type=signal.signal_type,
                severity=NudgeSeverity.WARNING,
                headline="🤝 FINANCIAL HARDSHIP ASSISTANCE",
                recommendation="Offer approved payment hardship path: Split payments into monthly installments or offer high-deductible premium reduction.",
                rationale="Borrower expressed acute cashflow constraint.",
                priority=2,
                timestamp_offset_ms=signal.timestamp_offset_ms,
                cooldown_key=cooldown_key,
                expires_in_seconds=45
            )

        return None

    def get_false_positive_analysis(self) -> Dict[str, Any]:
        """
        Returns statistical breakdown of caught vs suppressed alerts.
        """
        total_fired = len(self.active_nudges)
        total_suppressed = len(self.suppressed_log)
        total_signals = total_fired + total_suppressed

        return {
            "total_signals_detected": total_signals,
            "nudges_dispatched": total_fired,
            "signals_suppressed_as_noise_or_duplicate": total_suppressed,
            "suppression_ratio": f"{(total_suppressed / max(1, total_signals)) * 100:.1f}%",
            "suppressed_reasons": self.suppressed_log
        }
