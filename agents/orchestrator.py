import json
import uuid
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from .examiner import Examiner
from .devil_advocate import DevilAdvocate
from .verdict_manager_insights import VerdictManagerInsights

class SessionOrchestrator:
    """Wires Examiner → Devil's Advocate → Verdict into a live assessment session."""

    MAX_ROUNDS = 5

    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.examiner = Examiner()
        self.devil_advocate = DevilAdvocate()
        self.verdict = VerdictManagerInsights()
        self.transcript = []
        self.events = []
        self.started_at = datetime.utcnow().isoformat()

    def _emit(self, event_type: str, data: dict):
        event = {
            "session_id": self.session_id,
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        self.events.append(event)
        return event

    async def start_session(self, role: str, cert_id: str, employee_id: str = None, confidence: str = "50%") -> AsyncGenerator[dict, None]:
        """Run the full assessment session, yielding events as they happen."""

        yield self._emit("session_start", {
            "session_id": self.session_id,
            "role": role,
            "cert_id": cert_id,
            "employee_id": employee_id
        })

        yield self._emit("status", {"agent": "Examiner", "status": "retrieving_knowledge"})

        opening = self.examiner.open_session(role, cert_id, confidence)
        if "error" in opening:
            yield self._emit("error", {"agent": "Examiner", "detail": opening["error"]})
            return

        yield self._emit("question", {
            "agent": "Examiner",
            "content": opening.get("question", ""),
            "citation": opening.get("citation"),
            "difficulty": opening.get("difficulty_level", 1),
            "round": 1
        })

        self.transcript.append({
            "role": "examiner",
            "content": opening.get("question", ""),
            "round": 1
        })

        for round_num in range(1, self.MAX_ROUNDS + 1):
            yield self._emit("status", {"agent": "System", "status": f"awaiting_answer_round_{round_num}"})

            user_answer = yield self._emit("await_answer", {"round": round_num})

            if not user_answer or user_answer.get("type") == "end_session":
                break

            answer_text = user_answer.get("content", "")
            self.transcript.append({
                "role": "employee",
                "content": answer_text,
                "round": round_num
            })

            yield self._emit("answer_received", {
                "agent": "Employee",
                "content": answer_text,
                "round": round_num
            })

            if round_num < self.MAX_ROUNDS:
                yield self._emit("status", {"agent": "DevilAdvocate", "status": "analyzing_answer"})

                quality = self._assess_answer_quality(answer_text)
                challenge = self.devil_advocate.challenge(cert_id, opening.get("question", ""), answer_text, quality)

                if "error" not in challenge:
                    yield self._emit("challenge", {
                        "agent": "Devil's Advocate",
                        "content": challenge.get("counter_argument", ""),
                        "citation": challenge.get("citation"),
                        "challenge_type": challenge.get("challenge_type", ""),
                        "round": round_num
                    })

                    self.transcript.append({
                        "role": "devil_advocate",
                        "content": challenge.get("counter_argument", ""),
                        "round": round_num
                    })

                yield self._emit("status", {"agent": "Examiner", "status": "generating_next_question"})

                follow_up = self.examiner.ask_follow_up(role, cert_id, answer_text, opening.get("question", ""))
                if "error" not in follow_up:
                    opening = follow_up
                    yield self._emit("question", {
                        "agent": "Examiner",
                        "content": follow_up.get("question", ""),
                        "citation": follow_up.get("citation"),
                        "difficulty": follow_up.get("difficulty_level", 1),
                        "round": round_num + 1
                    })

                    self.transcript.append({
                        "role": "examiner",
                        "content": follow_up.get("question", ""),
                        "round": round_num + 1
                    })

        yield self._emit("status", {"agent": "Verdict", "status": "generating_report"})

        self_rated = int(confidence.replace("%", "")) if "%" in confidence else 50
        report = self.verdict.generate_report(self.transcript, self_rated, cert_id, employee_id)

        if "error" in report:
            yield self._emit("error", {"agent": "Verdict", "detail": report["error"]})
        else:
            yield self._emit("report", {
                "individual_report": report.get("individual_report", {}),
                "manager_insights": report.get("manager_insights", {}),
                "reasoning": report.get("reasoning", "")
            })

        yield self._emit("session_end", {
            "session_id": self.session_id,
            "total_rounds": len(self.transcript),
            "duration": datetime.utcnow().isoformat()
        })

    def _assess_answer_quality(self, answer: str) -> str:
        if len(answer) < 20:
            return "weak"
        elif len(answer) > 100 and any(kw in answer.lower() for kw in ["because", "therefore", "however", "depends"]):
            return "strong"
        return "medium"

    def get_full_report(self) -> dict:
        self_rated = 50
        report = self.verdict.generate_report(self.transcript, self_rated, "AZ-104")
        return {
            "session_id": self.session_id,
            "transcript": self.transcript,
            "events": self.events,
            "report": report,
            "started_at": self.started_at,
            "ended_at": datetime.utcnow().isoformat()
        }
