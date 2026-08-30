# main.py — the full AI Career Copilot team 🤝
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(True)
brain = OpenAIChatCompletionsModel(model="gemini-3.6-flash", openai_client=client)

# ---- The 4 teammates (tweak any instructions you like) ----
analyst = Agent(name="Analyst", model=brain, instructions="""
You are an expert technical recruiter. Compare the resume to the job posting.
Return: 1) Match Score 0-100, 2) matching skills, 3) missing skills, 4) top 3 fixes.""")

tailor = Agent(name="Resume Tailor", model=brain, instructions="""
You are an expert resume writer. Rewrite the resume to fit the job using its keywords,
staying 100% truthful. Return the improved resume + a short list of changes.""")

cover = Agent(name="Cover Letter Writer", model=brain, instructions="""
You are a professional cover-letter writer. Write a warm, confident 3-paragraph cover
letter tailored to the job and resume. Under 250 words.""")

coach = Agent(name="Interview Coach", model=brain, instructions="""
You are a friendly interview coach. Give 5 likely interview questions for this job,
each with a 1-line tip on how to answer.""")

# ---- YOUR INPUTS (paste once) ----
RESUME = """
Paste your resume text here.
"""
JOB_POSTING = """
Paste the job posting text here.
"""

# ---- Run the whole team ----
context = f"RESUME:\n{RESUME}\n\nJOB POSTING:\n{JOB_POSTING}"

print("\n🕵️ ANALYST\n");            print(Runner.run_sync(analyst, context).final_output)
print("\n✍️ TAILORED RESUME\n");     print(Runner.run_sync(tailor, context).final_output)
print("\n💌 COVER LETTER\n");        print(Runner.run_sync(cover, context).final_output)
print("\n🎤 INTERVIEW PREP\n");      print(Runner.run_sync(coach, context).final_output)