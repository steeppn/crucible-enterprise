import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("crucible.services.work_iq")

class WorkIQClient:
    """Simulated Work IQ client for Microsoft 365 work context signals.
    
    In production, this would connect to Microsoft Graph API via Foundry's
    Work IQ integration (A2A protocol). For the hackathon demo, it simulates
    Graph API responses using synthetic data structured as real payloads.
    
    This layer enables agents to reason over:
    - Meeting load and focus time patterns
    - Calendar availability for study scheduling
    - Team capacity signals for manager insights
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data"
            )
        self._data = self._load_data(data_dir)
        self._calendar_cache = {}

    def _load_data(self, data_dir: str) -> dict:
        """Load synthetic work activity signals."""
        signals_file = os.path.join(data_dir, "work_activity_signals.json")
        calendar_file = os.path.join(data_dir, "work_calendar_events.json")
        
        data = {}
        if os.path.exists(signals_file):
            with open(signals_file, "r") as f:
                data["signals"] = json.load(f)
        else:
            data["signals"] = []
            logger.warning("work_activity_signals.json not found")

        if os.path.exists(calendar_file):
            with open(calendar_file, "r") as f:
                data["calendar"] = json.load(f)
        else:
            data["calendar"] = []

        return data

    def _find_employee(self, employee_id: str) -> Optional[dict]:
        """Find employee signals by ID."""
        for emp in self._data["signals"]:
            if emp.get("employee_id") == employee_id:
                return emp
        return None

    # ── Employee Work Signals ─────────────────────────────────────────

    def get_employee_signals(self, employee_id: str) -> dict:
        """Get work context signals for an employee.
        
        Simulates Graph API /users/{id}/insights response.
        """
        employee = self._find_employee(employee_id)
        if not employee:
            return {
                "employee_id": employee_id,
                "meeting_hours_per_week": 15,
                "focus_hours_per_week": 15,
                "preferred_learning_slot": "Afternoon",
                "workload_level": "moderate",
                "stress_indicators": [],
                "collaboration_score": 0.7
            }

        meeting_hours = employee.get("meeting_hours_per_week", 15)
        focus_hours = employee.get("focus_hours_per_week", 15)
        
        workload_level = "light"
        if meeting_hours > 20:
            workload_level = "heavy"
        elif meeting_hours > 12:
            workload_level = "moderate"

        stress_indicators = []
        if meeting_hours > 25:
            stress_indicators.append("high_meeting_load")
        if focus_hours < 8:
            stress_indicators.append("low_focus_time")
        if employee.get("preferred_learning_slot") == "Evening":
            stress_indicators.append("after_hours_learning")

        return {
            "employee_id": employee_id,
            "meeting_hours_per_week": meeting_hours,
            "focus_hours_per_week": focus_hours,
            "preferred_learning_slot": employee.get("preferred_learning_slot", "Afternoon"),
            "workload_level": workload_level,
            "stress_indicators": stress_indicators,
            "collaboration_score": round(1.0 - (meeting_hours / 40), 2)
        }

    def get_available_slots(
        self,
        employee_id: str,
        week_start: str = None,
        hours_needed: int = 2
    ) -> list:
        """Get available study time slots for an employee.
        
        Simulates Graph API calendar free/busy query.
        Returns optimal study windows based on work patterns.
        """
        if week_start is None:
            week_start = datetime.now().strftime("%Y-%m-%d")

        employee = self._find_employee(employee_id)
        if not employee:
            employee = {
                "meeting_hours_per_week": 15,
                "focus_hours_per_week": 15,
                "preferred_learning_slot": "Afternoon"
            }

        preferred = employee.get("preferred_learning_slot", "Afternoon")
        focus_hours = employee.get("focus_hours_per_week", 15)
        meeting_hours = employee.get("meeting_hours_per_week", 15)

        slot_definitions = {
            "Morning": [
                {"start": "07:00", "end": "08:30", "quality": "high" if focus_hours > 15 else "medium"},
                {"start": "08:30", "end": "09:00", "quality": "medium"}
            ],
            "Afternoon": [
                {"start": "13:00", "end": "15:00", "quality": "high" if focus_hours > 12 else "medium"},
                {"start": "15:00", "end": "16:00", "quality": "medium"}
            ],
            "Evening": [
                {"start": "18:00", "end": "20:00", "quality": "high" if meeting_hours > 20 else "medium"},
                {"start": "20:00", "end": "21:00", "quality": "low"}
            ]
        }

        slots = []
        base_date = datetime.strptime(week_start, "%Y-%m-%d")
        
        for day_offset in range(5):
            current_date = base_date + timedelta(days=day_offset)
            date_str = current_date.strftime("%Y-%m-%d")
            
            for slot in slot_definitions.get(preferred, slot_definitions["Afternoon"]):
                if meeting_hours > 25 and slot["quality"] == "high":
                    continue
                    
                slots.append({
                    "date": date_str,
                    "start": slot["start"],
                    "end": slot["end"],
                    "quality": slot["quality"],
                    "employee_id": employee_id,
                    "conflicts": self._check_conflicts(employee_id, date_str, slot["start"], slot["end"])
                })

        slots.sort(key=lambda s: (
            0 if s["quality"] == "high" else 1 if s["quality"] == "medium" else 2,
            s["date"]
        ))

        return slots[:10]

    def _check_conflicts(self, employee_id: str, date: str, start: str, end: str) -> list:
        """Check for calendar conflicts in a time slot."""
        conflicts = []
        for event in self._data.get("calendar", []):
            if event.get("employee_id") != employee_id:
                continue
            if event.get("date") != date:
                continue
            
            event_start = event.get("start", "00:00")
            event_end = event.get("end", "00:00")
            
            if start < event_end and end > event_start:
                conflicts.append({
                    "title": event.get("title", "Meeting"),
                    "start": event_start,
                    "end": event_end
                })

        return conflicts

    def get_team_capacity(self, employee_ids: list) -> dict:
        """Get aggregated team capacity signals.
        
        Simulates aggregated Graph API insights for manager view.
        """
        if not employee_ids:
            employee_ids = [emp.get("employee_id") for emp in self._data["signals"]]

        team_signals = []
        for emp_id in employee_ids:
            signals = self.get_employee_signals(emp_id)
            team_signals.append(signals)

        if not team_signals:
            return {
                "team_size": 0,
                "avg_meeting_hours": 0,
                "avg_focus_hours": 0,
                "capacity_level": "unknown",
                "at_risk_count": 0
            }

        avg_meeting = sum(s["meeting_hours_per_week"] for s in team_signals) / len(team_signals)
        avg_focus = sum(s["focus_hours_per_week"] for s in team_signals) / len(team_signals)
        
        at_risk = sum(1 for s in team_signals if s["workload_level"] == "heavy")
        
        capacity_level = "high"
        if avg_meeting > 20:
            capacity_level = "constrained"
        elif avg_meeting > 15:
            capacity_level = "moderate"

        return {
            "team_size": len(team_signals),
            "avg_meeting_hours": round(avg_meeting, 1),
            "avg_focus_hours": round(avg_focus, 1),
            "capacity_level": capacity_level,
            "at_risk_count": at_risk,
            "preferred_slots": self._aggregate_preferred_slots(team_signals)
        }

    def _aggregate_preferred_slots(self, signals: list) -> dict:
        """Aggregate preferred learning slots across team."""
        slot_counts = {}
        for s in signals:
            slot = s.get("preferred_learning_slot", "Afternoon")
            slot_counts[slot] = slot_counts.get(slot, 0) + 1
        
        return dict(sorted(slot_counts.items(), key=lambda x: x[1], reverse=True))

    def get_work_pattern_summary(self, employee_id: str) -> dict:
        """Get a summary of work patterns for engagement personalization."""
        signals = self.get_employee_signals(employee_id)
        slots = self.get_available_slots(employee_id, hours_needed=2)
        
        high_quality_slots = [s for s in slots if s["quality"] == "high"]
        
        return {
            "employee_id": employee_id,
            "workload_level": signals["workload_level"],
            "meeting_load": signals["meeting_hours_per_week"],
            "available_focus_time": signals["focus_hours_per_week"],
            "best_study_windows": high_quality_slots[:3],
            "recommended_reminder_time": self._suggest_reminder_time(signals),
            "stress_risk": len(signals["stress_indicators"]) > 0,
            "stress_factors": signals["stress_indicators"]
        }

    def _suggest_reminder_time(self, signals: dict) -> str:
        """Suggest optimal reminder time based on work patterns."""
        preferred = signals.get("preferred_learning_slot", "Afternoon")
        meeting_hours = signals.get("meeting_hours_per_week", 15)
        
        if preferred == "Morning":
            return "07:30" if meeting_hours < 20 else "06:30"
        elif preferred == "Afternoon":
            return "12:30" if meeting_hours < 20 else "11:30"
        else:
            return "17:30" if meeting_hours < 25 else "18:30"
