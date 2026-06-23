# Tech-Restart Learning Companion
## Kaggle 5-Day AI Agents Intensive — Capstone Project Writeup

**Author:** Anuj Sharma  
**Submission Date:** June 2025  
**Word Count:** ~2,400

---

## The Problem: The Return-to-Learning Gap

Anyone who has taken a break from technical study — even for just two or three months — knows the feeling: you sit back down, open a notebook, and stare at code that once felt like a second language. The concepts aren't gone; they've just slipped below the surface. The standard advice is "just review everything again," which is both demoralising and inefficient. Most people don't need to restart from zero. They need a precise, personalised answer to: *what do I actually need to re-learn, and in what order?*

This is the problem **Tech-Restart Learning Companion** solves. It is a multi-agent AI system built for students returning to AI/ML and JavaScript coursework after a break. In under 30 seconds, three cooperating agents assess your specific knowledge gaps, design a week-by-week refresher roadmap, and surface the best curated resources — all running entirely on a local machine, with no external API keys required.

---

## Why Multi-Agent? Why Local?

A single monolithic prompt is a blunt instrument. The three tasks involved here — *diagnosing gaps*, *planning a curriculum*, and *retrieving resources* — have genuinely different concerns. Diagnosis requires domain-specific knowledge and evaluation logic. Planning requires temporal reasoning and milestone design. Resource retrieval requires querying a structured knowledge base. Separating these into agents with distinct responsibilities creates a system that is:

- **Easier to debug and extend** — each agent can be tested independently
- **More transparent** — the pipeline logs every decision per agent
- **Practically deployable** — no cloud API dependency, runs immediately on any machine with Python

The local-first constraint was also a deliberate design choice aligned with the course's theme of responsible AI deployment. Users' self-assessed confidence data is sensitive; it never leaves their machine.

---

## Architecture

### OOP Class Hierarchy

```
BaseAgent (abstract)
├── DiagnosticAgent
├── RoadmapArchitect
└── ResourceScout

AgentOrchestrator        ← coordinates the pipeline
MCPServer (Flask)        ← serves course_library.json over HTTP
```

All agents extend `BaseAgent`, which provides shared infrastructure: a structured log buffer, a creation timestamp, and the abstract `run()` interface. This enforces a consistent contract while allowing each agent to specialise.

---

### Agent 1: DiagnosticAgent

**Role:** Assess knowledge gaps from student confidence ratings.

The DiagnosticAgent holds a curated question bank across six domains — Python, Machine Learning, Deep Learning, JavaScript, NLP, and Data Analysis — with questions tagged by subtopic and difficulty. Its primary **Skill** (`analyze_gaps`) receives a map of subtopic confidence scores (0–100, self-reported via UI sliders) and produces a structured gap report containing:

- An **overall proficiency score** (weighted average)
- A **proficiency level** (Beginner / Intermediate / Advanced)
- **Weak areas** (subtopics scoring below 40)
- **Priority gaps** sorted by urgency
- An **estimated refresh time** in hours

The self-report approach is intentional. It is faster than a quiz, correlates well with actual performance (metacognitive accuracy research supports this for intermediate learners), and eliminates the latency of LLM-graded responses — keeping the system fully local.

---

### Agent 2: RoadmapArchitect

**Role:** Design a phased, time-boxed refresher curriculum.

The RoadmapArchitect ingests the DiagnosticAgent's gap reports and a user-specified timeline (in weeks), and produces a complete roadmap. Its design uses **phase templates** keyed to proficiency level:

| Level | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| Beginner | Foundation Reset | Applied Practice | Mini Project |
| Intermediate | Gap Bridging | Pattern Mastery | Project Sprint |
| Advanced | Spot Review | Challenge Mode | *(2 phases)* |

Each phase carries a `week_share` ratio (e.g. 0.4 / 0.4 / 0.2) that distributes the estimated hours. Milestones are generated per topic per phase using a domain-specific template system, with personalised injections for the top weak area discovered by the DiagnosticAgent.

The output includes a weekly schedule that interleaves all selected topics across the timeline, a daily commitment figure in minutes, and concrete milestone checklists for every phase.

---

### Agent 3: ResourceScout (MCP Client)

**Role:** Fetch curated learning resources from the local MCP server.

The ResourceScout acts as an MCP client. It reads the student's roadmap topic list, queries the local MCP server for each topic at the appropriate difficulty level, and returns a matched resource list. It also handles topic alias resolution (e.g., `"ml"` → `"machine_learning"`) and supplements thin results from the adjacent level if needed.

---

### MCP Server

The Model Context Protocol (MCP) Server is a standalone Flask application running on port 5001. It exposes `course_library.json` — a structured library of 20+ courses, books, and interactive platforms — through a typed HTTP API:

| Endpoint | MCP Tool Name | Description |
|----------|---------------|-------------|
| `GET /mcp/status` | `mcp_status` | Server health + topic list |
| `GET /mcp/resources` | `list_all_topics` | All topics + resource counts |
| `GET /mcp/resources/<topic>` | `get_resources_by_topic` | All levels for a topic |
| `GET /mcp/resources/<topic>/<level>` | `get_resources_by_topic_and_level` | Specific level |
| `GET /mcp/search?q=<query>` | `search_resources` | Full-text search |

