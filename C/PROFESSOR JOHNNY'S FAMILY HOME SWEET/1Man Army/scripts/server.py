from flask import Flask, jsonify, Response
import json
from pathlib import Path

app = Flask(__name__)

MEMORY_FILE = Path.home() / "1man.army" / "memory" / "experience_log.json"

def load_memory():
    if not MEMORY_FILE.exists():
        return []
    with open(MEMORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

@app.route("/api/ai/log")
def get_log():
    memory = load_memory()
    log_text = ""
    for m in memory[-10:]:
        log_text += f"[{m.get('timestamp')}] {m.get('label')}:\n{m.get('output_snippet')[:200]}\n\n"
    return Response(log_text, mimetype="text/plain")

@app.route("/api/ai/alerts")
def get_alerts():
    memory = load_memory()
    danger_ports = {"21", "23", "445", "3389", "5900", "22"}
    hot_keywords = {"vulnerable", "exploit", "unauthorized", "malware"}
    alerts = []

    for m in memory[-10:]:
        output = m.get("output_snippet", "").lower()
        for port in danger_ports:
            if f"{port}/tcp" in output and "open" in output:
                alerts.append(f"⚠️ Port {port}/tcp OPEN")
        for word in hot_keywords:
            if word in output:
                alerts.append(f"🚨 Threat keyword found: {word}")

    return jsonify(alerts)

@app.route("/api/ai/suggestion")
def get_suggestion():
    memory = load_memory()
    if not memory:
        return Response("No memory available", mimetype="text/plain")

    tool_count = {}
    for m in memory:
        tool = m.get("label", "unknown")
        tool_count[tool] = tool_count.get(tool, 0) + 1

    sorted_tools = sorted(tool_count.items(), key=lambda x: x[1], reverse=True)
    if sorted_tools:
        top_tool, count = sorted_tools[0]
        return Response(f"Use '{top_tool}' — it was run {count} times. Tactical trend recommends it.", mimetype="text/plain")
    return Response("No pattern detected yet.", mimetype="text/plain")

import os

if __name__ == "__main__":
    debug_mode = os.getenv("APP_ENV", "production") == "development"
    app.run(debug=debug_mode, port=5000)
