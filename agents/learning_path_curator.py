import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Learning Path Curator in CRUCIBLE Enterprise, a certification readiness system.

Your role: Map an employee's role and target certification to relevant skills and approved learning resources.

You are grounded in the organisation's knowledge base (Foundry IQ) and can supplement with Microsoft Learn documentation (MCP). You must cite source material — never provide unsupported free-text recommendations.

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

    def generate_learning_brief(self, role: str, certification: str) -> dict:
        self._log_step("start", f"Generating learning brief for role={role}, cert={certification}")

        foundry_results = self._retrieve_knowledge(certification, cert_id=certification, top_k=3)
        mcp_results = self._retrieve_mcp_docs(f"{certification} Microsoft certification objectives", top_k=3)

        foundry_context = self._format_retrieval_context(foundry_results, "Foundry IQ")
        mcp_context = self._format_retrieval_context(mcp_results, "Microsoft Learn MCP")

        role_mapping = self._get_role_mapping(role)
        cert_details = self._get_cert_details(certification)

        user_prompt = f"""Role: {role}
Target Certification: {certification}

ROLE-TO-CERT MAPPING (Fabric IQ):
{json.dumps(role_mapping, indent=2)}

CERTIFICATION DETAILS (Fabric IQ):
{json.dumps(cert_details, indent=2) if cert_details else "Not found in ontology"}

{foundry_context}

{mcp_context}

Generate the learning brief as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)

        try:
            result = json.loads(response)
            citations = []
            for r in foundry_results:
                citations.append(self._format_citation(
                    f"Foundry IQ: {r.get('source_file', 'unknown')}",
                    r.get("content", "")[:200]
                ))
            for r in mcp_results:
                if r.get("url"):
                    citations.append(self._format_citation(
                        f"Microsoft Learn MCP: {r.get('title', 'unknown')}",
                        r.get("summary", r.get("content", ""))[:200]
                    ))
            result["citations"] = citations
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