Every response is wrapped in an MCP envelope (`mcp_version`, `tool`, `server`, `data`) following the protocol convention. All search inputs are sanitised before querying.

---

### AgentOrchestrator

The orchestrator coordinates the three-agent pipeline with a single `run_pipeline()` call:

```
Input → sanitize_input()
         ↓
     DiagnosticAgent.run()   → gap_reports
         ↓
     RoadmapArchitect.run()  → roadmap
         ↓
     ResourceScout.run()     → resources
         ↓
     Consolidated JSON Response
```

Context is passed explicitly between agents via Python dicts — no shared mutable state, no hidden coupling. The logs from all three agents are collected and returned in the API response, giving full transparency into every decision in the pipeline.

---

## Security Features

Security was treated as a first-class concern, not an afterthought:

**Input Sanitisation (Backend — `sanitize_input`):**
- HTML tags stripped from all string fields using `re.sub(r'<[^>]+>', '', value)`
- String lengths capped at 200 characters
- Confidence scores clamped to `[0, 100]` range
- Topics validated against an explicit allowlist (`ALLOWED_TOPICS`)
- Unknown topics silently dropped rather than raising errors

**Input Sanitisation (Frontend — `sanitizeString`):**
- Client-side HTML stripping before sending to API
- `maxlength` attributes on all text inputs
- Topics only selectable from predefined chip buttons (no free-text topic entry)

**Search Sanitisation (MCP Server — `sanitize_query`):**
- HTML stripping on search queries
- 100-character length cap
- Minimum 2-character query requirement

**CORS:** Enabled via `flask-cors` with standard defaults; can be tightened to specific origins for production.

---

## Frontend Design

The UI is built with pure HTML, Tailwind CSS (CDN), and vanilla JavaScript — no framework required. The design follows a **White and Sky Blue** palette with glassmorphism card surfaces:

- **Glass cards:** `rgba(255,255,255,0.78)` background with `backdrop-filter: blur(16px)` and `border: 1px solid rgba(186,230,253,0.5)`
- **Ambient orbs:** Fixed-position blurred circles create depth without clutter
- **Typography:** Space Grotesk (display) + Inter (body) — a pairing that balances technical credibility with warmth
- **Interaction:** Confidence sliders with live gradient fill, topic chips with selection state, animated agent log console

The flow is deliberately linear — three steps (Assess → Roadmap → Resources) — with a sticky header navigation that reflects pipeline progress. The frontend includes a full **offline simulation fallback**: if the Python backend is not running, the JavaScript generates a realistic result from the same logic, so the UI can be demoed standalone.

---

## Kaggle Requirements Fulfilled

| Requirement | Implementation |
|-------------|----------------|
| ✅ Multi-agent system | DiagnosticAgent + RoadmapArchitect + ResourceScout, orchestrated via `AgentOrchestrator` |
| ✅ MCP Server integration | Standalone Flask MCP server on port 5001 serving `course_library.json` |
| ✅ Agent Skills / Custom tools | `analyze_gaps()`, `build_roadmap()`, `scout_resources()` as typed Skill methods per agent |
| ✅ Security features | Server-side sanitisation in `sanitize_input()`, client-side sanitisation, MCP query sanitisation, topic allowlists |
| ✅ Deployability | Professional Web UI with Tailwind CSS; backend launchable with `python app.py`; zero external dependencies |

---

## How to Run

```bash
# 1. Install dependencies
pip install flask flask-cors

# 2. Start the MCP Server (terminal 1)
cd backend
python mcp_server.py       # Runs on http://localhost:5001

# 3. Start the Agent Backend (terminal 2)
python app.py              # Runs on http://localhost:5000

# 4. Open the frontend
open frontend/index.html   # Or serve with: python -m http.server 8080
```

The system also runs in **standalone mode** — open `index.html` directly without starting the backend. The JavaScript offline fallback kicks in automatically and produces a full simulated roadmap.

---

## Reflections and Future Work

The most interesting design challenge was the balance between simulation fidelity and true local execution. The current system uses rule-based logic to simulate the "reasoning" layer — proficiency classification, phase weighting, milestone generation — which runs instantly and deterministically. A natural next step is integrating a local LLM (via Ollama) as a drop-in replacement for the rule engine, enabling truly generative milestone suggestions and more nuanced gap analysis, while keeping the system fully offline.

Other planned extensions:
- **Spaced repetition scheduler**: Convert roadmap milestones into a SM-2 review deck
- **Progress tracking**: LocalStorage-backed checkpoint system
- **Export**: Generate a PDF roadmap summary
- **Ollama integration**: Swap rule-based reasoning for `llama3` or `mistral` responses via `localhost:11434`

The architecture's OOP design makes these additions straightforward — each agent is a clean extension point.

---

## Conclusion

Tech-Restart Learning Companion demonstrates that a genuinely useful, production-quality multi-agent system can be built without cloud APIs, without paid services, and without sacrificing user experience. The three-agent pipeline maps naturally onto the real cognitive steps of returning to a course: *figure out what you forgot, make a plan, find the right materials*. By encoding those steps as discrete agents with typed skills and explicit context-passing, the system is transparent, extensible, and immediately runnable by any student with Python installed.
