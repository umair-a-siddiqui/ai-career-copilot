# app.py — JobJet 🚀 | AI Career Copilot
import os, re, time, asyncio
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from pypdf import PdfReader
import docx

# ---------- make sure this thread has an event loop (Streamlit needs it) ----------
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---------- connect to the Gemini "brain" ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
set_tracing_disabled(True)
brain = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite", openai_client=client)

# ---------- the AI team ----------
analyst = Agent(name="Analyst", model=brain, instructions="""
You are an expert technical recruiter. Compare the resume to the job posting.
Start your reply with a line EXACTLY like: MATCH SCORE: <number 0-100>
Then give: **✅ Matching skills**, **❌ Missing skills**, and **🛠️ Top 3 fixes**. Use clean markdown.""")
tailor = Agent(name="Resume Tailor", model=brain, instructions="""
You are an expert resume writer. Rewrite the resume to fit the job using its keywords,
staying 100% truthful. Return the improved resume, then a short "What I changed" list. Use markdown.""")
cover = Agent(name="Cover Letter Writer", model=brain, instructions="""
Write a warm, confident 3-paragraph cover letter tailored to the job and resume. Under 250 words.""")
coach = Agent(name="Interview Coach", model=brain, instructions="""
Give 5 likely interview questions for this job, each with a 1-line tip on how to answer. Use markdown.""")

# ---------- helpers ----------
def read_file(f):
    if f is None:
        return ""
    name = f.name.lower()
    if name.endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(f).pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in docx.Document(f).paragraphs)
    return f.read().decode("utf-8", errors="ignore")

async def run_agent(agent, context, retries=4):
    """Run one agent (async), auto-retrying if the free tier is rate-limited."""
    delay = 10
    for attempt in range(retries):
        try:
            result = await Runner.run(agent, context)
            return result.final_output
        except RateLimitError:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)

async def run_team(context):
    """Fire all 4 agents at the SAME time (parallel) instead of one-by-one."""
    analysis, resume_out, cover_out, interview_out = await asyncio.gather(
        run_agent(analyst, context),
        run_agent(tailor, context),
        run_agent(cover, context),
        run_agent(coach, context),
    )
    return {"analysis": analysis, "resume": resume_out,
            "cover": cover_out, "interview": interview_out}

def extract_score(text):
    m = re.search(r"MATCH SCORE:\s*(\d{1,3})", text, re.I) or re.search(r"(\d{1,3})\s*/\s*100", text)
    return max(0, min(100, int(m.group(1)))) if m else None

# ---------- page setup + custom styling ----------
st.set_page_config(page_title="JobJet — AI Career Copilot", page_icon="🚀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1150px; }
.hero { text-align: center; padding: 22px 0 6px 0; }
.hero h1 {
  font-size: 3.4rem; font-weight: 800; margin: 0; letter-spacing: -1px;
  background: linear-gradient(90deg, #6C5CE7, #00B894);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #6b7280; font-size: 1.15rem; margin-top: 6px; }
.stButton > button {
  background: linear-gradient(90deg, #6C5CE7, #8067f0);
  color: #fff; border: none; border-radius: 12px;
  padding: 0.75rem 1.4rem; font-weight: 600; font-size: 1.05rem; width: 100%;
  transition: transform .08s ease, box-shadow .2s ease;
  box-shadow: 0 6px 18px rgba(108, 92, 231, .35);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 26px rgba(108, 92, 231, .45); }
.stTextArea textarea { border-radius: 12px; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 16px; }
</style>
""", unsafe_allow_html=True)

# ---------- header ----------
st.markdown("""
<div class="hero">
  <h1>🚀 JobJet</h1>
  <p>Your AI team tailors your resume, writes your cover letter & preps your interview — in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ---------- sidebar ----------
with st.sidebar:
    st.header("🤖 Your AI Team")
    st.markdown(
        "- 🕵️ **Analyst** — scores your fit\n"
        "- ✍️ **Resume Tailor** — rewrites to match\n"
        "- 💌 **Cover Letter Writer** — drafts your letter\n"
        "- 🎤 **Interview Coach** — preps your answers"
    )
    st.divider()
    st.caption("HOW IT WORKS")
    st.markdown("1. Upload your resume\n2. Paste a job posting\n3. Hit **Run** ✨")
    st.divider()
    st.caption("Built with OpenAI Agents SDK + Google Gemini")

if not API_KEY:
    st.error("⚠️ No API key found — set `GEMINI_API_KEY` in Streamlit Secrets.")

# ---------- inputs ----------
c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader("📄 Your Resume")
    uploaded = st.file_uploader("Upload PDF / Word / TXT", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    if uploaded is not None and st.session_state.get("_file") != uploaded.name:
        st.session_state["resume_text"] = read_file(uploaded)
        st.session_state["_file"] = uploaded.name
    st.text_area("Resume text", key="resume_text", height=280, label_visibility="collapsed",
                 placeholder="Paste your resume here, or upload a file above…")
with c2:
    st.subheader("💼 Job Posting")
    st.text_area("Job text", key="job_text", height=336, label_visibility="collapsed",
                 placeholder="Paste the full job description here…")

_, bcol, _ = st.columns([1, 2, 1])
with bcol:
    run = st.button("✨ Run my AI team")

# ---------- run the team ----------
if run:
    resume = st.session_state.get("resume_text", "").strip()
    job = st.session_state.get("job_text", "").strip()
    if not resume or not job:
        st.warning("Please provide BOTH your resume and a job posting.")
    else:
        context = f"RESUME:\n{resume}\n\nJOB POSTING:\n{job}"
        try:
            with st.spinner("🤖 Your AI team is working — all 4 agents at once…"):
                loop = asyncio.get_event_loop()
                results = loop.run_until_complete(run_team(context))
            results["score"] = extract_score(results["analysis"])
            st.session_state["results"] = results
            st.balloons()
        except RateLimitError:
            st.error("⏳ Gemini's free tier is busy right now (rate limit). "
                     "Please wait about a minute, then click **Run** again.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ---------- show results ----------
res = st.session_state.get("results")
if res:
    st.markdown("---")
    if res.get("score") is not None:
        s = res["score"]
        m1, m2 = st.columns([1, 3])
        with m1:
            st.metric("🎯 Match Score", f"{s}/100")
        with m2:
            st.write("")
            st.progress(s / 100)
    t1, t2, t3, t4 = st.tabs(["🕵️ Analysis", "✍️ Tailored Resume", "💌 Cover Letter", "🎤 Interview Prep"])
    with t1:
        st.markdown(res["analysis"])
    with t2:
        st.markdown(res["resume"])
        st.download_button("⬇️ Download resume", res["resume"], file_name="tailored_resume.md")
    with t3:
        st.markdown(res["cover"])
        st.download_button("⬇️ Download cover letter", res["cover"], file_name="cover_letter.md")
    with t4:
        st.markdown(res["interview"])
