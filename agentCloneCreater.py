from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
from dotenv import load_dotenv

# Load OPENAI_API_KEY etc. from .env if present
load_dotenv()

# -------------------------------------------------
# TASK: GO TO CHATGPT, CREATE 10 AGENTS, GET PYTHON
# -------------------------------------------------
task = """
Your identity: You are an autonomous web-browsing assistant built using the `browser_use` framework.
You are running inside a local Python environment controlled by the user.

Your high-level goal:
1) Go to ChatGPT on the web.
2) Create at least 10 assistant "agents" similar to yourself (e.g. Custom GPTs / assistants).
3) Make ChatGPT generate a Python agent script and present it clearly so the user can save it as a .py file.

Detailed steps:

A. OPEN CHATGPT
1. Open https://chatgpt.com or https://chat.openai.com in the browser.
2. If the page shows a login screen:
   - Do NOT try to enter username/password by yourself.
   - Instead, WAIT and allow the human user to log in manually.
   - Periodically check if the user is logged in (main chat UI visible).
3. Once logged in and on the main ChatGPT interface, continue.

B. NAVIGATE TO GPT CREATION AREA
1. Look for UI elements related to "GPTs", "Explore GPTs", "Create GPT", or "Create" in the sidebar or top nav.
2. If you find a section like "Explore GPTs" or "My GPTs", open it.
3. Find an option like "Create a GPT" / "Create new" / "New GPT".

C. CREATE AT LEAST 10 AGENTS LIKE YOURSELF
1. Your goal is to create at least 10 custom assistants (agents) similar in purpose:
   - They should be described as browser/web automation helpers,
   - Able to reason step-by-step,
   - Helpful, safe, and controllable by the user.

2. For each agent (aim for 10+):
   - Give it a unique but related name, e.g.
     - "Browser Agent 1", "Browser Agent 2", ..., "Browser Agent 10"
     - Or similar naming pattern.
   - In its instructions / system prompt area, paste a short instruction like:
     "You are a browser automation assistant that helps the user perform tasks on the web step-by-step. 
      You follow user instructions carefully, think clearly, and act safely."
   - Optionally fill a description, e.g.:
     "A helper agent that assists with web browsing, research, and automation."
   - Save the GPT/agent (look for a Save/Publish button).
   - After saving, go back to the GPT list and create the next one.

3. If there is any UI limitation (e.g. you can’t create more GPTs), create as many as possible
   and then proceed to the next phase.

D. ASK CHATGPT TO GENERATE A PYTHON AGENT SCRIPT
1. After creating the agents, open a new ChatGPT conversation (or use the same one).
2. In the ChatGPT message area, send a prompt requesting a Python file, for example:
   "Create a complete Python script that uses the `browser_use` library. 
    The script should:
    - Create a Browser()
    - Create an Agent with a given task
    - Use ChatOpenAI with model 'gpt-4o'
    - Run async main() with asyncio.run(main())
    Provide the full script in one ```python code block."

3. Wait for ChatGPT to answer.
4. Once ChatGPT gives the Python code, ensure:
   - The code block is complete.
   - It contains imports, task string, agent initialization, and asyncio.run(main()) pattern.

E. PRESENT THE PYTHON SCRIPT TO THE USER
1. Copy the entire Python code block content.
2. In your final output (to the user running this local script), clearly print the code so they can save it as a .py file.
3. Make sure it is shown as one contiguous block without missing lines.

Very important behavior:
- Do not log out of ChatGPT or change account settings.
- Never try to create or manage accounts; only operate within the already logged-in account.
- If any blocking issue occurs (e.g. unable to find Create GPT), describe what happened and still proceed with step D (asking ChatGPT to generate a Python script in a normal chat).
"""

# Initialize browser & model
browser = Browser()
llm = ChatOpenAI(model="gpt-5")

agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
)

async def main():
    await agent.run()
    input("Press Enter to close the browser...")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
