# CRUCIBLE Enterprise

> **Voice-First Adversarial Certification Readiness Agent**
> Reasoning Agents Track | Microsoft Foundry Hackathon
> Built by Steph & Era

*"You don't know it until you can defend it."*

## What Is It

CRUCIBLE Enterprise is a voice-native, multi-agent certification readiness system built for organisations that need to know — really know — whether their people are ready to certify. Instead of self-reported confidence scores or multiple-choice practice tests, CRUCIBLE puts employees through a live spoken interrogation grounded in approved organisational knowledge. Agents question, challenge, and pressure-test understanding out loud.

## The Problem

Enterprise certification programmes rely on self-reported readiness and practice quiz scores. Both are poor signals. Employees can recognise correct answers without understanding the underlying concept. CRUCIBLE solves this by replacing passive assessment with **adversarial spoken interrogation** — the closest simulation of real exam and interview pressure that an AI system can produce.

## Architecture

```
Employee (Voice)
     ↓
Voice Live API (STT → TTS)
     ↓
FastAPI Backend
     ↓
Six-Agent Pipeline
     ├── Learning Path Curator (Planner)
     ├── Study Plan Generator (Executor)
     ├── Engagement Agent (Work IQ)
     ├── Examiner (Adversarial Assessor)
     ├── Devil's Advocate (Critic)
     └── Verdict + Manager Insights (Verifier)
     ↓
Microsoft IQ Layers
     ├── Foundry IQ — Knowledge base grounding
     ├── Work IQ — Work context signals
     └── Fabric IQ — Semantic layer
```

## Setup

1. **Azure Account:** Create at https://azure.microsoft.com/free
2. **Foundry Project:** Create at https://ai.azure.com
3. **Deploy Models:** Deploy GPT-4.1-mini as `crucible-examiner` and o4-mini as `crucible-reasoning`
4. **Clone & Configure:**
   ```bash
   git clone <repo-url>
   cd crucible-enterprise
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your Azure endpoints
   ```
5. **Run:**
   ```bash
   python -m agents.learning_path_curator
   ```

## Tech Stack

| Component | Tool |
|---|---|
| Agent orchestration | `azure-ai-agents` SDK + Python |
| Voice I/O | Voice Live API |
| Knowledge grounding | Foundry IQ (Azure AI Search) |
| LLM reasoning | GPT-4.1-mini + o4-mini |
| Backend | FastAPI + uvicorn |
| Frontend | HTML/CSS/JS |

## Synthetic Data

All data in this project is clearly fabricated. No real names, emails, or PII are used anywhere. See `/data/` and `/knowledge_base/` for the synthetic datasets.

## Team

- **Steph** — Technical Lead
- **Era** — Creative Lead

## License

MIT
