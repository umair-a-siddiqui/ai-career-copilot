# app.py — AI Career Copilot (web app) 🚀
import os, asyncio
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from pypdf import PdfReader
import docx

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(True)
brain = OpenAIChatCompletionsModel(model="gemini-3.6-flash", openai_client=client)

analyst = Agent(name="Analyst", model=brain, instructions="""
You are an expert technical recruiter. Compare the resume to the job posting.
Return: 1) Match Score 0-100, 2) matching skills, 3) missing skills, 4) top 3 fixes.""")
tailor = Agent(name="Resume Tailor", model=brain, instructions="""
You are an expert resume writer. Rewrite the resume to fit the job using its keywords,
staying 100% truthful. Return the improved resume + a short list of changes.""")
cover = Agent(name="Cover Letter Writer", model=brain, instructions="""
Write a warm, confident 3-paragraph cover letter tailored to the job and resume. Under 250 words.""")
coach = Agent(name="Interview Coach", model=brain, instructions="""
Give 5 likely interview questions for this job, each with a 1-line tip on how to answer.""")

# --- reads text out of an uploaded PDF / Word / TXT file ---
def read_file(f):
    if f is None:
        return ""
    name = f.name.lower()
    if name.endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(f).pages)
    if name.endswith(".docx"):
        return "\n".join(p.text for p in docx.Document(f).paragraphs)
    return f.read().decode("utf-8", errors="ignore")

st.set_page_config(page_title="AI Career Copilot", page_icon="🚀")
st.title("🚀 AI Career Copilot")
st.write("Upload your resume + paste a job posting. Your AI team does the rest.")

uploaded = st.file_uploader("📄 Upload your resume (PDF / Word / TXT)", type=["pdf", "docx", "txt"])
resume = st.text_area("…or paste/edit your resume here", value=read_file(uploaded), height=200)
job = st.text_area("💼 Job Posting", height=200)

if st.button("Run my AI team ✨"):
    if not resume or not job:
        st.warning("Please provide BOTH your resume and the job posting.")
    else:
        context = f"RESUME:\n{resume}\n\nJOB POSTING:\n{job}"
        t1, t2, t3, t4 = st.tabs(["🕵️ Analysis", "✍️ Resume", "💌 Cover Letter", "🎤 Interview"])
        with t1:
            with st.spinner("Analyzing..."): st.markdown(Runner.run_sync(analyst, context).final_output)
        with t2:
            with st.spinner("Tailoring..."): st.markdown(Runner.run_sync(tailor, context).final_output)
        with t3:
            with st.spinner("Writing..."): st.markdown(Runner.run_sync(cover, context).final_output)
        with t4:
            with st.spinner("Prepping..."): st.markdown(Runner.run_sync(coach, context).final_output)