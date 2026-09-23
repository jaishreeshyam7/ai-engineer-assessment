"""
Main Application Server: Fast-API Web Portal for AI Engineer Assessment
Provides interactive web calling UI, KB explorer, multilingual bot simulator,
and real-time live call nudge HUD.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import question packages
from q2_knowledge_base.retriever import KnowledgeBaseEngine
from q2_knowledge_base.benchmark_test import run_benchmark as run_q2_benchmark
from q1_voice_agent.voice_agent import GroundedVoiceAgent
from q1_voice_agent.crm_actions import crm_service
from q3_multilingual_bots.philippines_bot import PhilippinesVoiceBot, PH_LOCALIZATION_SHOWCASE
from q3_multilingual_bots.indonesia_bot import IndonesiaVoiceBot, ID_LOCALIZATION_SHOWCASE
from q3_multilingual_bots.asr_tts_analysis import ASR_EVALUATIONS, TTS_EVALUATIONS
from q4_realtime_nudges.benchmark_nudges import TEST_AUDIO_STREAMS
from q4_realtime_nudges.streamer import CallAudioStreamer
from q4_realtime_nudges.signal_extractor import SignalExtractor
from q4_realtime_nudges.nudge_controller import NudgeController
from q4_realtime_nudges.latency_tracker import LatencyTracker

app = FastAPI(title="AI Engineer Assessment - Production Suite")

# Mount static and templates
os.makedirs("web/static", exist_ok=True)
os.makedirs("web/templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="web/templates")

# Initialize shared engines
kb_engine = KnowledgeBaseEngine()
voice_agent = GroundedVoiceAgent(kb_engine=kb_engine)
ph_bot = PhilippinesVoiceBot()
id_bot = IndonesiaVoiceBot()

# In-memory web sessions
web_call_sessions: Dict[str, Any] = {}
web_ph_sessions: Dict[str, Any] = {}
web_id_sessions: Dict[str, Any] = {}

# ----------------- WEB PAGES -----------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# ----------------- QUESTION 1 API -----------------
class CallTurnRequest(BaseModel):
    session_id: str
    message: str
    caller_phone: Optional[str] = "+1-555-010-9988"

@app.post("/api/q1/turn")
async def handle_q1_turn(req: CallTurnRequest):
    session = voice_agent.get_or_create_session(session_id=req.session_id, phone=req.caller_phone)
    result = voice_agent.process_turn(session, req.message)
    return {
        "agent_response": result["response"],
        "action": result.get("action"),
        "citation": result.get("citation"),
        "is_grounded": result.get("is_grounded", True),
        "stage": session.stage.value,
        "customer_name": session.customer_name,
        "age": session.age,
        "pre_existing": session.pre_existing_conditions,
        "budget": session.budget_range,
        "lead_id": session.crm_lead_id,
        "qualification": session.qualification_result,
        "is_escalated": session.is_escalated
    }

@app.post("/api/q1/reset")
async def reset_q1_session(req: Dict[str, str]):
    sid = req.get("session_id", "web_default")
    if sid in voice_agent.sessions:
        del voice_agent.sessions[sid]
    return {"status": "reset", "session_id": sid}

@app.get("/api/q1/leads")
async def list_leads():
    return {"leads": [l.model_dump() for l in crm_service.leads_db.values()], "escalations": [e.model_dump() for e in crm_service.escalations_db.values()]}

# ----------------- QUESTION 2 API -----------------
@app.get("/api/q2/search")
async def search_kb(q: str):
    res = kb_engine.answer_query(q)
    return res

@app.get("/api/q2/benchmark")
async def get_q2_benchmark():
    benchmark_report = run_q2_benchmark()
    return {"results": benchmark_report}

# ----------------- QUESTION 3 API -----------------
class MultilingualChatRequest(BaseModel):
    market: str  # "PH" or "ID"
    session_id: str
    message: str

@app.post("/api/q3/chat")
async def handle_q3_chat(req: MultilingualChatRequest):
    if req.market.upper() == "PH":
        state = web_ph_sessions.setdefault(req.session_id, {"stage": "GREETING"})
        res = ph_bot.process_turn(state, req.message)
    else:
        state = web_id_sessions.setdefault(req.session_id, {"stage": "GREETING"})
        res = id_bot.process_turn(state, req.message)
    return res

@app.get("/api/q3/showcase")
async def get_q3_showcase():
    return {
        "philippines": [ex.model_dump() for ex in PH_LOCALIZATION_SHOWCASE],
        "indonesia": [ex.model_dump() for ex in ID_LOCALIZATION_SHOWCASE],
        "asr_evaluations": [e.model_dump() for e in ASR_EVALUATIONS],
        "tts_evaluations": [e.model_dump() for e in TTS_EVALUATIONS]
    }

# ----------------- QUESTION 4 API & WEBSOCKET -----------------
@app.get("/api/q4/streams")
async def get_q4_streams():
    return [{"id": s["stream_id"], "name": s["scenario_name"], "desc": s["description"]} for s in TEST_AUDIO_STREAMS]

@app.websocket("/ws/q4/stream/{stream_id}")
async def stream_q4_call(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    stream_meta = next((s for s in TEST_AUDIO_STREAMS if s["stream_id"] == stream_id), None)
    if not stream_meta:
        await websocket.send_json({"error": "Stream not found"})
        await websocket.close()
        return

    streamer = CallAudioStreamer(simulate_realtime_delay=True)
    extractor = SignalExtractor()
    controller = NudgeController()
    tracker = LatencyTracker()

    try:
        async for chunk in streamer.stream_call(stream_meta["chunks"]):
            # Simulate realistic ASR/processing latencies
            import random
            asr_lat = random.uniform(140.0, 210.0)
            sig_lat = random.uniform(18.0, 42.0)
            signals = extractor.extract_signals(chunk)
            
            nudge_lat = 0.0
            deliv_lat = random.uniform(4.0, 10.0)
            fired_nudge = None

            if signals:
                for sig in signals:
                    nudge_lat += random.uniform(25.0, 55.0)
                    nudge = controller.evaluate_signal(sig)
                    if nudge:
                        fired_nudge = nudge

            lat_rep = tracker.record_latencies(
                chunk_id=chunk.chunk_id,
                asr_ms=asr_lat,
                signal_ms=sig_lat,
                nudge_ms=nudge_lat,
                delivery_ms=deliv_lat
            )

            payload = {
                "type": "CHUNK",
                "chunk": chunk.model_dump(),
                "nudge": fired_nudge.model_dump() if fired_nudge else None,
                "latency": lat_rep.model_dump()
            }
            await websocket.send_json(payload)
            await asyncio.sleep(1.2)  # Paced real-time viewing

        summary = tracker.compute_summary_statistics()
        quality = controller.get_false_positive_analysis()
        await websocket.send_json({
            "type": "SUMMARY",
            "latency_summary": summary,
            "quality_summary": quality
        })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8050))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
