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
        self.client = None

    def _get_api_version(self, model_name: str) -> str:
        if "o4" in model_name or "o3" in model_name:
            return "2024-12-01-preview"
        return "2024-06-01"

    def _create_client(self, api_version: str = None) -> AzureOpenAI:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not set in environment")
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_version=api_version or "2024-06-01",
            api_key=os.getenv("AZURE_AI_API_KEY")
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
        api_version = self._get_api_version(model)
        self._log_step("model_call", f"Using model: {model}, api_version: {api_version}")

        client = self._create_client(api_version=api_version)

        is_reasoning_model = "o4" in model or "o3" in model
        params = {
            "model": model,
        }
        if is_reasoning_model:
            params["messages"] = [
                {"role": "user", "content": f"Instructions: {system_prompt}\n\nTask: {user_prompt}"}
            ]
            params["max_completion_tokens"] = 4000
        else:
            params["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            params["temperature"] = temperature
            params["max_tokens"] = 4000

        try:
            response = client.chat.completions.create(**params)
            msg = response.choices[0].message
            result = msg.content or ""
            if not result and hasattr(msg, 'reasoning') and msg.reasoning:
                result = msg.reasoning
            self._log_step("model_response", f"Received {len(result)} chars")
            if not result:
                self._log_step("model_warning", "Empty response from model")
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
