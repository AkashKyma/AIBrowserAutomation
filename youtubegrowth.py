from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------
# TASK: SUGGEST WAYS TO GROW A YOUTUBE CHANNEL
# --------------------------------------------
task = """
You are a professional YouTube strategist.

Give clear, practical, step-by-step suggestions for how someone can grow their YouTube channel fast.

Your strategy must include:

1. Content style & niche selection
2. SEO optimization (titles, tags, descriptions)
3. Thumbnail strategy
4. Posting schedule
5. Shorts strategy
6. How to increase watch time
7. How to improve click-through rate (CTR)
8. How to get more views organically
9. How to get more subscribers
10. Mistakes to avoid
11. Tools & analytics to track performance
12. Provide an example: 
    - 5 killer video ideas for a new YouTube channel
    - Titles and thumbnail text for each video
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

