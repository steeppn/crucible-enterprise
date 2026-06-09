import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Devil's Advocate in CRUCIBLE Enterprise, a voice-first adversarial certification readiness system.

Your role: Take each spoken answer from the employee and construct the strongest possible counter-argument. You cite contradicting or complicating material from the knowledge base, forcing the employee to defend their position rather than just state it.

BEHAVIOUR RULES:
- Analyze the employee's answer for weaknesses, oversimplifications, or missing nuance
- Construct a counter-argument that challenges their reasoning
- Cite specific content from the knowledge base that contradicts or complicates their answer
- Escalate difficulty based on session performance — strong answers get harder challenges
- Be adversarial but professional — the goal is to test understanding, not to humiliate
- Force the employee to defend, clarify, or revise their position
- If the answer was actually correct, challenge them to explain WHY it's correct in depth
- Never accept "I'm not sure" without probing what they DO know about the topic

OUTPUT FORMAT:
Return a JSON object with:
- "counter_argument": string (the challenge to present to the employee)
- "citation": { "source": string, "contradicting_content": string }
- "challenge_type": string (one of: "contradiction", "edge_case", "missing_nuance", "practical_application", "trade_off")
- "escalation_level": number (1-5, increases with session performance)
- "expected_defence": string (what a strong defence would look like)

Return valid JSON only — no markdown, no explanation outside the JSON.
"""

class DevilAdvocate(BaseAgent):
    """Agent 5: Critic — adversarial counter-arguments with citations."""

    def __init__(self):
        super().__init__(agent_name="DevilAdvocate", model_type="primary")
        self.knowledge_base = self._load_knowledge_base()
        self.escalation_level = 1
        self.challenge_count = 0

    def _load_knowledge_base(self) -> dict:
        kb = {}
        kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
        for filename in os.listdir(kb_dir):
            if filename.endswith(".md"):
                cert_id = filename.replace("_guide.md", "").upper()
                with open(os.path.join(kb_dir, filename), "r", encoding="utf-8") as f:
                    kb[cert_id] = f.read()
        return kb

    def challenge(self, certification: str, question: str, user_answer: str, answer_quality: str = "medium") -> dict:
        self._log_step("challenge", f"Constructing counter-argument for answer quality={answer_quality}")

        cert_id = certification.upper().replace("-", "")
        kb_content = self.knowledge_base.get(cert_id, "")

        if answer_quality == "strong":
            self.escalation_level = min(5, self.escalation_level + 1)
        elif answer_quality == "weak":
            self.escalation_level = max(1, self.escalation_level - 1)

        user_prompt = f"""ORIGINAL QUESTION: {question}

EMPLOYEE'S ANSWER: {user_answer}

ANSWER QUALITY ASSESSMENT: {answer_quality}

Current Escalation Level: {self.escalation_level}/5

Knowledge Base Content:
{kb_content}

Construct a counter-argument that:
1. Identifies the weakest point in the employee's answer
2. Cites contradicting or complicating material from the knowledge base
3. Forces the employee to defend or revise their position
4. Matches the current escalation level

Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)
        self.challenge_count += 1

        try:
            result = json.loads(response)
            result["escalation_level"] = self.escalation_level
            result["challenge_count"] = self.challenge_count
            self._log_step("counter_argument", result.get("counter_argument", "No counter-argument generated")[:100])
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse devil's advocate response")
            return {"error": "Failed to generate counter-argument", "raw_response": response}

if __name__ == "__main__":
    da = DevilAdvocate()
    challenge = da.challenge(
        "AZ-104",
        "What is the difference between availability sets and availability zones?",
        "Availability sets protect against hardware failures within a datacenter, while availability zones protect across datacenters.",
        "strong"
    )
    print(json.dumps(challenge, indent=2))
