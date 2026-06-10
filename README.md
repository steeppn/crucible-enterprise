# CRUCIBLE Enterprise

> **Voice-First Adversarial Certification Readiness System**
> Reasoning Agents Track | Microsoft Foundry Hackathon
> Built by Steph & Era

*"You don't know it until you can defend it."*

## What Is It

CRUCIBLE Enterprise is a multi-agent certification readiness system that puts employees through a live spoken interrogation grounded in approved organisational knowledge. Instead of self-reported confidence scores or practice quizzes, CRUCIBLE uses six specialised agents to question, challenge, and pressure-test understanding, then produces individual readiness reports and team-level manager insights.

## The Problem

Enterprise certification programmes rely on passive assessment signals. Employees can recognise correct answers without understanding the underlying concept. CRUCIBLE replaces this with **grounded spoken interrogation** agents ask cited questions from the knowledge base, adapt difficulty based on answer quality, and produce structured readiness analytics.

## Architecture

```
Employee (Voice)
     ↓
Voice Live API (STT → TTS)
     ↓
FastAPI Backend
     ↓
Six-Agent Pipeline
     ├── Learning Path Curator ──→ Foundry IQ + Fabric IQ + MCP
     ├── Study Plan Generator ───→ Fabric IQ + Work IQ
     ├── Engagement Agent ───────→ Work IQ
     ├── Examiner ───────────────→ Foundry IQ + MCP
     ├── Devil's Advocate ───────→ Foundry IQ + MCP
     └── Verdict + Manager ──────→ Fabric IQ + Work IQ
```

## Microsoft IQ Integration

CRUCIBLE integrates all three Microsoft IQ layers plus the Microsoft Learn MCP server:

| IQ Layer | Implementation | Purpose |
|---|---|---|
| **Foundry IQ** | Azure AI Search (real) | Indexes certification guides, returns semantically-ranked passages with citations |
| **Work IQ** | Simulated Graph API pattern | Employee meeting load, focus hours, calendar availability, team capacity |
| **Fabric IQ** | Simulated ontology engine | Certification prerequisites, skill overlap, role mappings, learner analytics |
| **MCP** | Microsoft Learn server (real) | Live search of official Microsoft documentation and code samples |

### Agent-to-IQ Mapping

| Agent | IQ Layers Used | What It Does |
|---|---|---|
| **Learning Path Curator** | Foundry IQ + Fabric IQ + MCP | Maps role → cert → skills, returns cited learning brief |
| **Study Plan Generator** | Fabric IQ + Work IQ | Builds milestone-based schedule accounting for workload |
| **Engagement Agent** | Work IQ | Personalises study windows and reminders to work patterns |
| **Examiner** | Foundry IQ + MCP | Asks grounded, cited assessment questions |
| **Devil's Advocate** | Foundry IQ + MCP | Explores edge cases and missing context in answers |
| **Verdict + Manager** | Fabric IQ + Work IQ | Produces readiness scores and team-level analytics |

## Service Layer

```
services/
├── foundry_iq.py    # Azure AI Search client — index creation, document upload, semantic queries
├── mcp_client.py    # Microsoft Learn MCP client — Streamable HTTP, tool discovery, doc search
├── work_iq.py       # Simulated Work IQ — employee signals, calendar slots, team capacity
└── fabric_iq.py     # Simulated Fabric IQ — ontology traversal, skill analysis, readiness analytics
```

All agents access IQ layers through helper methods in `base_agent.py`:
- `_retrieve_knowledge()` → Foundry IQ semantic search
- `_retrieve_mcp_docs()` → Microsoft Learn documentation search
- `_get_employee_signals()` → Work IQ work context
- `_get_cert_details()` → Fabric IQ ontology
- `_get_learner_readiness()` → Fabric IQ analytics

## Setup

