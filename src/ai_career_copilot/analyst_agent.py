# analyst_agent.py — the first real teammate: the ANALYST 🕵️
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled

# ---- Same Gemini setup as before ----
load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(True)
brain = OpenAIChatCompletionsModel(model="gemini-3.6-flash", openai_client=client)

# ---- 👇 YOUR JOB: write the Analyst's instructions (recipe below) ----
ANALYST_INSTRUCTIONS = """
WRITE ME!
"""

# ---- Hire the Analyst ----
analyst = Agent(name="Analyst", instructions=ANALYST_INSTRUCTIONS, model=brain)

# ---- The inputs ----
RESUME = """
Paste a short resume here (yours, or make one up for testing).
"""
JOB_POSTING = """
Paste a real job posting here (copy one from LinkedIn/Indeed).
"""

# ---- Run it ----
task = f"RESUME:\n{RESUME}\n\nJOB POSTING:\n{JOB_POSTING}\n\nAnalyze the match."
result = Runner.run_sync(analyst, task)
print("\n🕵️ Analyst says:\n")
print(result.final_output)
print()