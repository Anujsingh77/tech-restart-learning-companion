"""
Tech-Restart Learning Companion
================================
Multi-Agent Backend — 100% Local (No external API keys required)

Architecture:
  - DiagnosticAgent   : Assesses knowledge gaps from quiz answers
  - RoadmapArchitect  : Creates a personalised Refresher Roadmap
  - ResourceScout     : Fetches curated resources via local MCP Server

OOP Design:
  BaseAgent → DiagnosticAgent
            → RoadmapArchitect
            → ResourceScout
  AgentOrchestrator manages the full pipeline.
"""

import json
import re
import os
import math
from datetime import datetime
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# ─────────────────────────────────────────────
# 1. BASE AGENT (OOP Foundation)
# ─────────────────────────────────────────────

class BaseAgent:
    """Abstract base class for all agents in the system."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow().isoformat()
        self._log: list[str] = []

    def log(self, message: str):
        entry = f"[{self.name}] {message}"
        self._log.append(entry)
        print(entry)

    def get_logs(self) -> list[str]:
        return self._log

    def run(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement run()")

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' role='{self.role}'>"


# ─────────────────────────────────────────────
# 2. DIAGNOSTIC AGENT
# ─────────────────────────────────────────────

class DiagnosticAgent(BaseAgent):
    """
    Assesses the student's knowledge gaps by evaluating their
    quiz responses and self-reported confidence levels.
    
    Skill: analyze_gaps(quiz_data) → gap_report
    """

    # Domain-specific question banks
    QUESTION_BANK = {
        "python": [
            {
                "id": "py_1",
                "question": "What is the output of: `[x**2 for x in range(4)]`?",
                "answer": "[0, 1, 4, 9]",
                "topic": "list_comprehensions",
                "difficulty": "beginner"
            },
            {
                "id": "py_2",
                "question": "What keyword makes a function return a value lazily (one at a time)?",
                "answer": "yield",
                "topic": "generators",
                "difficulty": "intermediate"
            },
            {
                "id": "py_3",
                "question": "What does `*args` allow you to do in a function definition?",
                "answer": "Accept a variable number of positional arguments",
                "topic": "functions",
                "difficulty": "beginner"
            }
        ],
        "machine_learning": [
            {
                "id": "ml_1",
                "question": "What is the purpose of a validation set?",
                "answer": "To tune hyperparameters and estimate model performance without touching the test set",
                "topic": "model_validation",
                "difficulty": "beginner"
            },
            {
                "id": "ml_2",
                "question": "Name ONE technique to combat overfitting.",
                "answer": "Regularisation / Dropout / Early Stopping / Cross-validation / More data",
                "topic": "overfitting",
                "difficulty": "intermediate"
            },
            {
                "id": "ml_3",
                "question": "What does 'gradient descent' minimise?",
                "answer": "The loss (cost) function",
                "topic": "optimisation",
                "difficulty": "beginner"
            }
        ],
        "deep_learning": [
            {
                "id": "dl_1",
                "question": "What is the role of an activation function in a neural network?",
                "answer": "Introduce non-linearity so the network can learn complex patterns",
                "topic": "activations",
                "difficulty": "beginner"
            },
            {
                "id": "dl_2",
                "question": "What does 'backpropagation' compute?",
                "answer": "Gradients of the loss with respect to each weight via the chain rule",
                "topic": "backpropagation",
                "difficulty": "intermediate"
            }
        ],
        "javascript": [
            {
                "id": "js_1",
                "question": "What is the difference between `let`, `const`, and `var`?",
                "answer": "let/const are block-scoped; const cannot be reassigned; var is function-scoped and hoisted",
                "topic": "scope",
                "difficulty": "beginner"
            },
            {
                "id": "js_2",
                "question": "What does `.then()` do on a Promise?",
                "answer": "Registers a callback to run when the Promise resolves successfully",
                "topic": "async",
                "difficulty": "intermediate"
            },
            {
                "id": "js_3",
                "question": "What is event bubbling?",
                "answer": "An event triggered on a child element propagates up through its ancestors",
                "topic": "dom_events",
                "difficulty": "intermediate"
            }
        ],
        "nlp": [
            {
                "id": "nlp_1",
                "question": "What does TF-IDF stand for and what does it measure?",
                "answer": "Term Frequency–Inverse Document Frequency; measures how important a word is to a document relative to a corpus",
                "topic": "text_representation",
                "difficulty": "beginner"
            },
            {
                "id": "nlp_2",
                "question": "What is the core innovation of the Transformer architecture?",
                "answer": "Self-attention mechanism allowing the model to weigh the relevance of each token to every other token",
                "topic": "transformers",
                "difficulty": "intermediate"
            }
        ]
    }

    def __init__(self):
        super().__init__(
            name="DiagnosticAgent",
            role="Assess knowledge gaps via adaptive quiz evaluation"
        )

    def get_questions(self, topics: list[str]) -> list[dict]:
        """Skill: Fetch relevant questions for selected topics."""
        questions = []
        for topic in topics:
            bank = self.QUESTION_BANK.get(topic, [])
            questions.extend(bank)
        self.log(f"Fetched {len(questions)} questions for topics: {topics}")
        return questions

    def analyze_gaps(self, topic: str, confidence_scores: dict[str, int]) -> dict:
        """
        Skill: Analyze self-reported confidence (0-100) per topic
        and return a structured gap report.
        """
        self.log(f"Analysing gaps for topic '{topic}'...")

        gap_report = {
            "topic": topic,
            "overall_score": 0,
            "proficiency_level": "",
            "weak_areas": [],
            "strong_areas": [],
            "priority_gaps": [],
            "estimated_refresh_hours": 0
        }

        if not confidence_scores:
            return gap_report

        scores = list(confidence_scores.values())
        avg = sum(scores) / len(scores)
        gap_report["overall_score"] = round(avg)

        # Classify proficiency
        if avg < 30:
            gap_report["proficiency_level"] = "Beginner (Restart from basics)"
            gap_report["estimated_refresh_hours"] = 15
        elif avg < 60:
            gap_report["proficiency_level"] = "Intermediate (Targeted refresh)"
            gap_report["estimated_refresh_hours"] = 8
        else:
            gap_report["proficiency_level"] = "Advanced (Quick brushup)"
            gap_report["estimated_refresh_hours"] = 3

        # Classify subtopics
        for subtopic, score in confidence_scores.items():
            readable = subtopic.replace("_", " ").title()
            if score < 40:
                gap_report["weak_areas"].append(readable)
                gap_report["priority_gaps"].append({
                    "subtopic": readable,
                    "score": score,
                    "urgency": "High" if score < 20 else "Medium"
                })
            else:
                gap_report["strong_areas"].append(readable)

        # Sort priority gaps by score (lowest first)
        gap_report["priority_gaps"].sort(key=lambda x: x["score"])

        self.log(f"Gap analysis complete. Level: {gap_report['proficiency_level']}")
        return gap_report

    def run(self, topics: list[str], confidence_map: dict) -> dict:
        self.log(f"Starting diagnostic for {len(topics)} topics...")
        results = {}
        for topic in topics:
            topic_confidence = confidence_map.get(topic, {})
            results[topic] = self.analyze_gaps(topic, topic_confidence)
        self.log("Diagnostic complete.")
        return results


# ─────────────────────────────────────────────
# 3. ROADMAP ARCHITECT
# ─────────────────────────────────────────────

class RoadmapArchitect(BaseAgent):
    """
    Creates a personalised, time-boxed Refresher Roadmap based
    on the DiagnosticAgent's gap report.

    Skill: build_roadmap(gap_reports, timeline_weeks) → roadmap
    """

    PHASE_TEMPLATES = {
        "Beginner (Restart from basics)": [
            {"phase": 1, "name": "Foundation Reset", "focus": "Core syntax & concepts", "week_share": 0.4},
            {"phase": 2, "name": "Applied Practice", "focus": "Worked examples & exercises", "week_share": 0.4},
            {"phase": 3, "name": "Mini Project",    "focus": "Build something small end-to-end", "week_share": 0.2}
        ],
        "Intermediate (Targeted refresh)": [
            {"phase": 1, "name": "Gap Bridging",   "focus": "Revisit weak areas only", "week_share": 0.35},
            {"phase": 2, "name": "Pattern Mastery", "focus": "Common patterns & idioms", "week_share": 0.35},
            {"phase": 3, "name": "Project Sprint",  "focus": "Apply to a real problem", "week_share": 0.30}
        ],
        "Advanced (Quick brushup)": [
            {"phase": 1, "name": "Spot Review",    "focus": "Skim notes & revisit edge cases", "week_share": 0.50},
            {"phase": 2, "name": "Challenge Mode", "focus": "Tackle a hard project or competition", "week_share": 0.50}
        ]
    }

    def __init__(self):
        super().__init__(
            name="RoadmapArchitect",
            role="Generate personalised week-by-week refresher roadmaps"
        )

    def build_roadmap(self, gap_reports: dict, timeline_weeks: int = 4) -> dict:
        """Skill: Construct a phased roadmap from gap analysis results."""
        self.log(f"Building roadmap for {len(gap_reports)} topics over {timeline_weeks} weeks...")

        roadmap = {
            "title": "Your Personalised Tech-Restart Roadmap",
            "generated_at": datetime.utcnow().isoformat(),
            "timeline_weeks": timeline_weeks,
            "topics": [],
            "weekly_schedule": [],
            "total_hours_required": 0,
            "daily_commitment_minutes": 0
        }

        total_hours = 0

        for topic, gap_report in gap_reports.items():
            level = gap_report.get("proficiency_level", "Beginner (Restart from basics)")
            hours = gap_report.get("estimated_refresh_hours", 8)
            total_hours += hours

            phases = self.PHASE_TEMPLATES.get(level, self.PHASE_TEMPLATES["Intermediate (Targeted refresh)"])

            topic_plan = {
                "topic": topic.replace("_", " ").title(),
                "raw_topic": topic,
                "proficiency_level": level,
                "total_hours": hours,
                "score": gap_report.get("overall_score", 50),
                "weak_areas": gap_report.get("weak_areas", []),
                "phases": []
            }

            for p in phases:
                phase_hours = round(hours * p["week_share"], 1)
                phase_weeks = math.ceil(phase_hours / (hours / max(timeline_weeks, 1)))
                topic_plan["phases"].append({
                    "phase": p["phase"],
                    "name": p["name"],
                    "focus": p["focus"],
                    "hours": phase_hours,
                    "milestones": self._generate_milestones(topic, gap_report, p["phase"])
                })

            roadmap["topics"].append(topic_plan)

        # Build weekly schedule
        roadmap["total_hours_required"] = round(total_hours, 1)
        total_minutes = total_hours * 60
        days = timeline_weeks * 7
        roadmap["daily_commitment_minutes"] = round(total_minutes / days)

        roadmap["weekly_schedule"] = self._generate_weekly_schedule(
            roadmap["topics"], timeline_weeks
        )

        self.log(f"Roadmap built. Total: {total_hours}h over {timeline_weeks} weeks.")
        return roadmap

    def _generate_milestones(self, topic: str, gap_report: dict, phase: int) -> list[str]:
        """Generate concrete milestones per phase per topic."""
        weak = gap_report.get("weak_areas", [])
        strong = gap_report.get("strong_areas", [])
        level = gap_report.get("proficiency_level", "Intermediate (Targeted refresh)")

        milestone_map = {
            "python": {
                1: ["Complete syntax review notebook", "Write 10 functions from scratch", "Understand list/dict comprehensions"],
                2: ["Solve 5 LeetCode Easy problems in Python", "Build a file-processing script"],
                3: ["Create a personal CLI tool using argparse"]
            },
            "machine_learning": {
                1: ["Re-read bias-variance tradeoff notes", "Rebuild a linear regression from scratch"],
                2: ["Train a Random Forest on Titanic dataset", "Tune hyperparameters with GridSearchCV"],
                3: ["Submit to a beginner Kaggle competition"]
            },
            "deep_learning": {
                1: ["Review forward/backward pass math", "Implement a 2-layer NN in NumPy"],
                2: ["Build an image classifier with Keras", "Experiment with batch normalisation"],
                3: ["Fine-tune a pre-trained model on a custom dataset"]
            },
            "javascript": {
                1: ["Re-read MDN closures & scope guide", "Rewrite 5 functions using modern ES6+ syntax"],
                2: ["Build a DOM manipulation mini-app", "Implement a fetch-based weather widget"],
                3: ["Build a full To-Do app with localStorage persistence"]
            },
            "nlp": {
                1: ["Review tokenisation and word vectors", "Run a basic TF-IDF pipeline"],
                2: ["Fine-tune a Hugging Face model", "Build a sentiment classifier"],
                3: ["Deploy a small text classification API"]
            },
            "data_analysis": {
                1: ["Complete Kaggle Pandas exercises", "Review groupby + merge operations"],
                2: ["Perform a full EDA on a Kaggle dataset", "Create 5 meaningful visualisations"],
                3: ["Publish an EDA notebook on Kaggle"]
            }
        }

        default = {
            1: [f"Review core {topic.replace('_',' ')} concepts", "Take notes on weak areas"],
            2: [f"Complete 3 practice exercises in {topic.replace('_',' ')}", "Identify remaining blockers"],
            3: [f"Build a small project using {topic.replace('_',' ')}"]
        }

        milestones = milestone_map.get(topic, default).get(phase, default.get(phase, []))

        # Inject personalised gaps
        if weak and phase == 1:
            milestones.insert(0, f"Focus first on: {weak[0]}")

        return milestones

    def _generate_weekly_schedule(self, topics: list[dict], weeks: int) -> list[dict]:
        """Distribute topics across weeks."""
        schedule = []
        for week in range(1, weeks + 1):
            week_topics = []
            for t in topics:
                phase_index = min(week - 1, len(t["phases"]) - 1)
                phase = t["phases"][phase_index]
                week_topics.append({
                    "topic": t["topic"],
                    "phase": phase["name"],
                    "focus": phase["focus"],
                    "daily_hours": round(phase["hours"] / 7, 1)
                })
            schedule.append({
                "week": week,
                "theme": f"Week {week}: {week_topics[0]['phase'] if week_topics else 'Review'}",
                "topics": week_topics
            })
        return schedule

    def run(self, gap_reports: dict, timeline_weeks: int = 4) -> dict:
        return self.build_roadmap(gap_reports, timeline_weeks)


# ─────────────────────────────────────────────
# 4. RESOURCE SCOUT (MCP Client)
# ─────────────────────────────────────────────

class ResourceScout(BaseAgent):
    """
    Fetches curated learning resources from the local MCP Server
    (backed by course_library.json).

    Skill: scout_resources(topic, level) → resource_list
    """

    def __init__(self, library_path: str = "course_library.json"):
        super().__init__(
            name="ResourceScout",
            role="Fetch curated resources from local MCP course library"
        )
        self.library_path = library_path
        self._library: Optional[dict] = None

    def _load_library(self) -> dict:
        """MCP Tool: Load the local course library."""
        if self._library:
            return self._library
        try:
            with open(self.library_path, "r") as f:
                self._library = json.load(f)
            self.log(f"MCP Library loaded from '{self.library_path}'")
        except FileNotFoundError:
            self.log(f"WARNING: Library file not found at '{self.library_path}'")
            self._library = {"courses": {}, "topic_aliases": {}}
        return self._library

    def scout_resources(self, topic: str, level: str) -> list[dict]:
        """
        Skill: Retrieve resources for a topic at a given proficiency level.
        Level is normalised to 'beginner' or 'intermediate'.
        """
        library = self._load_library()
        courses = library.get("courses", {})
        aliases = library.get("topic_aliases", {})

        # Resolve aliases (e.g. 'ml' → 'machine_learning')
        resolved_topic = aliases.get(topic, topic)
        topic_courses = courses.get(resolved_topic, {})

        if not topic_courses:
            self.log(f"No resources found for topic '{topic}' (resolved: '{resolved_topic}')")
            return []

        # Normalise level
        norm_level = "beginner" if "Beginner" in level else "intermediate"

        resources = topic_courses.get(norm_level, [])

        # Supplement with the other level's first item if thin
        if len(resources) < 2:
            other_level = "intermediate" if norm_level == "beginner" else "beginner"
            resources += topic_courses.get(other_level, [])[:1]

        self.log(f"Found {len(resources)} resources for {resolved_topic}/{norm_level}")
        return resources

    def run(self, gap_reports: dict, roadmap: dict) -> dict:
        """Scout resources for every topic in the roadmap."""
        self.log("Scouting resources for all roadmap topics...")
        resource_map = {}

        for topic_plan in roadmap.get("topics", []):
            raw_topic = topic_plan.get("raw_topic", "")
            level = topic_plan.get("proficiency_level", "Intermediate")
            resources = self.scout_resources(raw_topic, level)
            resource_map[raw_topic] = {
                "topic": topic_plan["topic"],
                "level": level,
                "resources": resources
            }

        self.log(f"Resource scouting complete for {len(resource_map)} topics.")
        return resource_map


# ─────────────────────────────────────────────
# 5. AGENT ORCHESTRATOR
# ─────────────────────────────────────────────

class AgentOrchestrator:
    """
    Coordinates the three-agent pipeline:
      DiagnosticAgent → RoadmapArchitect → ResourceScout
    
    Implements the Agent SDK pattern: sequential delegation with
    shared context passed between agents.
    """

    def __init__(self, library_path: str = "course_library.json"):
        self.diagnostic   = DiagnosticAgent()
        self.architect    = RoadmapArchitect()
        self.scout        = ResourceScout(library_path=library_path)
        self.session_log: list[str] = []

    def _collect_logs(self):
        logs = []
        for agent in [self.diagnostic, self.architect, self.scout]:
            logs.extend(agent.get_logs())
        return logs

    def sanitize_input(self, data: dict) -> dict:
        """
        Security: Strip HTML tags, limit string lengths,
        validate numeric ranges, and reject unknown topics.
        """
        ALLOWED_TOPICS = {
            "python", "machine_learning", "deep_learning",
            "javascript", "nlp", "data_analysis", "ai_agents",
            "ml", "dl", "js", "data", "pandas", "agents"
        }
        MAX_STR_LEN = 200

        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Strip HTML tags
                clean = re.sub(r'<[^>]+>', '', value)
                # Trim to max length
                clean = clean[:MAX_STR_LEN]
                sanitized[key] = clean

            elif isinstance(value, list):
                sanitized[key] = [
                    item for item in value
                    if isinstance(item, str) and item in ALLOWED_TOPICS
                ]

            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = {}
                for k, v in value.items():
                    if isinstance(v, (int, float)):
                        # Clamp confidence scores to 0-100
                        sanitized[key][k] = max(0, min(100, int(v)))
                    elif isinstance(v, dict):
                        sanitized[key][k] = {
                            sk: max(0, min(100, int(sv)))
                            for sk, sv in v.items()
                            if isinstance(sv, (int, float))
                        }
                    else:
                        sanitized[key][k] = v

            elif isinstance(value, (int, float)):
                sanitized[key] = value

            else:
                sanitized[key] = value

        return sanitized

    def run_pipeline(self, raw_input: dict) -> dict:
        """
        Full pipeline:
          1. Sanitize inputs
          2. DiagnosticAgent  → gap_reports
          3. RoadmapArchitect → roadmap
          4. ResourceScout    → resources
          5. Return consolidated result
        """
        print("\n" + "="*60)
        print(" TECH-RESTART AGENT PIPELINE STARTING")
        print("="*60)

        # Step 0: Sanitize
        safe_input = self.sanitize_input(raw_input)
        topics          = safe_input.get("topics", [])
        confidence_map  = safe_input.get("confidence_map", {})
        timeline_weeks  = max(1, min(12, int(safe_input.get("timeline_weeks", 4))))
        student_name    = safe_input.get("student_name", "Student")

        if not topics:
            return {"error": "No valid topics provided after sanitisation."}

        # Step 1: Diagnostic
        print("\n[PIPELINE] Step 1 → DiagnosticAgent")
        gap_reports = self.diagnostic.run(topics, confidence_map)

        # Step 2: Roadmap
        print("\n[PIPELINE] Step 2 → RoadmapArchitect")
        roadmap = self.architect.run(gap_reports, timeline_weeks)
        roadmap["student_name"] = student_name

        # Step 3: Resources
        print("\n[PIPELINE] Step 3 → ResourceScout (MCP)")
        resources = self.scout.run(gap_reports, roadmap)

        # Attach resources into roadmap topics for convenience
        for topic_plan in roadmap["topics"]:
            raw = topic_plan.get("raw_topic", "")
            topic_plan["resources"] = resources.get(raw, {}).get("resources", [])

        print("\n[PIPELINE] ✅ All agents complete.\n")

        return {
            "status": "success",
            "student_name": student_name,
            "gap_reports": gap_reports,
            "roadmap": roadmap,
            "resources": resources,
            "agent_logs": self._collect_logs(),
            "pipeline_version": "1.0.0"
        }


# ─────────────────────────────────────────────
# 6. FLASK API ROUTES
# ─────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "course_library.json")
orchestrator = AgentOrchestrator(library_path=LIBRARY_PATH)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "Tech-Restart Learning Companion",
        "agents": ["DiagnosticAgent", "RoadmapArchitect", "ResourceScout"],
        "version": "1.0.0"
    })


@app.route("/api/questions", methods=["POST"])
def get_questions():
    """Return quiz questions for selected topics."""
    data = request.get_json(force=True)
    safe = orchestrator.sanitize_input(data)
    topics = safe.get("topics", [])
    questions = orchestrator.diagnostic.get_questions(topics)
    return jsonify({"status": "success", "questions": questions})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Run the full multi-agent pipeline."""
    data = request.get_json(force=True)
    result = orchestrator.run_pipeline(data)
    return jsonify(result)


@app.route("/api/resources", methods=["POST"])
def get_resources():
    """Scout resources for a topic directly."""
    data = request.get_json(force=True)
    safe = orchestrator.sanitize_input(data)
    topic = safe.get("topic", "")
    level = safe.get("level", "Intermediate (Targeted refresh)")
    resources = orchestrator.scout.scout_resources(topic, level)
    return jsonify({"status": "success", "resources": resources})


if __name__ == "__main__":
    print("\n🚀 Tech-Restart Learning Companion Backend")
    print("   Agents: DiagnosticAgent | RoadmapArchitect | ResourceScout")
    print("   Running on: http://localhost:5000\n")
    app.run(debug=True, port=5000)
