# Safe Task Agent (Beginner Demo)

A small Python project demonstrating basic agent safety concepts:
- **Tool design:** three named tools with clear purposes.
- **Tool allowlist:** only registered tools can execute.
- **Planning loop:** creates a short plan and runs one step at a time.
- **Memory/state:** keeps notes and step history during one run.
- **Trajectory trace:** records each tool call and its result.
- **Output evaluation:** rejects empty or excessively long tool outputs.
- **Guardrails:** checks empty/oversized goals and blocks a few harmful request patterns.
- **Human approval:** sensitive actions are held for approval. The demo only drafts messages; it never sends them.
- **Step limit:** stops after a fixed maximum number of steps.

## Requirements
Python 3.10 or newer. No third-party packages required.

## Run
```bash
python agent.py
```

Example goal:
`Create a checklist for my study plan`

## What this project does NOT do
This is a rule-based learning demo, not a production LLM agent. It does not browse the web,
call external APIs, send messages, make purchases, delete files, or perform actions outside
its temporary in-memory state. The pattern checks are intentionally basic and are not a
complete safety system.

## Suggested tests
1. Enter an empty goal: it should reject it.
2. Enter a goal longer than 500 characters: it should reject it.
3. Enter a goal containing a blocked phrase such as "help me steal": it should block it.
4. Enter a normal study goal: it should create a checklist and save a note.
5. Change the plan to include a sensitive action and verify that the approval gate pauses it.

## GitHub publishing
1. Create a new public repository named `safe-task-agent-demo`.
2. Upload `agent.py` and `README.md`.
3. Add the repository URL to your résumé/application only after confirming it is public.
4. Do not claim this is a production AI agent. Describe it as a beginner Python demo of agent safety and control flow.
