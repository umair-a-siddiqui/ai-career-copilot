# resume_tailor.py — teammate #2: the RESUME TAILOR ✍️
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

# ---- 👇 YOUR JOB: write the Tailor's instructions ----
TAILOR_INSTRUCTIONS = """
WRITE ME!
"""

tailor = Agent(name="Resume Tailor", instructions=TAILOR_INSTRUCTIONS, model=brain)

RESUME = """
Paste your resume text here.
"""
JOB_POSTING = """
Paste the job posting text here.
"""

task = f"RESUME:\n{RESUME}\n\nJOB POSTING:\n{JOB_POSTING}\n\nRewrite the resume to fit this job."
result = Runner.run_sync(tailor, task)
print("\n✍️ Tailored resume:\n")
print(result.final_output)
print()