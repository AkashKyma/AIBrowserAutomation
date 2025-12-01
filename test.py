from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os
import random
load_dotenv()
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
# List of positive comments to randomly choose from
COMMENTS = [
    "Great post! :+1:",
    "Love this! :heart:",
    "Amazing content!",
    "Awesome! :fire:",
    "This is so cool!",
    "Nice shot! :camera_with_flash:",
    "Very impressive!",
    "Beautiful! :heart_eyes:",
    "So inspiring!"
]
# This prints the values to confirm what's being used (remove these in production)
print(f"Username being used: {INSTAGRAM_USERNAME}")
print(f"Password being used: {INSTAGRAM_PASSWORD}")
task = f"""
Open the instagram.com and login with the given credentials.
"""
browser = Browser()
# Initialize the OpenAI chat model
llm = ChatOpenAI(model="gpt-5")
agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
)
async def main():
    await agent.run()
    input('Press Enter to close the browser...')
    await browser.close()