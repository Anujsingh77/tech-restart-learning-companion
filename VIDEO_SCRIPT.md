# 5-Minute Video Script — Tech-Restart Learning Companion
## Kaggle AI Agents Intensive Capstone

**Total Runtime:** 5:00  
**Format:** Screen recording + voiceover (no face cam needed)  
**Screen layout:** Code editor left / Browser right, or full-browser during demo

---

## [0:00 – 0:45] SEGMENT 1: THE PROBLEM

**[Screen: Blank code editor + a sad empty Kaggle notebook]**

> "You've been away from your AI course for two months. Life got in the way — work, exams, whatever it was. Now you're back. You open your notebooks and... it all feels foreign. Do you restart from lesson one? Do you skim everything? Do you just wing it and hope the gaps don't show up?
>
> This is the return-to-learning problem. And it's more common than anyone talks about. The issue isn't motivation — it's *precision*. You don't need to relearn everything. You need to know *exactly* what to re-learn, in what order, with what resources.
>
> That's what I built this for. Meet **Tech-Restart Learning Companion** — a three-agent AI system that solves this in under 30 seconds, running entirely on your local machine."

**[Cut to: Project running in browser — landing page hero visible]**

---

## [0:45 – 1:45] SEGMENT 2: AGENT ARCHITECTURE

**[Screen: VS Code showing `app.py` class hierarchy, scroll slowly]**

> "The system has three agents — each built as a Python class extending a shared `BaseAgent`:
>
> **First: the Diagnostic Agent.** This agent evaluates your confidence across subtopics — things like closures, backpropagation, Pandas groupby — and outputs a structured gap report. It knows your weak areas, your proficiency level, and how many hours it'll take you to close each gap.
>
> **Second: the Roadmap Architect.** It takes that gap report and designs a phased, week-by-week refresher plan. Not generic advice — concrete milestones, daily hour targets, and phases tuned to whether you're a beginner restarting or an intermediate just brushing up.
>
> **Third: the Resource Scout.** This one acts as an MCP client. It queries a local Model Context Protocol server — backed by a hand-curated JSON library — and retrieves the best courses, books, and interactive platforms matched to your specific gaps."

**[Screen: Show MCP server code briefly — `mcp_server.py` endpoints]**

> "The MCP Server runs locally on port 5001. It exposes five endpoints following the MCP protocol format — including full-text search across the resource library. All inputs are sanitised at both the client and server level before any processing happens."

**[Screen: Show `AgentOrchestrator.run_pipeline()` — 4 steps visible]**

> "The **Orchestrator** sequences the pipeline: sanitise → Diagnostic → Roadmap → Scout. Context passes explicitly between agents via Python dicts. Clean, transparent, and fully logged."

---

## [1:45 – 3:30] SEGMENT 3: LIVE DEMO

**[Screen: Browser, full-screen — `index.html` open]**

> "Let me show you this running. I'm going to pretend I've been away from Python and Machine Learning for two months."

**[Action: Type name "Anuj" in the name field]**

> "I select my topics..."

**[Action: Click Python chip, then Machine Learning chip — both highlight in sky blue]**

> "Confidence sliders appear for every subtopic. I'm pretty okay with Python syntax, but I've really forgotten gradient descent and overfitting — so I'm dragging those low."

**[Action: Adjust sliders — syntax at 70, gradient descent at 15, overfitting at 20, rest mid-range]**

> "Timeline — I've got four weeks. Hit the analysis button."

**[Action: Click "Run Multi-Agent Analysis"]**

**[Screen: Loading state — animated spinner, agent log console scrolling]**

> "Watch the agent console. The Diagnostic Agent fires first — you can see it evaluating each topic. Then the Roadmap Architect picks it up. Then the Resource Scout hits the MCP server."

**[Screen: Roadmap page fades in]**

