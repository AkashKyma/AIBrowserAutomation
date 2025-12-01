from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio

# -----------------------------
# TASK: AMAZON ELECTRONICS LIST
# -----------------------------
task = """
Go to https://www.amazon.com.

If any popups or location dialogs appear, close or skip them.

Then:
1. Navigate to the 'Electronics' category (or search for 'Electronics').
2. Scroll through the results and collect at least 20 electronics products.

For each product, extract:
- Product name
- Price (or 'N/A' if not visible)
- Rating (or 'N/A')
- Number of reviews (or 'N/A')
- Product URL

At the end, produce a clean, structured list or table of all collected products in the final answer.
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
