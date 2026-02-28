import os
import json
import time
import gradio as gr

from openai import OpenAI
from groq import Groq

# =========================
# 1) Secrets / Clients
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY. Add it in Space Settings → Variables and secrets → Secrets.")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY. Add it in Space Settings → Variables and secrets → Secrets.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

OPENAI_MODEL = "gpt-4.1-mini"
GROQ_MODEL = "llama-3.3-70b-versatile"


# =========================
# 2) Helpers
# =========================
HIGH_RISK_KEYWORDS = [
    "airbag", "srs", "brake line", "brake fluid leak", "fuel leak", "gas leak",
    "steering", "suspension", "timing belt", "engine knock", "transmission",
    "high voltage", "hybrid battery", "ev battery", "abs module"
]

def risk_screen(user_text: str) -> str:
    t = (user_text or "").lower()
    hits = [k for k in HIGH_RISK_KEYWORDS if k in t]
    if hits:
        return (
            "⚠️ **Safety Escalation Triggered**\n\n"
            f"Your request mentions potentially high-risk areas: {', '.join(hits)}.\n"
            "For v1, AutoAssist may still provide high-level guidance, but will recommend professional help "
            "for anything involving safety-critical systems.\n"
        )
    return ""

def groq_chat(system_prompt: str, user_prompt: str) -> str:
    start = time.time()
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    _ = time.time() - start
    return resp.choices[0].message.content.strip()

def openai_chat(system_prompt: str, user_prompt: str) -> str:
    start = time.time()
    resp = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    _ = time.time() - start
    return resp.choices[0].message.content.strip()

def openai_web_search_notes(system_prompt: str, user_prompt: str) -> str:
    """
    Uses OpenAI Responses API with the built-in web_search tool.
    If your account/plan doesn't allow web_search, replace this with openai_chat().
    """
    start = time.time()
    resp = openai_client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        tools=[{"type": "web_search"}],
    )
    _ = time.time() - start

    # Extract readable text
    # The Responses API returns output chunks; this pulls text parts when available.
    out_text = []
    for item in getattr(resp, "output", []) or []:
        for c in getattr(item, "content", []) or []:
            if getattr(c, "type", None) in ("output_text", "text"):
                out_text.append(getattr(c, "text", ""))
    text = "\n".join([t for t in out_text if t]).strip()

    # Fallback if parsing fails
    if not text:
        try:
            text = json.dumps(resp.model_dump(), indent=2)[:4000]
        except Exception:
            text = str(resp)[:4000]
    return text


# =========================
# 3) Agents
# =========================
def questioner(question: str) -> str:
    sys = (
        "You are a Questioner agent for car maintenance.\n"
        "Rewrite the user's input into a clear, structured question.\n"
        "Do NOT answer the question. Just rewrite it.\n"
        "Include vehicle year/make/model if present, and ask for missing key details briefly."
    )
    usr = (
        f"User input:\n{question}\n\n"
        "Return ONLY the rewritten question."
    )
    return groq_chat(sys, usr)

def researcher(question_2: str) -> str:
    sys = (
        "You are a Research agent for car maintenance.\n"
        "Goal: produce factual notes and sources.\n"
        "Be conservative: if uncertain, say what to verify."
    )
    usr = (
        f"Task: Research the best next steps for:\n{question_2}\n\n"
        "Return:\n"
        "1) Likely causes (bullets)\n"
        "2) Quick checks/diagnostic steps\n"
        "3) Parts/tools potentially needed\n"
        "4) Safety warnings\n"
        "5) Sources/links (bullets)\n"
        "Keep concise."
    )
    # Uses web_search tool:
    return openai_web_search_notes(sys, usr)

def verifier(question_2: str, research: str) -> str:
    sys = (
        "You are a Verifier agent.\n"
        "Evaluate research for clarity, safety, and fit to the exact vehicle/question.\n"
        "Do NOT rewrite the research."
    )
    usr = (
        f"Rewritten question:\n{question_2}\n\n"
        f"Research notes:\n{research}\n\n"
        "Output format:\n"
        "- Clarity score (1–5) + 2 fixes\n"
        "- Safety score (1–5) + 2 fixes\n"
        "- Fit-to-vehicle score (1–5) + 2 fixes\n"
        "- Any red flags / when to stop DIY (bullets)\n"
    )
    return groq_chat(sys, usr)

