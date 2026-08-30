# hello_agent.py — my very first AI agent 🤖

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled

# STEP 1: Load the secret key from the .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# STEP 2: Connect to Gemini (the "brain provider")
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(True)  # we're using Gemini, not OpenAI — turn off OpenAI logging

# STEP 3: Choose the brain (which Gemini model does the thinking)
brain = OpenAIChatCompletionsModel(
        model="gemini-3.6-flash",
    openai_client=client,
)

# STEP 4: Hire the agent — a NAME, a JOB (instructions), and a BRAIN
agent = Agent(
    name="Career Copilot",
    instructions="You are a warm, encouraging career coach who helps people land jobs.",
    model=brain,
)

# STEP 5: Give it a task and print the reply
result = Runner.run_sync(agent, "Introduce yourself in 2 short sentences and tell me you're ready to help me get hired.")
print("\n🤖 Your agent says:\n")
print(result.final_output)
print()