import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Verdict and Manager Insights Agent in CRUCIBLE Enterprise.

Your role: Synthesize the full session transcript and reasoning traces to produce an individual readiness report and aggregated manager insights. You use Fabric IQ for semantic analytics over learner data and Work IQ for team capacity signals.

INDIVIDUAL REPORT:
Analyze the full session and produce:
- "readiness_score": number (0-100)
- "exam_recommendation": string (one of: "Ready", "Not Yet", "Needs Review")
- "confidence_calibration": {
    "self_rated": number (0-100),
    "actual_performance": number (0-100),
    "gap": number (self_rated - actual, positive = overconfident)
  }
- "concept_mastery": {
    "topic_name": string (one of: "strong", "shaky", "weak")
  }
- "weak_areas": [
    { "topic": string, "description": string, "next_step": string }
  ]
- "session_summary": string (2-3 sentence summary of performance)

MANAGER INSIGHTS (aggregated, no individual PII):
Produce team-level insights using Fabric IQ analytics and Work IQ capacity signals:
- "team_readiness_by_cert": {
    "cert_id": { "avg_readiness": number, "employee_count": number, "risk_level": string }
  }
- "risk_flags": [
    { "cert_id": string, "risk_type": string, "description": string, "affected_count": number }
  }
- "completion_patterns": {
    "avg_study_hours": number,
    "pass_rate": number,
    "study_hour_correlation": string
  }

OUTPUT FORMAT:
Return a JSON object with:
- "individual_report": { ... }
- "manager_insights": { ... }
- "reasoning": string (one-line explanation of the verdict)

Return valid JSON only — no markdown, no explanation outside the JSON.
"""

class VerdictManagerInsights(BaseAgent):
    """Agent 6: Verifier + Reporting — individual readiness + manager dashboard."""

    def __init__(self):
        super().__init__(agent_name="VerdictManagerInsights", model_type="reasoning")

    def generate_report(self, session_transcript: list, self_rated_confidence: int, certification: str, employee_id: str = None) -> dict:
        self._log_step("generate_report", f"Synthesizing report for cert={certification}, self_rated={self_rated_confidence}")

        transcript_text = "\n".join([
            f"{'Examiner' if e.get('role') == 'examiner' else 'Employee'}: {e.get('content', '')}"
            for e in session_transcript
        ])

        learner_readiness = self._get_learner_readiness(employee_id) if employee_id else {
            "readiness_score": 0,
            "status": "no_data",
            "recommendation": "No learner data available"
        }

        team_analytics = self._get_team_analytics(certification)
        work_capacity = self._get_work_iq().get_team_capacity([employee_id]) if employee_id else {
            "team_size": 0,
            "avg_meeting_hours": 0,
            "avg_focus_hours": 0,
            "capacity_level": "unknown"
        }

        cert_details = self._get_cert_details(certification)

        user_prompt = f"""SESSION TRANSCRIPT:
{transcript_text}

EMPLOYEE'S SELF-RATED CONFIDENCE: {self_rated_confidence}/100
TARGET CERTIFICATION: {certification}

LEARNER READINESS (Fabric IQ):
{json.dumps(learner_readiness, indent=2)}

TEAM ANALYTICS (Fabric IQ):
{json.dumps(team_analytics, indent=2)}

TEAM CAPACITY (Work IQ):
{json.dumps(work_capacity, indent=2)}

CERTIFICATION DETAILS (Fabric IQ):
{json.dumps(cert_details, indent=2) if cert_details else "Not found in ontology"}

Generate the individual readiness report and manager insights as specified in your system prompt.

For the individual report:
- Calculate readiness based on answer quality, depth, and citation accuracy
- Compare self-rated confidence to actual performance
- Identify weak areas from the transcript

For manager insights:
- Aggregate across the synthetic learner data
- Identify risk patterns (e.g., learners with high confidence but low scores)
- Present without individual PII

Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)

        try:
            result = json.loads(response)
            self._log_step("report_complete", f"Readiness score: {result.get('individual_report', {}).get('readiness_score', 'N/A')}, Recommendation: {result.get('individual_report', {}).get('exam_recommendation', 'N/A')}")
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse verdict response")
            return {"error": "Failed to generate report", "raw_response": response}

if __name__ == "__main__":
    verdict = VerdictManagerInsights()
    mock_transcript = [
        {"role": "examiner", "content": "What is the difference between availability sets and availability zones?"},
        {"role": "employee", "content": "Availability sets protect against hardware failures within a datacenter, while availability zones protect across datacenters."},
        {"role": "examiner", "content": "Good. Now explain how many availability zones a typical Azure region has and what happens if one zone goes down."},
        {"role": "employee", "content": "I think most regions have 3 zones. If one goes down, the others keep running. But I'm not sure about the exact SLA."},
    ]
    report = verdict.generate_report(mock_transcript, 70, "AZ-104", "L-1001")
    print(json.dumps(report, indent=2))
