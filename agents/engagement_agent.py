import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Engagement Agent in CRUCIBLE Enterprise.

Your role: Keep learners progressing by adapting study reminders and session recommendations to their actual work rhythm. You draw on work context signals to avoid scheduling study sessions during peak meeting periods.

BEHAVIOUR RULES:
- Analyze the employee's meeting load and focus hours
- Recommend study windows that align with their preferred learning slot
- Avoid suggesting study during high-meeting periods (>15 hrs/week)
- Prioritize focus-heavy time blocks
- Keep recommendations supportive, not demanding
- Adapt reminder timing to their work patterns
- If the employee is behind schedule, suggest a catch-up plan without being punitive

OUTPUT FORMAT:
Return a JSON object with:
- "study_windows": [
    {
      "day": string,
      "time_slot": string,
      "duration_minutes": number,
      "topic": string,
      "rationale": string
    }
  ]
- "reminder_schedule": {
    "frequency": string (e.g., "daily", "every other day"),
    "preferred_time": string,
    "message_tone": string (e.g., "supportive", "urgent", "encouraging")
  }
- "workload_assessment": string (one-line assessment of their capacity this week)
- "recommendations": [list of 2-3 one-line tips]

Return valid JSON only — no markdown, no explanation outside the JSON.
"""

class EngagementAgent(BaseAgent):
    """Agent 3: Work-context-aware study reminders and session scheduling."""

    def __init__(self):
        super().__init__(agent_name="EngagementAgent", model_type="primary")
        self.synthetic_data = self._load_synthetic_data()

    def _load_synthetic_data(self) -> dict:
        data = {}
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                key = filename.replace(".json", "")
                with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
                    data[key] = json.load(f)
        return data

    def generate_engagement(self, employee_id: str, study_plan: dict, progress: dict = None) -> dict:
        self._log_step("generate_engagement", f"Creating engagement plan for employee={employee_id}")

        work_signals = self.synthetic_data.get("work_activity_signals", [])
        employee_signal = None
        for signal in work_signals:
            if signal.get("employee_id") == employee_id:
                employee_signal = signal
                break

        if not employee_signal and work_signals:
            employee_signal = work_signals[0]

        progress_info = json.dumps(progress) if progress else "No progress data available — assume starting fresh"

        user_prompt = f"""EMPLOYEE WORK SIGNALS:
{json.dumps(employee_signal, indent=2)}

STUDY PLAN:
{json.dumps(study_plan, indent=2)}

CURRENT PROGRESS:
{progress_info}

Generate an engagement plan that:
1. Recommends specific study windows aligned with their work rhythm
2. Sets a reminder schedule that respects their meeting load
3. Assesses their capacity for this week
4. Provides supportive recommendations

Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)

        try:
            result = json.loads(response)
            self._log_step("engagement_complete", f"Generated {len(result.get('study_windows', []))} study windows")
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse engagement response")
            return {"error": "Failed to generate engagement plan", "raw_response": response}

if __name__ == "__main__":
    engagement = EngagementAgent()
    mock_plan = {
        "study_plan": {
            "certification": "AZ-104",
            "total_recommended_hours": 40,
            "estimated_weeks": 4,
            "milestones": [
                {"milestone_number": 1, "topic": "Identity & Governance", "estimated_hours": 8, "week": 1}
            ]
        }
    }
    result = engagement.generate_engagement("EMP-001", mock_plan)
    print(json.dumps(result, indent=2))
