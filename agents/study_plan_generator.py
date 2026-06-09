import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Study Plan Generator in CRUCIBLE Enterprise.

Your role: Convert a learning brief from the Learning Path Curator into a practical, milestone-based study schedule. You account for the employee's workload, available focus windows, and certification prerequisites.

BEHAVIOUR RULES:
- Break the certification into logical study milestones (one per skill domain)
- Allocate study hours based on the certification's recommended hours and the employee's availability
- Sequence milestones based on prerequisites and difficulty progression
- Include assessment checkpoints after each milestone
- Account for the employee's meeting load and focus hours
- Produce a realistic schedule — don't overload any single week

OUTPUT FORMAT:
Return a JSON object with:
- "study_plan": {
    "certification": string,
    "total_recommended_hours": number,
    "estimated_weeks": number,
    "milestones": [
      {
        "milestone_number": number,
        "topic": string,
        "skill_domain": string,
        "estimated_hours": number,
        "week": number,
        "assessment_checkpoint": string,
        "prerequisites": [list of prerequisite milestone numbers]
      }
    ]
  }
- "weekly_schedule": [
    { "week": number, "study_hours": number, "topics": [list of topic names] }
  ]
- "recommendations": [list of 2-3 one-line study tips]

Return valid JSON only — no markdown, no explanation outside the JSON.
"""

class StudyPlanGenerator(BaseAgent):
    """Agent 2: Converts learning brief into practical study schedule."""

    def __init__(self):
        super().__init__(agent_name="StudyPlanGenerator", model_type="reasoning")
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

    def generate_plan(self, learning_brief: dict, employee_id: str = None) -> dict:
        self._log_step("generate_plan", f"Creating study plan for cert={learning_brief.get('certification', 'unknown')}")

        work_signals = self.synthetic_data.get("work_activity_signals", [])
        employee_signal = None
        if employee_id:
            for signal in work_signals:
                if signal.get("employee_id") == employee_id:
                    employee_signal = signal
                    break

        if not employee_signal and work_signals:
            employee_signal = work_signals[0]

        user_prompt = f"""LEARNING BRIEF:
{json.dumps(learning_brief, indent=2)}

EMPLOYEE WORK SIGNALS:
{json.dumps(employee_signal, indent=2) if employee_signal else "No work signals available — assume 15 meeting hours/week, 15 focus hours/week, preferred slot: Afternoon"}

Generate a practical study plan that:
1. Breaks the certification into milestones (one per skill domain)
2. Allocates hours based on the recommended total and employee availability
3. Sequences milestones logically (prerequisites first)
4. Includes assessment checkpoints
5. Produces a realistic weekly schedule

Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)

        try:
            result = json.loads(response)
            self._log_step("plan_complete", f"Study plan generated: {len(result.get('study_plan', {}).get('milestones', []))} milestones over {result.get('study_plan', {}).get('estimated_weeks', '?')} weeks")
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse study plan response")
            return {"error": "Failed to generate study plan", "raw_response": response}

if __name__ == "__main__":
    planner = StudyPlanGenerator()
    mock_brief = {
        "role": "Cloud Engineer",
        "certification": "AZ-104",
        "cert_name": "Microsoft Azure Administrator",
        "skill_domains": ["Identity & Governance", "Storage", "Compute", "Virtual Networking", "Monitoring"],
        "recommended_hours": 40,
        "prerequisites": ["AZ-900"],
        "difficulty": "Associate"
    }
    plan = planner.generate_plan(mock_brief, "EMP-001")
    print(json.dumps(plan, indent=2))
