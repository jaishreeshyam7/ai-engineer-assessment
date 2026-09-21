"""
Question 4: Real-Time Audio Insights - Latency Tracker & Profiler
Instruments end-to-end latency:
Audio Received -> ASR Streaming -> Signal Extraction -> Nudge Generation -> Web Delivery.
Computes P50, P90, P95, and P99 percentiles across streaming call sessions.
"""

import numpy as np
from typing import List, Dict, Any
from .models import LatencyReport

class LatencyTracker:
    """
    Granular latency profiler across the 4 stages of the real-time audio nudge pipeline.
    """

    def __init__(self):
        self.records: List[LatencyReport] = []

    def record_latencies(self, chunk_id: str, asr_ms: float, signal_ms: float, nudge_ms: float, delivery_ms: float) -> LatencyReport:
        total = round(asr_ms + signal_ms + nudge_ms + delivery_ms, 2)
        report = LatencyReport(
            chunk_id=chunk_id,
            asr_ms=round(asr_ms, 2),
            signal_ms=round(signal_ms, 2),
            nudge_ms=round(nudge_ms, 2),
            delivery_ms=round(delivery_ms, 2),
            total_e2e_ms=total
        )
        self.records.append(report)
        return report

    def compute_summary_statistics(self) -> Dict[str, Any]:
        if not self.records:
            return {"status": "No latency records recorded"}

        def get_stats(vals: List[float]):
            arr = np.array(vals)
            return {
                "mean": round(float(np.mean(arr)), 2),
                "p50": round(float(np.percentile(arr, 50)), 2),
                "p90": round(float(np.percentile(arr, 90)), 2),
                "p95": round(float(np.percentile(arr, 95)), 2),
                "p99": round(float(np.percentile(arr, 99)), 2),
                "max": round(float(np.max(arr)), 2)
            }

        asr_vals = [r.asr_ms for r in self.records]
        sig_vals = [r.signal_ms for r in self.records]
        ndg_vals = [r.nudge_ms for r in self.records]
        deliv_vals = [r.delivery_ms for r in self.records]
        total_vals = [r.total_e2e_ms for r in self.records]

        return {
            "total_chunks_processed": len(self.records),
            "stages": {
                "asr_streaming_latency": get_stats(asr_vals),
                "signal_extraction_latency": get_stats(sig_vals),
                "nudge_generation_latency": get_stats(ndg_vals),
                "ui_delivery_latency": get_stats(deliv_vals)
            },
            "end_to_end_latency": get_stats(total_vals)
        }
