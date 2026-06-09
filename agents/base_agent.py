import os
import json
import logging
from datetime import datetime
from typing import Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crucible.agents")

class BaseAgent:
    """Base class for all CRUCIBLE agents. Handles model routing, grounding, and reasoning traces."""

    MODEL_PRIMARY = os.getenv("AZURE_AI_PRIMARY_MODEL_DEPLOYMENT", "crucible-examiner")
    MODEL_REASONING = os.getenv("AZURE_AI_REASONING_MODEL_DEPLOYMENT", "crucible-reasoning")

    def __init__(self, agent_name: str, model_type: str = "primary"):
        self.agent_name = agent_name
        self.model_type = model_type
        self.reasoning_trace = []
        self.client = self._create_client()

    def _create_client(self) -> AzureOpenAI:
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        if not endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT not set in environment")
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-05-01-preview",
            api_key=os.getenv("AZURE_AI_API_KEY", "dummy-key-for-foundry")
        )

    def _get_model_name(self) -> str:
        if self.model_type == "reasoning":
            return self.MODEL_REASONING
        return self.MODEL_PRIMARY

    def _log_step(self, step: str, detail: str):
        entry = {
            "agent": self.agent_name,
            "step": step,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.reasoning_trace.append(entry)
        logger.info(f"[{self.agent_name}] {step}: {detail}")

    def _call_model(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        model = self._get_model_name()
        self._log_step("model_call", f"Using model: {model}")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            result = response.choices[0].message.content
            self._log_step("model_response", f"Received {len(result)} chars")
            return result
        except Exception as e:
            self._log_step("model_error", str(e))
            raise

    def _format_citation(self, source: str, content: str) -> dict:
        return {
            "source": source,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_reasoning_trace(self) -> list:
        return self.reasoning_trace

    def clear_trace(self):
        self.reasoning_trace = []