> "In about two seconds — we have a complete personalised roadmap. I need 23 hours total. That's about 49 minutes a day for four weeks.
>
> Look at the Machine Learning card — it caught that gradient descent and overfitting are my top gaps. Phase 1 tells me exactly what to do first: 'Rebuild linear regression from scratch, review bias-variance tradeoff notes.' Not 'review ML.' Specific, actionable steps.
>
> And here's the weekly schedule — all topics distributed across four weeks with daily hour targets."

**[Action: Click "View Resources →"]**

> "The Resource Scout matched these gaps to the MCP library. For my Machine Learning beginner-level gaps — Kaggle's Intro to ML course and Andrew Ng's Specialization. For Python — the CS50P course and Kaggle's interactive track. Every link is live, every resource is curated."

---

## [3:30 – 4:30] SEGMENT 4: THE BUILD

**[Screen: Split — `app.py` left, terminal right]**

> "A quick look under the hood at what makes this work.
>
> The backend is pure Python — no external AI API keys. Flask handles the HTTP layer. The agent reasoning is rule-based but sophisticated: the Diagnostic Agent's `analyze_gaps()` skill classifies proficiency from confidence averages, identifies weak subtopics, and estimates refresh hours. The Roadmap Architect's `build_roadmap()` skill uses phase-ratio templates per proficiency level and injects personalised milestones based on the top weak area.
>
> Security is built in at every layer."

**[Screen: Zoom to `sanitize_input()` function]**

> "The `sanitize_input()` method strips HTML tags, clamps numeric ranges, and validates topics against an explicit allowlist. The MCP server does the same for search queries. The frontend mirrors this with client-side sanitisation before anything is sent."

**[Screen: Show `course_library.json` briefly — clean nested structure]**

> "The MCP resource library is a structured JSON file with 20-plus resources across 7 domains, two difficulty levels each. The MCP server exposes it over a typed HTTP API following the Model Context Protocol envelope format."

**[Screen: Show the frontend running — smooth animation of chip selection]**

> "The UI is vanilla JavaScript and Tailwind CSS — no framework, no bundler. Glass-morphism cards, live slider gradients, an animated agent log console. And critically — if the backend isn't running, the JavaScript falls back to a full simulation so the UI always works for demos."

---

## [4:30 – 5:00] SEGMENT 5: WRAP-UP

**[Screen: Roadmap view — full result visible]**

> "So to recap what this project demonstrates:
>
> A three-agent OOP system with typed Skills per agent. An MCP Server exposing a structured local resource library. Full input sanitisation at every boundary. A professional, deployable web UI. And a pipeline that runs in under two seconds, entirely on your machine.
>
> The architecture is designed to grow — swap the rule-based reasoning for a local Ollama model, add spaced repetition scheduling, export to PDF. The agents are independent, the context flow is explicit, and the whole thing boots with two commands.
>
> If you've ever lost your momentum on a technical course and didn't know where to restart — this is the tool I wish I'd had. Thanks for watching."

**[Screen: Fade to project title card]**  
`Tech-Restart Learning Companion · github.com/yourusername/tech-restart · Kaggle AI Agents Intensive 2025`

---

## PRODUCTION NOTES

**Recording tips:**
- Record at 1920×1080, export at 1080p
- Use OBS Studio (free) with Display Capture
- Add light background music at -20dB (Lo-fi / Chill Beats royalty-free)
- Zoom browser to 110% for readability
- Highlight mouse clicks with a cursor highlighter tool

**Editing timeline:**
| Segment | Start | End | Duration |
|---------|-------|-----|----------|
| Problem | 0:00 | 0:45 | 45s |
| Architecture | 0:45 | 1:45 | 60s |
| Demo | 1:45 | 3:30 | 105s |
| The Build | 3:30 | 4:30 | 60s |
| Wrap-up | 4:30 | 5:00 | 30s |

**B-roll suggestions:**
- Terminal showing both servers starting up (nice visual)
- Zoom-in on the sliding agent log console during loading
- Zoom-in on a resource card hover animation
- Show MCP server status endpoint in browser (`localhost:5001/mcp/status`)
