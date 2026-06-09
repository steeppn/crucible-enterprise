import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Learning Path Curator in CRUCIBLE Enterprise, a certification readiness system.

Your role: Map an employee's role and target certification to relevant skills and approved learning resources.

You are grounded in the organisation's knowledge base. You must cite source material — never provide unsupported free-text recommendations.

Given:
- Employee role (e.g., Cloud Engineer, Network Engineer, DevOps Engineer)
- Target certification (e.g., AZ-900, AZ-104, AZ-204, AZ-400, AZ-700)

Output a structured JSON object with:
- "learning_brief": {
    "role": string,
    "certification": string,
    "cert_name": string,
    "skill_domains": [list of skill domain names from the cert guide],
    "recommended_hours": number,
    "prerequisites": [list of prerequisite cert IDs],
    "difficulty": string
  }
- "citations": [list of citation objects with source and content]
- "reasoning": string (one-line explanation of the learning path)

Rules:
- Only recommend skills and resources that exist in the provided knowledge base
- Include the passing score and recommended study hours from the cert guide
- If prerequisites exist, list them clearly
- Return valid JSON only — no markdown, no explanation outside the JSON
"""

class LearningPathCurator(BaseAgent):
    """Agent 1: Maps employee role + target cert to skills and approved learning resources."""

    def __init__(self):
        super().__init__(agent_name="LearningPathCurator", model_type="primary")
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        kb = {}
        kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
        for filename in os.listdir(kb_dir):
            if filename.endswith(".md"):
                cert_id = filename.replace("_guide.md", "").upper()
                with open(os.path.join(kb_dir, filename), "r", encoding="utf-8") as f:
                    kb[cert_id] = f.read()
        return kb

    def generate_learning_brief(self, role: str, certification: str) -> dict:
        self._log_step("start", f"Generating learning brief for role={role}, cert={certification}")

        cert_id = certification.upper().replace("-", "")
        if cert_id not in self.knowledge_base:
            self._log_step("error", f"Certification {certification} not found in knowledge base")
            return {
                "error": f"Certification {certification} not found in knowledge base",
                "available_certs": list(self.knowledge_base.keys())
            }

        kb_content = self.knowledge_base[cert_id]

        user_prompt = f"""Role: {role}
Target Certification: {certification}

Knowledge Base Content for {certification}:
{kb_content}

Generate the learning brief as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)

        try:
            result = json.loads(response)
            result["citations"] = [
                self._format_citation(f"{certification}_guide.md", kb_content[:500])
            ]
            self._log_step("complete", f"Learning brief generated with {len(result.get('learning_brief', {}).get('skill_domains', []))} skill domains")
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse model response as JSON")
            return {"error": "Failed to parse learning brief", "raw_response": response}

if __name__ == "__main__":
    curator = LearningPathCurator()
    brief = curator.generate_learning_brief("Cloud Engineer", "AZ-104")
    print(json.dumps(brief, indent=2))
    print("\nReasoning Trace:")
    for step in curator.get_reasoning_trace():
        print(f"  [{step['timestamp']}] {step['step']}: {step['detail']}")
