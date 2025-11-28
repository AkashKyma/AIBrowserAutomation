from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio

# -----------------------------
# TASK: FIND & RECOMMEND MONITORS
# -----------------------------
task = """
Go to https://www.amazon.com.

If any popups (location, sign-in, cookies, etc.) appear, close or skip them.

Then:

1. Search for "computer monitor".
2. Focus on popular monitors (e.g., many reviews, good ratings).
3. Analyze at least 10–15 different monitors.

For each monitor you analyze, try to capture:
- Product name
- Screen size (in inches)
- Resolution (e.g., 1080p, 1440p, 4K)
- Refresh rate (e.g., 60Hz, 75Hz, 144Hz)
- Panel type if visible (IPS, VA, TN, OLED)
- Price
- Rating
- Number of reviews
- Product URL

Then, based on this data:
- Recommend the TOP 3–5 monitors overall.
- Explain briefly WHY each one is recommended (e.g., best value, best for gaming, best for office, etc.).

Finally, output:
1) A structured comparison table/list of all analyzed monitors.
2) A separate clear "Recommended Monitors" section with your top picks.
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
