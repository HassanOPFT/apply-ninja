# 🚀 Job Application Automation Platform

## Overview
This project automates the process of finding, reviewing, and applying to software engineering jobs across multiple job platforms (LinkedIn, Naukrigulf, Indeed, Glassdoor, etc.) using **Python**, **AI Agents SDK**, and **Playwright**.

You can approve or reject job listings manually through a CLI, and the system will automatically generate personalized cover letters and apply on your behalf.

## ✨ Features
- **Job Fetching:** Scrape jobs dynamically from various platforms.
- **Manual Review:** Review jobs via a CLI tool (Approve/Reject).
- **Automated Application:** Fill forms, upload CV, and submit with AI-generated cover letters.
- **Session Management:** Handles login sessions automatically without frequent manual authentication.
- **Configuration Driven:** Customize keywords, countries, resume path, etc.
- **Environment Variables:** Sensitive information like API keys is securely handled with `.env` files.

## 🏛️ Architecture
The system follows clean architecture and separation of concerns:
- **Agents Layer:** Handles job fetching, analysis, application, and session management.
- **Services Layer:** Business logic for job and application processing.
- **Database Layer:** Persistent storage for job listings and statuses (using SQLite).
- **Utils Layer:** OpenAI integration, config management, logging utilities.
- **CLI Layer:** Command-line tool for job approval/rejection.

## 📂 Project Structure
```
job-application-automation/
│
├── agents/
│   ├── job_fetch_agent.py
│   ├── job_analyzer_agent.py
│   ├── apply_agent.py
│   └── session_manager_agent.py
│
├── services/
│   ├── job_service.py
│   └── application_service.py
│
├── database/
│   ├── db.py
│   └── job_repository.py
│
├── utils/
│   ├── ai_generator.py
│   ├── config_loader.py
│   └── logger.py
│
├── cli/
│   └── review_jobs_cli.py
│
├── configs/
│   └── config.yaml
│
├── resumes/
│   └── resume.pdf
│
├── tests/
│   ├── test_job_service.py
│   ├── test_application_service.py
│   └── test_agents.py
│
├── .env.example
├── .env.development
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

## 🔑 Environment Variables Setup
All sensitive/customizable information is stored in `.env.development`.

Create a `.env.development` file based on `.env.example`:

```env
OPENAI_API_KEY=your-openai-api-key
LINKEDIN_EMAIL=your-linkedin-email
LINKEDIN_PASSWORD=your-linkedin-password
RESUME_PATH=resumes/resume.pdf
TARGET_COUNTRY=Saudi Arabia
JOB_KEYWORDS=Software Engineer,Backend Developer
DATABASE_URL=sqlite:///jobs.db
```

> **Important:** Never commit `.env.development` to GitHub. It's listed in `.gitignore`.

## 🧹 .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Environments
.env
.env.*
.venv/
venv/

# IDEs
.vscode/
.idea/

# Databases
*.db

# Playwright
playwright/.cache/
```

## 📦 Installation
Clone the repository:

```bash
git clone https://github.com/yourusername/job-application-automation.git
cd job-application-automation
```

Set up the virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Prepare environment:

```bash
cp .env.example .env.development
```
Fill in your values in `.env.development`.

## ⚙️ Configuration
Edit `configs/config.yaml` if needed:

```yaml
platforms:
  - LinkedIn
  - Naukrigulf
  - Indeed
  - Glassdoor
resume_path: "resumes/resume.pdf"
```

> **Note:** Environment variables will override YAML configs if both exist.

## 🚀 How to Run
Run the main system:

```bash
python main.py
```

Follow the CLI prompts to:
- Approve/Reject jobs
- Trigger automatic applications after approval

## 🛡️ Security
- No hardcoded passwords, API keys, or resume paths.
- All secrets and credentials are loaded from environment variables.
- Automated login uses Playwright's secure session management.

## 🔥 Future Improvements
- Add web dashboard for reviewing jobs.
- Telegram/Slack notifications when new jobs are fetched.
- Cloud deployment with database scaling.
- Auto-listening (real-time scraping) instead of fetching manually.

## 🛠️ Technologies Used
- Python 3.11+
- Playwright (Python)
- Agents SDK (Python)
- SQLite (PostgreSQL-ready later)
- OpenAI API
- YAML, ENV standards
- Rich CLI interface