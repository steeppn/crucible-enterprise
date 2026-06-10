import os
import json
import logging
from datetime import datetime
from typing import Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crucible.evaluation")

class FoundryEvaluator:
    """Runs Foundry-style evaluation on agent responses.

    Evaluates responses against three metrics used by Azure AI Foundry:
    - Groundedness: How well the response is supported by the retrieved knowledge
    - Relevance: How well the response answers the question
    - Coherence: How well-structured and fluent the response is

    Uses GPT-4.1-mini as the evaluation model (following Foundry's pattern).
    """

    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_AI_API_KEY")
        self.model = os.getenv("AZURE_AI_PRIMARY_MODEL_DEPLOYMENT", "gpt-4.1-mini")
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_version="2024-06-01",
            api_key=self.api_key
        )

    def evaluate_response(self, question: str, answer: str, context: str) -> dict:
        """Evaluate a single Q&A pair against retrieved context."""

        prompt = f"""You are an evaluation assistant. Score the following answer on three metrics.

QUESTION: {question}

RETRIEVED CONTEXT:
{context[:1000]}

ANSWER: {answer}

Score each metric from 1 to 5:
- GROUNDEDNESS: How well is the answer supported by the retrieved context? (1 = not supported at all, 5 = fully supported with citations)
- RELEVANCE: How well does the answer address the question? (1 = completely irrelevant, 5 = directly and completely answers the question)
- COHERENCE: How well-structured and fluent is the answer? (1 = incoherent, 5 = clear, well-structured, professional)

Return ONLY a JSON object with these fields:
{{
  "groundedness": <1-5>,
  "relevance": <1-5>,
  "coherence": <1-5>,
  "groundedness_reason": "<one sentence explanation>",
  "relevance_reason": "<one sentence explanation>",
  "coherence_reason": "<one sentence explanation>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=500
            )
            result_text = response.choices[0].message.content or ""
            result = json.loads(result_text)

            result["question"] = question
            result["answer"] = answer[:200]
            result["timestamp"] = datetime.utcnow().isoformat()

            logger.info(f"Evaluation: G={result.get('groundedness')}, R={result.get('relevance')}, C={result.get('coherence')}")
            return result
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "groundedness": 0,
                "relevance": 0,
                "coherence": 0,
                "error": str(e),
                "question": question,
                "timestamp": datetime.utcnow().isoformat()
            }

    def evaluate_session(self, transcript: list, context_map: dict) -> dict:
        """Evaluate an entire session transcript."""
        evaluations = []
        qa_pairs = self._extract_qa_pairs(transcript)

        for qa in qa_pairs:
            context = context_map.get(qa["question"], "")
            eval_result = self.evaluate_response(qa["question"], qa["answer"], context)
            evaluations.append(eval_result)

        if not evaluations:
            return {
                "groundedness_avg": 0,
                "relevance_avg": 0,
                "coherence_avg": 0,
                "total_evaluations": 0,
                "evaluations": [],
                "timestamp": datetime.utcnow().isoformat()
            }

        groundedness_scores = [e["groundedness"] for e in evaluations if e.get("groundedness", 0) > 0]
        relevance_scores = [e["relevance"] for e in evaluations if e.get("relevance", 0) > 0]
        coherence_scores = [e["coherence"] for e in evaluations if e.get("coherence", 0) > 0]

        return {
            "groundedness_avg": round(sum(groundedness_scores) / len(groundedness_scores) / 5 * 100, 1) if groundedness_scores else 0,
            "relevance_avg": round(sum(relevance_scores) / len(relevance_scores) / 5 * 100, 1) if relevance_scores else 0,
            "coherence_avg": round(sum(coherence_scores) / len(coherence_scores) / 5 * 100, 1) if coherence_scores else 0,
            "total_evaluations": len(evaluations),
            "evaluations": evaluations,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _extract_qa_pairs(self, transcript: list) -> list:
        """Extract question-answer pairs from a session transcript."""
        pairs = []
        last_question = None

        for entry in transcript:
            role = entry.get("role", "")
            content = entry.get("content", "")

            if role == "examiner":
                last_question = content
            elif role == "employee" and last_question:
                pairs.append({
                    "question": last_question,
                    "answer": content
                })

        return pairs

    def generate_evaluation_report(self, session_id: str, transcript: list, context_map: dict) -> dict:
        """Generate a full evaluation report for a session."""
        evaluation = self.evaluate_session(transcript, context_map)

        return {
            "session_id": session_id,
            "evaluation": evaluation,
            "summary": self._generate_summary(evaluation),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_summary(self, evaluation: dict) -> str:
        g = evaluation.get("groundedness_avg", 0)
        r = evaluation.get("relevance_avg", 0)
        c = evaluation.get("coherence_avg", 0)

        if g >= 80 and r >= 80:
            quality = "Strong"
        elif g >= 60 and r >= 60:
            quality = "Moderate"
        else:
            quality = "Needs Improvement"

        return (
            f"{quality} session performance. "
            f"Groundedness: {g}% | Relevance: {r}% | Coherence: {c}%. "
            f"Based on {evaluation.get('total_evaluations', 0)} Q&A evaluations."
        )
