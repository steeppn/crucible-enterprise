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
    """Base class for all CRUCIBLE agents. Handles model routing, IQ layer integration, and reasoning traces."""

    MODEL_PRIMARY = os.getenv("AZURE_AI_PRIMARY_MODEL_DEPLOYMENT", "crucible-examiner")
    MODEL_REASONING = os.getenv("AZURE_AI_REASONING_MODEL_DEPLOYMENT", "crucible-reasoning")

    def __init__(self, agent_name: str, model_type: str = "primary"):
        self.agent_name = agent_name
        self.model_type = model_type
        self.reasoning_trace = []
        self.client = None
        self._foundry_iq = None
        self._work_iq = None
        self._fabric_iq = None
        self._mcp_client = None

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

    # ── IQ Layer Helpers ──────────────────────────────────────────────

    def _get_foundry_iq(self):
        """Lazy-load Foundry IQ client."""
        if self._foundry_iq is None:
            from services.foundry_iq import FoundryIQClient
            self._foundry_iq = FoundryIQClient()
        return self._foundry_iq

    def _get_work_iq(self):
        """Lazy-load Work IQ client."""
        if self._work_iq is None:
            from services.work_iq import WorkIQClient
            self._work_iq = WorkIQClient()
        return self._work_iq

    def _get_fabric_iq(self):
        """Lazy-load Fabric IQ client."""
        if self._fabric_iq is None:
            from services.fabric_iq import FabricIQClient
            self._fabric_iq = FabricIQClient()
        return self._fabric_iq

    def _get_mcp_client(self):
        """Lazy-load MCP client."""
        if self._mcp_client is None:
            from services.mcp_client import MCPClient
            self._mcp_client = MCPClient()
        return self._mcp_client

    def _retrieve_knowledge(self, query: str, cert_id: str = None, top_k: int = 5) -> list:
        """Retrieve grounded knowledge from Foundry IQ."""
        foundry = self._get_foundry_iq()
        results = foundry.query(query, cert_id=cert_id, top_k=top_k)
        self._log_step("foundry_iq_retrieval", f"Query: {query[:60]}... Results: {len(results)}")
        return results

    def _retrieve_mcp_docs(self, query: str, top_k: int = 5) -> list:
        """Search Microsoft Learn documentation via MCP."""
        mcp = self._get_mcp_client()
        results = mcp.search_docs(query, top_k=top_k)
        self._log_step("mcp_search", f"Query: {query[:60]}... Results: {len(results)}")
        return results

    def _get_employee_signals(self, employee_id: str) -> dict:
        """Get work context signals from Work IQ."""
        work_iq = self._get_work_iq()
        signals = work_iq.get_employee_signals(employee_id)
        self._log_step("work_iq_signals", f"Employee: {employee_id}, Workload: {signals.get('workload_level', 'unknown')}")
        return signals

    def _get_available_slots(self, employee_id: str, hours_needed: int = 2) -> list:
        """Get available study slots from Work IQ."""
        work_iq = self._get_work_iq()
        slots = work_iq.get_available_slots(employee_id, hours_needed=hours_needed)
        self._log_step("work_iq_slots", f"Employee: {employee_id}, Available slots: {len(slots)}")
        return slots

    def _get_cert_details(self, cert_id: str) -> dict:
        """Get certification details from Fabric IQ ontology."""
        fabric = self._get_fabric_iq()
        details = fabric.get_cert_details(cert_id)
        self._log_step("fabric_iq_cert", f"Cert: {cert_id}, Found: {details is not None}")
        return details

    def _get_role_mapping(self, role: str) -> dict:
        """Get role-to-cert mapping from Fabric IQ ontology."""
        fabric = self._get_fabric_iq()
        mapping = fabric.get_role_cert_mapping(role)
        self._log_step("fabric_iq_role", f"Role: {role}, Primary: {mapping.get('primary_cert')}")
        return mapping

    def _get_skill_overlap(self, cert_a: str, cert_b: str) -> dict:
        """Get skill overlap analysis from Fabric IQ."""
        fabric = self._get_fabric_iq()
        overlap = fabric.get_skill_overlap(cert_a, cert_b)
        self._log_step("fabric_iq_overlap", f"{cert_a} vs {cert_b}: {overlap.get('overlap_pct', 0)}% overlap")
        return overlap

    def _get_learner_readiness(self, learner_id: str) -> dict:
        """Get learner readiness from Fabric IQ analytics."""
        fabric = self._get_fabric_iq()
        readiness = fabric.get_learner_readiness(learner_id)
        self._log_step("fabric_iq_readiness", f"Learner: {learner_id}, Score: {readiness.get('readiness_score', 0)}")
        return readiness

    def _get_team_analytics(self, cert_id: str = None) -> dict:
        """Get team analytics from Fabric IQ."""
        fabric = self._get_fabric_iq()
        analytics = fabric.get_team_analytics(cert_id=cert_id)
        self._log_step("fabric_iq_analytics", f"Cert: {cert_id or 'all'}, Learners: {analytics.get('total_learners', 0)}")
        return analytics

    def _recommend_next_cert(self, role: str, completed_certs: list) -> list:
        """Get certification recommendations from Fabric IQ."""
        fabric = self._get_fabric_iq()
        recs = fabric.recommend_next_cert(role, completed_certs)
        self._log_step("fabric_iq_recommend", f"Role: {role}, Recommendations: {len(recs)}")
        return recs

    def _format_retrieval_context(self, results: list, source: str = "Foundry IQ") -> str:
        """Format retrieval results into context text for model prompts."""
        if not results:
            return f"No {source} results found."
        
        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Unknown")
            content = r.get("content", "")[:500]
            section = r.get("section", "")
            skill = r.get("skill_domain", "")
            score = r.get("reranker_score", 0)
            
            part = f"[{i}] {title}"
            if section:
                part += f" (Section: {section})"
            if skill:
                part += f" [Skill: {skill}]"
            if score:
                part += f" (Relevance: {score:.2f})"
            part += f"\n{content}"
            context_parts.append(part)
        
        return f"{source} Retrieved Content:\n" + "\n\n---\n\n".join(context_parts)

    def get_reasoning_trace(self) -> list:
        return self.reasoning_trace

    def clear_trace(self):
        self.reasoning_trace = []
