import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Study Plan Generator in CRUCIBLE Enterprise.

Your role: Convert a learning brief from the Learning Path Curator into a practical, milestone-based study schedule. You account for the employee's workload (Work IQ), certification prerequisites and skill relationships (Fabric IQ), and available focus windows.

BEHAVIOUR RULES:
- Break the certification into logical study milestones (one per skill domain)
- Allocate study hours based on the certification's recommended hours and the employee's availability
- Sequence milestones based on prerequisites and difficulty progression
- Include assessment checkpoints after each milestone
- Account for the employee's meeting load and focus hours from Work IQ
- Use Fabric IQ ontology to understand skill dependencies and overlap
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

    def generate_plan(self, learning_brief: dict, employee_id: str = None) -> dict:
        self._log_step("generate_plan", f"Creating study plan for cert={learning_brief.get('certification', 'unknown')}")

        work_signals = self._get_employee_signals(employee_id) if employee_id else {
            "meeting_hours_per_week": 15,
            "focus_hours_per_week": 15,
            "preferred_learning_slot": "Afternoon",
            "workload_level": "moderate"
        }

        available_slots = self._get_available_slots(employee_id, hours_needed=2) if employee_id else []

        cert_id = learning_brief.get("certification", "")
        cert_details = self._get_cert_details(cert_id)
        prerequisites = self._get_fabric_iq().get_cert_prerequisites(cert_id) if cert_details else []

        skill_overlap = {}
        if cert_details and len(cert_details.get("skills", [])) > 1:
            first_skill = cert_details["skills"][0]
            for skill in cert_details["skills"][1:]:
                certs_a = self._get_fabric_iq().get_certs_by_skill(first_skill)
                certs_b = self._get_fabric_iq().get_certs_by_skill(skill)
                shared = set(certs_a) & set(certs_b)
                if shared:
                    skill_overlap[f"{first_skill} ↔ {skill}"] = list(shared)

        user_prompt = f"""LEARNING BRIEF:
{json.dumps(learning_brief, indent=2)}

EMPLOYEE WORK SIGNALS (Work IQ):
{json.dumps(work_signals, indent=2)}

AVAILABLE STUDY SLOTS (Work IQ):
{json.dumps(available_slots[:5], indent=2) if available_slots else "No slots queried"}

CERTIFICATION DETAILS (Fabric IQ):
{json.dumps(cert_details, indent=2) if cert_details else "Not found in ontology"}

PREREQUISITE CHAIN (Fabric IQ):
{json.dumps(prerequisites, indent=2)}

SKILL OVERLAP ANALYSIS (Fabric IQ):
{json.dumps(skill_overlap, indent=2) if skill_overlap else "No significant overlap detected"}

Generate a practical study plan that:
1. Breaks the certification into milestones (one per skill domain)
2. Allocates hours based on the recommended total and employee availability
3. Sequences milestones logically (prerequisites first)
4. Includes assessment checkpoints
5. Produces a realistic weekly schedule
6. Accounts for meeting load and focus windows

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
