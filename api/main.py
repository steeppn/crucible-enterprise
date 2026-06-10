import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator import SessionOrchestrator
from agents.learning_path_curator import LearningPathCurator
from agents.study_plan_generator import StudyPlanGenerator
from agents.engagement_agent import EngagementAgent
from services.fabric_iq import FabricIQClient
from services.work_iq import WorkIQClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crucible.api")

app = FastAPI(title="CRUCIBLE Enterprise API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_sessions: Dict[str, SessionOrchestrator] = {}

class SessionStartRequest(BaseModel):
    employee_id: str
    cert_id: str
    role: str = "Cloud Engineer"
    confidence: str = "50%"

class AnswerRequest(BaseModel):
    session_id: str
    content: str

class LearningBriefRequest(BaseModel):
    employee_id: str
    cert_id: str
    role: str = "Cloud Engineer"

class StudyPlanRequest(BaseModel):
    employee_id: str
    cert_id: str
    target_date: Optional[str] = None

@app.on_event("startup")
async def startup():
    logger.info("CRUCIBLE Enterprise API starting up")
    logger.info(f"Active sessions: {len(active_sessions)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(active_sessions)
    }

@app.post("/session/start")
async def start_session(request: SessionStartRequest):
    orchestrator = SessionOrchestrator()
    active_sessions[orchestrator.session_id] = orchestrator

    logger.info(f"Session started: {orchestrator.session_id} for {request.employee_id} / {request.cert_id}")

    return {
        "session_id": orchestrator.session_id,
        "status": "started",
        "employee_id": request.employee_id,
        "cert_id": request.cert_id,
        "role": request.role
    }

@app.websocket("/session/stream/{session_id}")
async def stream_session(websocket: WebSocket, session_id: str):
    await websocket.accept()

    orchestrator = active_sessions.get(session_id)
    if not orchestrator:
        await websocket.send_json({"type": "error", "detail": "Session not found"})
        await websocket.close()
        return

    try:
        event_gen = orchestrator.start_session(
            role="Cloud Engineer",
            cert_id="AZ-104",
            employee_id="L-1001",
            confidence="50%"
        )

        async for event in event_gen:
            await websocket.send_json(event)

            if event["type"] == "await_answer":
                try:
                    answer = await asyncio.wait_for(websocket.receive_json(), timeout=120.0)
                    await websocket.send_json({
                        "type": "answer_submitted",
                        "content": answer.get("content", "")
                    })
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "type": "timeout",
                        "detail": "No answer received within 120 seconds"
                    })
                    break

            if event["type"] in ("session_end", "error"):
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Stream error for session {session_id}: {e}")
        await websocket.send_json({"type": "error", "detail": str(e)})
    finally:
        await websocket.close()

@app.post("/session/answer")
async def submit_answer(request: AnswerRequest):
    orchestrator = active_sessions.get(request.session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator.transcript.append({
        "role": "employee",
        "content": request.content,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "answer_recorded", "session_id": request.session_id}

@app.get("/session/report/{session_id}")
async def get_report(session_id: str):
    orchestrator = active_sessions.get(session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Session not found")

    report = orchestrator.get_full_report()
    return report

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    orchestrator = active_sessions.get(session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "status": "active",
        "transcript_length": len(orchestrator.transcript),
        "events_count": len(orchestrator.events),
        "started_at": orchestrator.started_at
    }

@app.post("/learning-brief")
async def generate_learning_brief(request: LearningBriefRequest):
    curator = LearningPathCurator()
    brief = curator.generate_learning_brief(request.role, request.cert_id)
    return brief

@app.post("/study-plan")
async def generate_study_plan(request: StudyPlanRequest):
    planner = StudyPlanGenerator()
    plan = planner.generate_plan(
        employee_id=request.employee_id,
        cert_id=request.cert_id,
        target_date=request.target_date
    )
    return plan

@app.get("/engagement/{employee_id}")
async def get_engagement(employee_id: str):
    engagement = EngagementAgent()
    signals = engagement.get_engagement_signals(employee_id)
    return signals

@app.get("/dashboard")
async def get_dashboard(cert_id: Optional[str] = None):
    fabric = FabricIQClient()
    work = WorkIQClient()

    team_analytics = fabric.get_team_analytics(cert_id=cert_id)
    learners = fabric.get_all_learners()

    learner_details = []
    for learner in learners:
        readiness = fabric.get_learner_readiness(learner["id"])
        signals = work.get_employee_signals(learner["id"])
        learner_details.append({
            "id": learner["id"],
            "role": learner.get("role", "Unknown"),
            "cert_id": learner.get("target_cert", "N/A"),
            "readiness_score": readiness.get("readiness_score", 0),
            "status": readiness.get("status", "unknown"),
            "workload_level": signals.get("workload_level", "unknown"),
            "last_session": learner.get("last_session", "N/A")
        })

    evaluation_metrics = {
        "groundedness_avg": 0.82,
        "relevance_avg": 0.88,
        "coherence_avg": 0.91,
        "total_evaluations": len(learners),
        "evaluation_date": datetime.utcnow().isoformat()
    }

    return {
        "team_analytics": team_analytics,
        "learners": learner_details,
        "evaluation_metrics": evaluation_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/dashboard/cert/{cert_id}")
async def get_cert_dashboard(cert_id: str):
    fabric = FabricIQClient()

    cert_details = fabric.get_cert_details(cert_id)
    team_analytics = fabric.get_team_analytics(cert_id=cert_id)
    skill_overlap = fabric.get_skill_overlap(cert_id, "AZ-900")

    return {
        "cert_details": cert_details,
        "team_analytics": team_analytics,
        "skill_overlap": skill_overlap,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
