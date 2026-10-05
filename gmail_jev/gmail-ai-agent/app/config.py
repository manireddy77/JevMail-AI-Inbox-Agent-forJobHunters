import os
from dotenv import load_dotenv

load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ENABLE_CLEANUP = os.getenv("ENABLE_CLEANUP", "false").lower() == "true"

JEV_PROVIDER = os.getenv("JEV_PROVIDER", "openrouter").lower()
JEV_MODEL = os.getenv("JEV_MODEL", "typesafe/jev-latest")
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

SUMMARY_PROVIDER = os.getenv("SUMMARY_PROVIDER", "ollama")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

IMPORTANT_THRESHOLD = float(os.getenv("IMPORTANT_THRESHOLD", "0.70"))
ACTION_THRESHOLD = float(os.getenv("ACTION_THRESHOLD", "0.70"))
ADVERTISEMENT_THRESHOLD = float(os.getenv("ADVERTISEMENT_THRESHOLD", "0.95"))
SPAM_THRESHOLD = float(os.getenv("SPAM_THRESHOLD", "0.98"))

MAX_EMAILS_PER_RUN = int(os.getenv("MAX_EMAILS_PER_RUN", "50"))
MAX_EMAILS_PER_DAY = int(os.getenv("MAX_EMAILS_PER_DAY", "200"))

GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/email_agent.db")
