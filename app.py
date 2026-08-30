# app.py — JobJet 🚀 | AI Career Copilot
import os, re, asyncio
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from pypdf import PdfReader
import docx

# ---------- Ensure Event Loop ----------
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---------- Load API Credentials ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
set_tracing_disabled(True)
brain = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client)

# ---------- AI Agents Team ----------
analyst = Agent(
    name="Analyst",
    model=brain,
    instructions="""You are a strict ATS parser and senior recruiter.
Realistically compare the resume to the job posting.
Calculate an EXACT match score from 0-100 based strictly on actual keyword and skill overlap between resume and job posting.
DO NOT default to 75. If missing key qualifications, penalize heavily. If perfect, score high.
Start your response EXACTLY with: MATCH SCORE: <number>
Then list in markdown:
- 🟢 **Matched Hard Skills**
- 🔴 **Missing Critical Requirements**
- 💡 **Top 3 Upgrades Needed**"""
)

tailor = Agent(
    name="Resume Tailor",
    model=brain,
    instructions="""You are an expert resume writer. Rewrite the resume to fit the job using its keywords,
staying 100% truthful. Return the improved resume, then a short "What I changed" list. Use markdown."""
)

cover = Agent(
    name="Cover Letter Writer",
    model=brain,
    instructions="""Write a warm, confident 3-paragraph cover letter tailored to the job and resume. Under 250 words."""
)

coach = Agent(
    name="Interview Coach",
    model=brain,
    instructions="""Give 5 likely interview questions for this job, each with a 1-line tip on how to answer. Use markdown."""
)

# ---------- Helper Functions ----------
def read_file(f):
    if f is None: return ""
    name = f.name.lower()
    if name.endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(f).pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in docx.Document(f).paragraphs)
    return f.read().decode("utf-8", errors="ignore")

async def run_agent(agent, context, retries=3):
    delay = 5
    for attempt in range(retries):
        try:
            result = await Runner.run(agent, context)
            return result.final_output
        except RateLimitError:
            if attempt == retries - 1: raise
            await asyncio.sleep(delay)
            delay *= 2

async def run_team(context):
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

# ---------- Page Setup & Advanced Glassmorphism UI ----------
st.set_page_config(page_title="JobJet — AI Career Copilot", page_icon="🚀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1100px; }

/* Executive Header */
.hero-box {
    text-align: center;
    padding: 35px 20px 20px 20px;
    background: radial-gradient(circle at 50% -20%, rgba(108, 92, 231, 0.25) 0%, rgba(0, 0, 0, 0) 70%);
    border-radius: 20px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.hero-box h1 {
    font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -1.5px;
    background: linear-gradient(135deg, #a78bfa 0%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-box p { color: #94a3b8; font-size: 1.15rem; margin-top: 8px; }

/* Textarea styling */
.stTextArea textarea {
    background-color: #11141a !important;
    border: 1px solid #232834 !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem;
}
.stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.25) !important;
}

/* Action Button Glow */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.8rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    box-shadow: 0 4px 25px rgba(168, 85, 247, 0.4) !important;
    transition: all 0.2s ease-in-out !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 30px rgba(168, 85, 247, 0.6) !important;
}

/* Tab Container Styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #11141a;
    padding: 8px;
    border-radius: 14px;
    border: 1px solid #232834;
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #94a3b8;
    font-weight: 600;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header & Sidebar ----------
with st.sidebar:
    st.title("⚙️ JobJet Control")
    st.caption("AI Career Copilot v2.0")
    st.divider()
    st.markdown("### 🤖 Active Agents")
    st.markdown(
        "- 🕵️ **Analyst** (Keyword Matching)\n"
        "- ✍️ **Tailor** (ATS Optimization)\n"
        "- 💌 **Cover Letter** (Custom Pitch)\n"
        "- 🎤 **Coach** (Q&A Interview Prep)"
    )

st.markdown("""
<div class="hero-box">
  <h1>🚀 JobJet</h1>
  <p>AI-powered ATS Resume Tailoring, Cover Letters & Interview Coaching</p>
</div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("⚠️ `GEMINI_API_KEY` missing in `.env` file.")

# ---------- Inputs Section ----------
c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader("📄 Your Resume")
    uploaded = st.file_uploader("Upload PDF / Word / TXT", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    if uploaded is not None and st.session_state.get("_file") != uploaded.name:
        st.session_state["resume_text"] = read_file(uploaded)
        st.session_state["_file"] = uploaded.name
    st.text_area("Resume text", key="resume_text", height=280, label_visibility="collapsed",
                 placeholder="Paste resume text or upload a file above...")

with c2:
    st.subheader("💼 Job Description")
    st.text_area("Job text", key="job_text", height=336, label_visibility="collapsed",
                 placeholder="Paste the full job description text here (avoid raw links)...")

_, bcol, _ = st.columns([1, 2, 1])
with bcol:
    run = st.button("✨ Run AI Team")

# ---------- Run Pipeline ----------
if run:
    resume = st.session_state.get("resume_text", "").strip()
    job = st.session_state.get("job_text", "").strip()
    
    if not resume or not job:
        st.warning("Please provide BOTH your resume and full job description text.")
    else:
        with st.spinner("⚡ AI Agents are analyzing keywords and rewriting content..."):
            context = f"RESUME:\n{resume}\n\nJOB POSTING:\n{job}"
            try:
                loop = asyncio.get_event_loop()
                results = loop.run_until_complete(run_team(context))
                results["score"] = extract_score(results["analysis"])
                st.session_state["results"] = results
                st.balloons()
            except RateLimitError:
                st.error("⏳ Rate limit reached. Please wait a minute and try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Modern Results Dashboard ----------
res = st.session_state.get("results")
if res:
    st.markdown("---")
    
    # Custom Dynamic Score Card
    if res.get("score") is not None:
        score = res["score"]
        score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 24px; border-radius: 18px; text-align: center; margin-bottom: 30px;">
            <div style="color: #94a3b8; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Calculated Compatibility Score</div>
            <div style="color: {score_color}; font-size: 4.2rem; font-weight: 800; margin: 8px 0;">{score}%</div>
            <div style="background: #1e293b; border-radius: 10px; height: 12px; width: 100%; overflow: hidden;">
                <div style="background: {score_color}; height: 100%; width: {score}%; transition: width 1s ease-in-out;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    t1, t2, t3, t4 = st.tabs(["🕵️ Keyword Analysis", "✍️ ATS Tailored Resume", "💌 Custom Cover Letter", "🎤 Interview Prep"])
    with t1:
        st.markdown(res["analysis"])
    with t2:
        st.markdown(res["resume"])
        st.download_button("⬇️ Download Tailored Resume (.md)", res["resume"], file_name="tailored_resume.md")
    with t3:
        st.markdown(res["cover"])
        st.download_button("⬇️ Download Cover Letter (.md)", res["cover"], file_name="cover_letter.md")
    with t4:
        st.markdown(res["interview"])