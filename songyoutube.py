from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio

# -----------------------------------------
# TASK: PLAY "TUM TODO NA" ON YOUTUBE
# -----------------------------------------
task = """
Go to https://www.youtube.com.

If any popup like "accept cookies" or "sign in" appears, close or skip it.

Then:

1. Use the search bar to search for: Tum Todo Na song.
2. Look at the search results.
3. Play the official or most relevant video with highest views.
4. Ensure the video starts playing properly (full screen not necessary).
"""

# Initialize browser + LLM
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
