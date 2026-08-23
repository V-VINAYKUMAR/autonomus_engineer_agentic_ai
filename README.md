# Autonomous Engineer

An autonomous software engineering loop: Planner → Orchestrator → Coder → Tester → Debugger → Reviewer,
driven by the Gemini API.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add your key to `.env`:

```
GEMINI_API_KEY=your_key_here
```

## Run

```bash
python3 engine.py
```
