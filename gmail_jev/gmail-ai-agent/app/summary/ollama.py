import requests
from app.config import OLLAMA_BASE_URL, SUMMARY_MODEL
from app.utils.logging import logger


def is_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def generate_insight(subject: str, sender: str, body: str) -> str:
    """Generate a 1-2 sentence insight for an email using the local Ollama model."""
    if not is_ollama_running():
        return "Ollama not running — start it to get AI insights."

    prompt = f"""You are helping a job seeker manage their inbox.

Email:
From: {sender}
Subject: {subject}
Body (first 800 chars): {body[:800]}

In 1-2 short sentences, tell the user: what is this email about and what (if anything) should they do?
Be direct. No preamble."""

    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": SUMMARY_MODEL, "prompt": prompt, "stream": False},
            timeout=45
        )
        if r.status_code == 200:
            return r.json().get("response", "").strip()
        else:
            logger.warning(f"Ollama generate failed: {r.status_code}")
            return ""
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return ""
