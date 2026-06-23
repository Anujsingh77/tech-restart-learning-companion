"""
MCP Server — Tech-Restart Learning Companion
=============================================
A lightweight Model Context Protocol (MCP) server that exposes
course resources from a local JSON file over HTTP.

Endpoints:
  GET  /mcp/resources              → List all available topics
  GET  /mcp/resources/<topic>      → Get resources for a topic
  GET  /mcp/resources/<topic>/<lvl>→ Get resources at a specific level
  GET  /mcp/search?q=<query>       → Full-text search across resources
  GET  /mcp/status                 → MCP Server status

This runs on port 5001 (separate from the main backend on 5000).
"""

import json
import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "course_library.json")


def load_library() -> dict:
    """Load the course library from disk."""
    with open(LIBRARY_PATH, "r") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# MCP Protocol Helpers
# ─────────────────────────────────────────────

def mcp_response(data: dict, tool_name: str) -> dict:
    """Wrap a response in the MCP envelope format."""
    return {
        "mcp_version": "1.0",
        "tool": tool_name,
        "server": "tech-restart-mcp",
        "data": data
    }


def sanitize_query(q: str) -> str:
    """Strip HTML and limit length for search query safety."""
    clean = re.sub(r'<[^>]+>', '', q)
    return clean[:100].lower().strip()


# ─────────────────────────────────────────────
# MCP Endpoints
# ─────────────────────────────────────────────

@app.route("/mcp/status", methods=["GET"])
def mcp_status():
    library = load_library()
    topics = list(library.get("courses", {}).keys())
    return jsonify(mcp_response({
        "status": "online",
        "library_version": library.get("version", "unknown"),
        "last_updated": library.get("last_updated", "unknown"),
        "available_topics": topics,
        "total_topics": len(topics)
    }, tool_name="mcp_status"))


@app.route("/mcp/resources", methods=["GET"])
def list_resources():
    """MCP Tool: list_all_topics"""
    library = load_library()
    courses = library.get("courses", {})
    summary = {}
    for topic, levels in courses.items():
        count = sum(len(r) for r in levels.values())
        summary[topic] = {
            "levels": list(levels.keys()),
            "total_resources": count
        }
    return jsonify(mcp_response({
        "topics": summary,
        "aliases": library.get("topic_aliases", {})
    }, tool_name="list_all_topics"))


@app.route("/mcp/resources/<topic>", methods=["GET"])
def get_topic_resources(topic: str):
    """MCP Tool: get_resources_by_topic"""
    library = load_library()
    courses = library.get("courses", {})
    aliases = library.get("topic_aliases", {})

    resolved = aliases.get(topic, topic)
    topic_data = courses.get(resolved)

    if not topic_data:
        return jsonify({"error": f"Topic '{topic}' not found", "available": list(courses.keys())}), 404

    all_resources = []
    for level, resources in topic_data.items():
        for r in resources:
            all_resources.append({**r, "level": level})

    return jsonify(mcp_response({
        "topic": resolved,
        "alias_used": topic != resolved,
        "resources": all_resources
    }, tool_name="get_resources_by_topic"))


@app.route("/mcp/resources/<topic>/<level>", methods=["GET"])
def get_topic_level_resources(topic: str, level: str):
    """MCP Tool: get_resources_by_topic_and_level"""
    library = load_library()
    courses = library.get("courses", {})
    aliases = library.get("topic_aliases", {})

    resolved = aliases.get(topic, topic)
    topic_data = courses.get(resolved, {})

    norm_level = level.lower()
    if norm_level not in ["beginner", "intermediate"]:
        return jsonify({"error": "Level must be 'beginner' or 'intermediate'"}), 400

    resources = topic_data.get(norm_level, [])

    return jsonify(mcp_response({
        "topic": resolved,
        "level": norm_level,
        "count": len(resources),
        "resources": resources
    }, tool_name="get_resources_by_topic_and_level"))


@app.route("/mcp/search", methods=["GET"])
def search_resources():
    """MCP Tool: search_resources — full-text search across all resources."""
    raw_query = request.args.get("q", "")
    query = sanitize_query(raw_query)

    if not query or len(query) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400

    library = load_library()
    courses = library.get("courses", {})
    results = []

    for topic, levels in courses.items():
        for level, resources in levels.items():
            for r in resources:
                # Search in title, description, tags
                search_text = " ".join([
                    r.get("title", "").lower(),
                    r.get("description", "").lower(),
                    " ".join(r.get("tags", []))
                ])
                if query in search_text:
                    results.append({
                        **r,
                        "topic": topic,
                        "level": level,
                        "relevance_score": search_text.count(query)
                    })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return jsonify(mcp_response({
        "query": query,
        "count": len(results),
        "results": results
    }, tool_name="search_resources"))


if __name__ == "__main__":
    print("\n🔌 Tech-Restart MCP Server")
    print("   Protocol: Model Context Protocol v1.0")
    print("   Library:  course_library.json")
    print("   Running on: http://localhost:5001\n")
    app.run(debug=True, port=5001)
