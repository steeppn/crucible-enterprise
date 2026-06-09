import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are the Examiner in CRUCIBLE Enterprise, a voice-first adversarial certification readiness system.

Your role: Conduct a spoken interrogation session to assess an employee's readiness for their target certification. You ask grounded questions cited from the organisation's knowledge base, listen to spoken answers, and adapt follow-up questions in real time.

BEHAVIOUR RULES:
- Open each session by acknowledging the employee's calibration (topic + confidence level)
- Ask ONE question at a time — wait for the employee's answer before proceeding
- Every question MUST be grounded in the knowledge base content provided
- Cite the specific skill domain or exam objective your question relates to
- Do NOT accept vague or surface-level answers — probe deeper with follow-ups
- If an answer is weak, ask a more specific follow-up on the same topic
- If an answer is strong, escalate to a harder question on a related topic
- Adapt difficulty based on answer quality (track internally)
- Be professional but firm — this is an adversarial examination, not a friendly quiz
- Never give away the answer in your question

OUTPUT FORMAT:
Return a JSON object with:
- "question": string (the question to ask the employee)
- "citation": { "source": string, "skill_domain": string, "content_snippet": string }
- "difficulty_level": number (1-5, where 1 is basic recall, 5 is complex synthesis)
- "follow_up_strategy": string (one of: "probe_deeper", "escalate", "maintain", "redirect")
- "session_state": { "questions_asked": number, "answers_received": number, "current_score": number }

If this is the opening question (no prior answers), set follow_up_strategy to "opening".

Return valid JSON only — no markdown, no explanation outside the JSON.
"""

class Examiner(BaseAgent):
    """Agent 4: Adversarial Assessor — voice-first grounded questioning."""

    def __init__(self):
        super().__init__(agent_name="Examiner", model_type="primary")
        self.knowledge_base = self._load_knowledge_base()
        self.session_state = {
            "questions_asked": 0,
            "answers_received": 0,
            "current_score": 0,
            "topic_scores": {},
            "conversation_history": []
        }

    def _load_knowledge_base(self) -> dict:
        kb = {}
        kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
        for filename in os.listdir(kb_dir):
            if filename.endswith(".md"):
                cert_id = filename.replace("_guide.md", "").upper()
                with open(os.path.join(kb_dir, filename), "r", encoding="utf-8") as f:
                    kb[cert_id] = f.read()
        return kb

    def open_session(self, role: str, certification: str, confidence_level: str) -> dict:
        self._log_step("session_open", f"Role={role}, Cert={certification}, Confidence={confidence_level}")

        cert_id = certification.upper().replace("-", "")
        if cert_id not in self.knowledge_base:
            return {"error": f"Certification {certification} not found in knowledge base"}

        kb_content = self.knowledge_base[cert_id]

        user_prompt = f"""This is the OPENING question for a new session.

Employee Role: {role}
Target Certification: {certification}
Employee's Self-Rated Confidence: {confidence_level}

Knowledge Base Content:
{kb_content}

Generate an opening question that:
1. Acknowledges their confidence level
2. Asks a grounded question from the knowledge base
3. Sets the tone for an adversarial examination

Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)
        self.session_state["questions_asked"] += 1

        try:
            result = json.loads(response)
            result["session_state"] = self.session_state
            self._log_step("opening_question", result.get("question", "No question generated"))
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse examiner response")
            return {"error": "Failed to generate question", "raw_response": response}

    def ask_follow_up(self, role: str, certification: str, user_answer: str, previous_question: str) -> dict:
        self._log_step("follow_up", f"Processing answer to: {previous_question[:80]}...")

        cert_id = certification.upper().replace("-", "")
        kb_content = self.knowledge_base.get(cert_id, "")

        history_summary = "\n".join([
            f"Q: {h['question']}\nA: {h['answer']}"
            for h in self.session_state["conversation_history"][-4:]
        ])

        user_prompt = f"""PREVIOUS QUESTION: {previous_question}

EMPLOYEE'S ANSWER: {user_answer}

CONVERSATION HISTORY (last 4 exchanges):
{history_summary}

Knowledge Base Content:
{kb_content}

Evaluate the answer and generate the next question.
Return the JSON as specified in your system prompt."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)
        self.session_state["questions_asked"] += 1
        self.session_state["answers_received"] += 1
        self.session_state["conversation_history"].append({
            "question": previous_question,
            "answer": user_answer
        })

        try:
            result = json.loads(response)
            result["session_state"] = self.session_state
            self._log_step("follow_up_question", result.get("question", "No question generated"))
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse examiner response")
            return {"error": "Failed to generate follow-up", "raw_response": response}

    def get_session_summary(self) -> dict:
        return {
            "session_state": self.session_state,
            "reasoning_trace": self.reasoning_trace
        }

if __name__ == "__main__":
    examiner = Examiner()
    opening = examiner.open_session("Cloud Engineer", "AZ-104", "70%")
    print(json.dumps(opening, indent=2))
