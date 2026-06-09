import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You help assess employee readiness for Microsoft certification exams.

Ask one question at a time about the certification topic. Base your questions on the provided knowledge base content. After receiving an answer, ask a follow-up question that explores the topic further.

Return your response as a JSON object with these fields:
- question: the question to ask
- citation: object with source, skill_domain, and content_snippet
- difficulty_level: number from 1 to 5
- follow_up_strategy: one of explore, advance, maintain, shift_focus, or opening
- session_state: object with questions_asked, answers_received, and current_score

For the first question, set follow_up_strategy to opening.
"""

class Examiner(BaseAgent):
    """Agent 4: Assessment Agent for certification readiness."""

    def __init__(self):
        super().__init__(agent_name="Examiner", model_type="primary")
        self.session_state = {
            "questions_asked": 0,
            "answers_received": 0,
            "current_score": 0,
            "topic_scores": {},
            "conversation_history": []
        }

    def open_session(self, role: str, certification: str, confidence_level: str) -> dict:
        self._log_step("session_open", f"Role={role}, Cert={certification}, Confidence={confidence_level}")

        foundry_results = self._retrieve_knowledge(certification, cert_id=certification, top_k=5)
        mcp_results = self._retrieve_mcp_docs(f"{certification} exam objectives", top_k=3)

        foundry_context = self._format_retrieval_context(foundry_results, "Foundry IQ")
        mcp_context = self._format_retrieval_context(mcp_results, "Microsoft Learn MCP")

        user_prompt = f"""Generate an opening question for this employee:

Role: {role}
Certification: {certification}
Confidence: {confidence_level}

Knowledge base content:
{foundry_context}

{mcp_context}

Return JSON as described in your instructions."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)
        self.session_state["questions_asked"] += 1

        try:
            result = json.loads(response)
            result["session_state"] = self.session_state
            if foundry_results:
                result["citation"] = {
                    "source": f"Foundry IQ: {foundry_results[0].get('source_file', 'unknown')}",
                    "skill_domain": foundry_results[0].get("skill_domain", "General"),
                    "content_snippet": foundry_results[0].get("content", "")[:200]
                }
            self._log_step("opening_question", result.get("question", "No question generated"))
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse examiner response")
            return {"error": "Failed to generate question", "raw_response": response}

    def ask_follow_up(self, role: str, certification: str, user_answer: str, previous_question: str) -> dict:
        self._log_step("follow_up", f"Processing answer to: {previous_question[:80]}...")

        foundry_results = self._retrieve_knowledge(previous_question, cert_id=certification, top_k=3)
        foundry_context = self._format_retrieval_context(foundry_results, "Foundry IQ")

        history_summary = "\n".join([
            f"Q: {h['question']}\nA: {h['answer']}"
            for h in self.session_state["conversation_history"][-4:]
        ])

        user_prompt = f"""Previous question: {previous_question}
Employee answer: {user_answer}

Conversation history:
{history_summary}

Knowledge base:
{foundry_context}

Generate a follow-up question. Return JSON as described in your instructions."""

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
            if foundry_results:
                result["citation"] = {
                    "source": f"Foundry IQ: {foundry_results[0].get('source_file', 'unknown')}",
                    "skill_domain": foundry_results[0].get("skill_domain", "General"),
                    "content_snippet": foundry_results[0].get("content", "")[:200]
                }
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
