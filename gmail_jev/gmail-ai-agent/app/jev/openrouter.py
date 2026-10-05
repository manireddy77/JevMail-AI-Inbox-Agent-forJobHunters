import requests
import json
import time
from app.jev.base import JevProvider
from app.config import OPENROUTER_API_KEY, JEV_MODEL
from app.utils.logging import logger

class OpenRouterJevProvider(JevProvider):
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is missing")
        self.api_key = OPENROUTER_API_KEY
        self.model = JEV_MODEL
        self.endpoint = "https://openrouter.ai/api/alpha/decisions"

    def _build_questions(self, questions: dict) -> dict:
        formatted = {}
        for k, v in questions.items():
            q = {
                "type": v["type"],
                "instructions": v["instructions"]
            }
            if "criteria" in v:
                q["criteria"] = v["criteria"]
            elif v["type"] == "noul":
                q["criteria"] = {
                    "true": "Yes, this condition applies.",
                    "false": "No, this condition does not apply."
                }
            formatted[k] = q
        return formatted

    def _parse_response(self, data: dict, questions: dict) -> dict:
        """
        Parse OpenRouter Decisions API response.
        Expected response shape (based on official docs):
        {
          "nouls":   { "key": { "noul": 0.97 } },
          "choices": { "key": { "choice": "option_a" } },
          "scores":  { "key": { "score": "high" } }
        }
        """
        output = {}
        logger.debug(f"Raw Jev response keys: {list(data.keys())}")

        for k, v in questions.items():
            qtype = v["type"]
            if qtype == "noul":
                # The real API returns data["answers"]["key"]["noul"]
                val = (
                    data.get("answers", {}).get(k, {}).get("noul")
                    or data.get("nouls", {}).get(k, {}).get("noul")
                    or data.get("decisions", {}).get(k, {}).get("noul")
                    or data.get(k, {}).get("noul")
                )
                if val is not None:
                    output[f"{k}_probability"] = float(val)
                else:
                    logger.warning(f"Could not parse noul for '{k}' from response: {list(data.keys())}")
                    output[f"{k}_probability"] = 0.5
            elif qtype == "choice":
                val = (
                    data.get("choices", {}).get(k, {}).get("choice")
                    or data.get("decisions", {}).get(k, {}).get("choice")
                )
                output[f"{k}_choice"] = val or "unknown"
            elif qtype == "score":
                val = (
                    data.get("scores", {}).get(k, {}).get("score")
                    or data.get("decisions", {}).get(k, {}).get("score")
                )
                output[f"{k}_score"] = val or ""
        return output

    def classify(self, state: str, questions: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Gmail AI Agent"
        }

        formatted_questions = self._build_questions(questions)
        payload = {
            "model": self.model,
            "state": state,
            "questions": formatted_questions
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                start = time.time()
                response = requests.post(
                    self.endpoint, headers=headers, json=payload, timeout=30
                )
                latency = time.time() - start

                if response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited. Retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                if not response.ok:
                    logger.error(f"Jev API error {response.status_code}: {response.text[:300]}")
                    if response.status_code in (500, 502, 503, 504) and attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return {f"{k}_probability": 0.5 for k, v in questions.items() if v["type"] == "noul"}

                data = response.json()
                # Log full raw response at DEBUG level so we can diagnose format issues
                logger.debug(f"Jev raw response ({latency:.2f}s): {json.dumps(data)[:600]}")
                result = self._parse_response(data, questions)
                logger.debug(f"Parsed probabilities: {result}")
                return result

            except requests.exceptions.RequestException as e:
                logger.error(f"Network error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

        logger.warning("All retries failed. Returning safe REVIEW defaults.")
        return {f"{k}_probability": 0.5 for k, v in questions.items() if v["type"] == "noul"}

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model_name(self) -> str:
        return self.model
