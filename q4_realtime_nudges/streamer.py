"""
Question 4: Real-Time Audio Streamer & Playback Simulator
Simulates or streams continuous call audio chunks in chronological order,
attaching speaker channel diarization and measuring realistic network/ASR jitter.
"""

import asyncio
import random
from typing import List, AsyncGenerator, Tuple
from .models import AudioChunk, Speaker

class CallAudioStreamer:
    """
    Streams call audio chunks sequentially. Supports both simulated real-time mode
    (with sleep intervals) and batch benchmark mode.
    """

    def __init__(self, simulate_realtime_delay: bool = False):
        self.simulate_realtime_delay = simulate_realtime_delay

    async def stream_call(self, call_chunks: List[Tuple[Speaker, str, int]]) -> AsyncGenerator[AudioChunk, None]:
        """
        Yields AudioChunk objects with realistic millisecond timing offsets.
        Tuple format: (Speaker, text, duration_ms)
        """
        cumulative_offset_ms = 0

        for idx, (speaker, utterance, dur_ms) in enumerate(call_chunks):
            if self.simulate_realtime_delay:
                # Sleep proportional to chunk length / 4 to demonstrate real-time streaming without taking 5 minutes
                await asyncio.sleep(dur_ms / 4000.0)

            chunk = AudioChunk(
                chunk_id=f"chk_{idx:03d}",
                chunk_index=idx,
                speaker=speaker,
                text=utterance,
                duration_ms=dur_ms,
                timestamp_offset_ms=cumulative_offset_ms
            )
            cumulative_offset_ms += dur_ms
            yield chunk
