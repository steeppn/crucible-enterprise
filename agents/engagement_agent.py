import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Engagement Agent in CRUCIBLE Enterprise.

Your role: Keep learners progressing by adapting study reminders and session recommendations to their actual work rhythm. You draw on Work IQ signals to avoid scheduling study sessions during peak meeting periods and to personalize engagement based on individual work patterns.

BEHAVIOUR RULES:
- Analyze the employee's meeting load and focus hours from Work IQ
- Recommend study windows that align with their preferred learning slot
- Avoid suggesting study during high-meeting periods (>20 hrs/week)
- Prioritize focus-heavy time blocks
- Keep recommendations supportive, not demanding
- Adapt reminder timing to their work patterns
- If the employee is behind schedule, suggest a catch-up plan without being punitive
- Consider stress indicators when setting engagement tone

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

    def generate_engagement(self, employee_id: str, study_plan: dict, progress: dict = None) -> dict:
        self._log_step("generate_engagement", f"Creating engagement plan for employee={employee_id}")

        work_signals = self._get_employee_signals(employee_id)
        available_slots = self._get_available_slots(employee_id, hours_needed=2)
        work_pattern = self._get_work_iq().get_work_pattern_summary(employee_id)

        progress_info = json.dumps(progress) if progress else "No progress data available — assume starting fresh"

        user_prompt = f"""EMPLOYEE WORK SIGNALS (Work IQ):
{json.dumps(work_signals, indent=2)}

AVAILABLE STUDY SLOTS (Work IQ):
{json.dumps(available_slots[:5], indent=2)}

WORK PATTERN SUMMARY (Work IQ):
{json.dumps(work_pattern, indent=2)}

STUDY PLAN:
{json.dumps(study_plan, indent=2)}

CURRENT PROGRESS:
{progress_info}

Generate an engagement plan that:
1. Recommends specific study windows aligned with their work rhythm
2. Sets a reminder schedule that respects their meeting load
3. Assesses their capacity for this week
4. Provides supportive recommendations
5. Accounts for stress indicators and workload level

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
