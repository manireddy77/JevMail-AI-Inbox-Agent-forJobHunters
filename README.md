# 📨 Gmail AI Agent for Job Seekers

A fully local, privacy-first AI agent that connects to your Gmail, cuts through the noise of your job hunt, and highlights the emails that actually matter.

Built with **Python**, **Flask**, **Ollama (llama3.2:3b)** for local insights, and **OpenRouter (Jev)** for structured decision routing.

![Gmail AI Dashboard](docs/dashboard.png)

## ✨ Features

- **Job-Seeker Focused Categories**: Explicitly trained to separate real human emails from automated noise.
  - 🔴 **Needs Response**: Real humans waiting for your reply, interview slots, or documents.
  - 🟢 **Shortlisted**: Interview invites and next steps.
  - 🟡 **Financial**: Genuine bank alerts and payments.
  - 🔵 **Has Info**: Actionable data (salaries, dates).
- **Aggressive Noise Filtering**: Silently skips platform notifications (LinkedIn, Indeed), auto-acknowledgments ("We received your application"), and promotional spam.
- **Local AI Insights**: Uses a local Ollama LLM to read the body of important emails and generate a 1-sentence summary of what you need to do, ensuring privacy.
- **Beautiful Web Dashboard**: A Flask-powered UI to review your emails by priority.
- **Safe Dry-Run Mode**: By default, it reads and categorizes emails without deleting or modifying anything in your actual Gmail inbox.

---

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/) installed on your machine.

### 2. Clone & Install
```bash
git clone https://github.com/yourusername/gmail-ai-agent.git
cd gmail-ai-agent

# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate
# Activate it (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Ollama (Local AI)
Start the Ollama background service on your computer, then pull the required model:
```bash
ollama pull llama3.2:3b
```

### 4. Setup API Keys
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and add your **OpenRouter API Key** (Get it free at [openrouter.ai](https://openrouter.ai/settings/keys)):
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
```

### 5. Setup Gmail Authentication
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API**.
3. Go to **APIs & Services > OAuth consent screen**. Set up the consent screen and **add your own email address** to the "Test users" list.
4. Go to **Credentials > Create Credentials > OAuth client ID** (Choose **Desktop app**).
5. Download the JSON file, rename it exactly to `credentials.json`, and place it in the root folder of this project.

Authenticate your app:
```bash
python -m app auth
```
*(This will open a browser to log in. Click Advanced -> Go to App (unsafe) since it's your personal testing app).*

---

## 💻 Usage

### 1. Process Your Inbox
Fetch your latest emails, classify them using Jev, and generate insights using local Ollama:
```bash
python -m app run --dry-run --limit 50
```
*(Pro-tip: If you want maximum speed and don't care about the 1-sentence AI insights, append `--skip-insights` to the command).*

### 2. Open the Dashboard
Launch the web UI to view your processed emails:
```bash
python -m app ui
```
Open your browser to: **http://127.0.0.1:5050**

---

## 📁 Project Structure

```
gmail-ai-agent/
├── app/
│   ├── classifier/     # AI prompts and decision routing rules
│   ├── database/       # SQLite logic for storing email states
│   ├── gmail/          # OAuth and Gmail API client
│   ├── jev/            # OpenRouter API integration
│   ├── summary/        # Local Ollama integration
│   ├── ui/             # Flask dashboard (templates/ and static/)
│   ├── cli.py          # Command Line Interface
│   └── main.py         # Core processing loop
├── data/               # Local SQLite database (auto-created)
├── docs/               # Documentation assets
├── logs/               # Application logs
├── .env                # Your configuration & keys (do not commit)
├── credentials.json    # Your Google OAuth credentials (do not commit)
└── requirements.txt    # Python dependencies
```

## 🛡️ Privacy & Security
- Emails are stored in a local SQLite database (`data/email_agent.db`).
- Insights are generated strictly on your local machine using Ollama.
- The `DRY_RUN=true` environment variable ensures the agent only reads emails and never deletes or labels anything in your live Gmail account unless explicitly disabled.