def planner(research: str, feedback: str, risk_note: str = "") -> str:
    sys = (
        "You are a Planner agent (experienced mechanic).\n"
        "Write a safe, beginner-friendly step-by-step plan.\n"
        "Use the research + verifier notes. If risk is high, recommend a professional."
    )
    usr = (
        f"{risk_note}\n"
        f"Research:\n{research}\n\n"
        f"Verifier feedback:\n{feedback}\n\n"
        "Return:\n"
        "A) Summary (2–3 bullets)\n"
        "B) Step-by-step plan (numbered)\n"
        "C) Tools list\n"
        "D) Parts list\n"
        "E) Safety checks / stop conditions\n"
        "F) Time estimate (rough)\n"
    )
    return openai_chat(sys, usr)

def assistant(instructions: str, followup: str) -> str:
    sys = (
        "You are an Assistant Research agent.\n"
        "Answer follow-up questions about the plan.\n"
        "Be factual and cite sources when possible."
    )
    usr = (
        f"Instructions:\n{instructions}\n\n"
        f"User follow-up:\n{followup}\n\n"
        "Return concise notes + sources."
    )
    return openai_web_search_notes(sys, usr)

def explainer(answer: str) -> str:
    sys = (
        "You are an Explainer agent.\n"
        "Turn research notes into a simple explanation a beginner understands.\n"
        "Be direct, safe, and helpful."
    )
    usr = (
        f"Follow-up research notes:\n{answer}\n\n"
        "Return a clear explanation (short paragraphs + bullets if needed)."
    )
    return openai_chat(sys, usr)


# =========================
# 4) Orchestration for UI
# =========================
def run_questioner(q):
    return questioner(q)

def run_research(q2):
    return researcher(q2)

def run_verifier(q2, r):
    return verifier(q2, r)

def run_planner(r, fb, original_user_question):
    risk_note = risk_screen(original_user_question)
    return planner(r, fb, risk_note=risk_note)

def run_assistant(instr, fu):
    if not fu or not fu.strip():
        return "Please type a follow-up question."
    return assistant(instr, fu)

def run_explainer(ans):
    return explainer(ans)


# =========================
# 5) Gradio App
# =========================
with gr.Blocks(title="AutoAssist — Agentic DIY Auto Repair") as app:
    gr.Markdown(
        "# 🚗 AutoAssist — Multi-Agent DIY Auto Repair\n"
        "Enter a car issue + vehicle details. The workflow will structure the problem, research, verify, and produce a safe plan.\n\n"
        "**Disclaimer:** Educational demo. For safety-critical repairs, consult a professional."
    )

    question = gr.Textbox(
        label="User Question (include year/make/model)",
        placeholder="Example: 2015 Honda Civic — brake squeal when stopping slowly. What should I check?",
        lines=3
    )

    gr.Markdown("## 1) Questioner Agent")
    btn_q = gr.Button("Rewrite Question")
    question_2 = gr.Textbox(label="Rewritten / Structured Question", lines=6)

    gr.Markdown("## 2) Research Agent (with web search)")
    btn_r = gr.Button("Research the Repair")
    research_box = gr.Textbox(label="Research Notes (editable)", lines=10)

    gr.Markdown("## 3) Verifier Agent")
    btn_v = gr.Button("Verify Research")
    feedback_box = gr.Textbox(label="Verifier Feedback", lines=10)

    gr.Markdown("## 4) Planner Agent (Final Instructions)")
    btn_p = gr.Button("Create Repair Plan")
    instructions_box = gr.Textbox(label="Repair Plan (editable)", lines=14)

    gr.Markdown("## 5) Follow-up Q&A")
    followup = gr.Textbox(label="Follow-up Question", placeholder="Ask about a step, tool, or safety warning...", lines=2)
    btn_a = gr.Button("Research Follow-up")
    answer_box = gr.Textbox(label="Follow-up Research Notes", lines=10)

    btn_e = gr.Button("Explain Clearly")
    explanation_box = gr.Textbox(label="Beginner-friendly Explanation", lines=10)

    # Wiring
    btn_q.click(fn=run_questioner, inputs=[question], outputs=[question_2])
    btn_r.click(fn=run_research, inputs=[question_2], outputs=[research_box])
    btn_v.click(fn=run_verifier, inputs=[question_2, research_box], outputs=[feedback_box])
    btn_p.click(fn=run_planner, inputs=[research_box, feedback_box, question], outputs=[instructions_box])
    btn_a.click(fn=run_assistant, inputs=[instructions_box, followup], outputs=[answer_box])
    btn_e.click(fn=run_explainer, inputs=[answer_box], outputs=[explanation_box])

app.launch()
