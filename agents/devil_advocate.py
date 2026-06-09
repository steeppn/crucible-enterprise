import json
import os
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You help deepen employee understanding during certification assessments.

After an employee answers a question, provide a follow-up perspective that explores additional complexity or edge cases. Base your perspective on the provided knowledge base content.

Return your response as a JSON object with these fields:
- counter_argument: the follow-up perspective to share
- citation: object with source and contradicting_content
- challenge_type: one of edge_case, missing_context, practical_application, or trade_off
- escalation_level: number from 1 to 5
- expected_defence: what a thorough response would include
"""

class DevilAdvocate(BaseAgent):
    """Agent 5: Depth exploration agent with citations."""

    def __init__(self):
        super().__init__(agent_name="DevilAdvocate", model_type="primary")
        self.escalation_level = 1
        self.challenge_count = 0

    def challenge(self, certification: str, question: str, user_answer: str, answer_quality: str = "medium") -> dict:
        self._log_step("challenge", f"Constructing follow-up perspective for answer quality={answer_quality}")

        foundry_results = self._retrieve_knowledge(question, cert_id=certification, top_k=3)
        mcp_results = self._retrieve_mcp_docs(f"{certification} {question} considerations", top_k=2)

        foundry_context = self._format_retrieval_context(foundry_results, "Foundry IQ")
        mcp_context = self._format_retrieval_context(mcp_results, "Microsoft Learn MCP")

        if answer_quality == "strong":
            self.escalation_level = min(5, self.escalation_level + 1)
        elif answer_quality == "weak":
            self.escalation_level = max(1, self.escalation_level - 1)

        user_prompt = f"""Original question: {question}
Employee answer: {user_answer}
Answer quality: {answer_quality}
Current depth level: {self.escalation_level}/5

Knowledge base:
{foundry_context}

{mcp_context}

Provide a follow-up perspective that explores additional complexity. Return JSON as described in your instructions."""

        response = self._call_model(SYSTEM_PROMPT, user_prompt)
        self.challenge_count += 1

        try:
            result = json.loads(response)
            result["escalation_level"] = self.escalation_level
            result["challenge_count"] = self.challenge_count
            if foundry_results:
                result["citation"] = {
                    "source": f"Foundry IQ: {foundry_results[0].get('source_file', 'unknown')}",
                    "contradicting_content": foundry_results[0].get("content", "")[:200]
                }
            self._log_step("follow_up_perspective", result.get("counter_argument", "No perspective generated")[:100])
            return result
        except json.JSONDecodeError:
            self._log_step("parse_error", "Failed to parse response")
            return {"error": "Failed to generate perspective", "raw_response": response}

if __name__ == "__main__":
    da = DevilAdvocate()
    challenge = da.challenge(
        "AZ-104",
        "What is the difference between availability sets and availability zones?",
        "Availability sets protect against hardware failures within a datacenter, while availability zones protect across datacenters.",
        "strong"
    )
    print(json.dumps(challenge, indent=2))