1. **Azure Account:** Create at https://azure.microsoft.com/free
2. **Foundry Project:** Create at https://ai.azure.com
3. **Deploy Models:** Deploy `gpt-4.1-mini` and `o4-mini`
4. **Azure AI Search:** Create a Free tier search service, copy endpoint and admin key
5. **Clone & Configure:**
   ```bash
   git clone https://github.com/steeppn/crucible-enterprise.git
   cd crucible-enterprise
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
6. **Edit `.env`:**
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_AI_API_KEY=your-key
   AZURE_AI_PRIMARY_MODEL_DEPLOYMENT=gpt-4.1-mini
   AZURE_AI_REASONING_MODEL_DEPLOYMENT=o4-mini
   AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
   AZURE_SEARCH_API_KEY=your-search-key
   VOICE_LIVE_STT_ENDPOINT=wss://your-voice-live-endpoint/stt
   VOICE_LIVE_TTS_ENDPOINT=wss://your-voice-live-endpoint/tts
   VOICE_LIVE_API_KEY=your-voice-key
   ```
7. **Start the API server:**
   ```bash
   python -m api.main
   ```
   Server runs at http://localhost:8000

8. **Run an agent directly:**
   ```bash
   python -m agents.learning_path_curator
   ```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/session/start` | Start a new assessment session |
| `WS` | `/session/stream/{id}` | WebSocket for real-time session streaming |
| `POST` | `/session/answer` | Submit an answer to an active session |
| `GET` | `/session/report/{id}` | Get full session report with verdict |
| `GET` | `/session/{id}` | Get session status |
| `POST` | `/learning-brief` | Generate a learning brief for a role + cert |
| `POST` | `/study-plan` | Generate a study plan |
| `GET` | `/engagement/{id}` | Get engagement signals for an employee |
| `GET` | `/dashboard` | Get team dashboard with evaluation metrics |
| `GET` | `/dashboard/cert/{id}` | Get certification-specific dashboard |

## Tech Stack

| Component | Tool |
|---|---|
| Agent orchestration | Python + `azure-ai-agents` SDK |
| Voice I/O | Voice Live API |
| Knowledge grounding | Foundry IQ (Azure AI Search) |
| External tools | Microsoft Learn MCP Server |
| Work context | Work IQ (simulated Graph API) |
| Semantic layer | Fabric IQ (simulated ontology) |
| LLM reasoning | GPT-4.1-mini + o4-mini |
| Backend | FastAPI + uvicorn |
| Frontend | HTML/CSS/JS |

## Synthetic Data

All data in this project is clearly fabricated. No real names, emails, or PII are used. Identifiers use the `L-1001` / `EMP-001` pattern. See `/data/` and `/knowledge_base/` for the synthetic datasets.

## Project Structure

```
crucible-enterprise/
├── agents/              # Six specialised agent classes + orchestrator
│   ├── base_agent.py    # Model routing + IQ layer helpers
│   ├── orchestrator.py  # Session loop: Examiner → Devil's Advocate → Verdict
│   ├── learning_path_curator.py
│   ├── study_plan_generator.py
│   ├── engagement_agent.py
│   ├── examiner.py
│   ├── devil_advocate.py
│   └── verdict_manager_insights.py
├── services/            # IQ layer integrations + evaluation
│   ├── foundry_iq.py    # Azure AI Search client
│   ├── mcp_client.py    # Microsoft Learn MCP client
│   ├── work_iq.py       # Simulated Graph API
│   ├── fabric_iq.py     # Simulated ontology engine
│   └── evaluation.py    # Foundry-style groundedness/relevance/coherence scoring
├── api/                 # FastAPI backend
│   └── main.py          # REST + WebSocket endpoints
├── voice/               # Voice pipeline
│   └── voice_live_client.py  # STT/TTS WebSocket client
├── data/                # Synthetic datasets
│   ├── learner_performance.json
│   ├── work_activity_signals.json
│   ├── work_calendar_events.json
│   └── certification_semantic_model.json
├── knowledge_base/      # Synthetic certification guides
├── docs/                # Documentation
│   └── era-frontend-guide.md  # Frontend build guide
└── frontend/            # UI (in progress)
```

## Team

- **Stephen Alegros** - Technical Lead
- **Era Yesha Reyes** - Creative Lead

## License

MIT
