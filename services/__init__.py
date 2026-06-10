"""CRUCIBLE Enterprise - IQ Service Layer

Provides integration with Microsoft IQ layers:
- Foundry IQ: Azure AI Search for knowledge retrieval
- Work IQ: Simulated Microsoft 365 work context signals
- Fabric IQ: Simulated semantic ontology engine
- MCP: Microsoft Learn documentation server
- Evaluation: Foundry-style groundedness/relevance/coherence scoring
"""

from .foundry_iq import FoundryIQClient
from .work_iq import WorkIQClient
from .fabric_iq import FabricIQClient
from .mcp_client import MCPClient
from .evaluation import FoundryEvaluator

__all__ = ["FoundryIQClient", "WorkIQClient", "FabricIQClient", "MCPClient", "FoundryEvaluator"]
