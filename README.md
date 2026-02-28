# 🚗 AutoAssist — Multi-Agent DIY Auto Repair AI System

Multi-agent AI system that transforms vague vehicle symptoms into structured, step-by-step DIY repair plans with human-in-the-loop safety checks and escalation logic.

---

## 🔍 Problem

Most car owners describe issues vaguely:
> "My car makes a weird noise."

DIY advice online is:
- Unstructured
- Risky
- Overwhelming
- Lacking safety validation

There is no structured workflow guiding users from symptom → diagnosis → safe repair plan.

---

## 💡 Solution

AutoAssist is an agentic AI workflow that:

1. Converts vague symptoms into structured diagnostic questions
2. Performs research & grounding
3. Verifies repair feasibility & safety
4. Generates beginner-friendly step-by-step plans
5. Escalates when DIY is unsafe

---

## 🧠 System Architecture

Multi-agent orchestration including:

- 🧭 Planner Agent — Structures the problem
- 🔎 Research Agent — Grounds information
- ✅ Verification Agent — Applies safety checks
- 🛠 Repair Agent — Generates structured repair plan
- 🚨 Escalation Logic — Determines when NOT to DIY

See full architecture: [architecture.md](architecture.md)

---

## ⚙️ How to Run

1. Open `notebooks/Demo_clean.ipynb`
2. Run all cells top-to-bottom
3. Enter a sample issue (e.g., "2015 Honda Civic brake squeal")
4. Review structured repair plan output

---

## 🛡 Responsible AI Features

- Human-in-the-loop verification
- Confidence scoring
- Safety guardrails
- Escalation logic for high-risk repairs

---

## 📈 Why This Is Hard to Copy

Competitors can copy:
- A chatbot
- A UI
- Basic LLM prompts

They cannot quickly replicate:
- Multi-agent decision orchestration
- Structured safety validation logic
- Accumulated workflow performance tuning
- Embedded escalation framework

---

## 🧰 Skills Demonstrated

- Agentic AI system design
- Multi-agent orchestration
- LLM workflow engineering
- Safety & guardrail implementation
- Applied AI architecture thinking
- Structured prompt engineering
- Python-based AI pipelines

---

## 🏷 Tech Stack

- Python
- Large Language Models (LLMs)
- Multi-Agent Architecture
- Prompt Engineering
- Structured Workflow Design

---

## 🎯 Project Context

Course: CIS 568 — AI & Business Strategy  
Spring 2026  
Arizona State University
