from flask import Flask, jsonify, render_template, request
from app.database.db import get_all_emails, get_stats, init_db
from app.summary.ollama import is_ollama_running
from app.config import JEV_PROVIDER, JEV_MODEL, SUMMARY_MODEL

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/emails")
def api_emails():
    category = request.args.get("category", "")
    limit = int(request.args.get("limit", 200))
    emails = get_all_emails(limit=limit)
    for e in emails:
        if not e.get("category"):
            e["category"] = "REVIEW"

    if category and category != "ALL":
        emails = [e for e in emails if e["category"] == category]
    # Sort: NEEDS_RESPONSE first, then SHORTLISTED, etc.
    priority = {
        "NEEDS_RESPONSE": 0, "SHORTLISTED": 1, "FINANCIAL": 2,
        "HAS_INFO": 3, "REVIEW": 4, "REJECTION": 5,
        "SKIP_ACK": 6, "SKIP_PLATFORM": 7, "SKIP_PROMO": 8,
    }
    emails.sort(key=lambda e: priority.get(e.get("category", "REVIEW"), 9))
    return jsonify(emails)


@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    ollama = is_ollama_running()
    return jsonify({
        "stats": stats,
        "provider": JEV_PROVIDER,
        "model": JEV_MODEL,
        "summary_model": SUMMARY_MODEL,
        "ollama_running": ollama,
        "total": sum(stats.values()),
    })


def run_ui(host="127.0.0.1", port=5050, debug=False):
    init_db()
    print(f"\n✓ Gmail AI Dashboard running at http://{host}:{port}")
    print("  Press Ctrl+C to stop.\n")
    app.run(host=host, port=port, debug=debug)
