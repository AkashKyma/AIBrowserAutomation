from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------
# TASK: FIND LYRICS OF THE SONG "PARO" AND PRINT THEM
# -----------------------------------------------------
task = """
Your mission is to find and print the full lyrics of the song "Paro".

Steps:

1. Open Google.com.
2. Search for: Paro song lyrics.
3. Open any trusted lyrics website such as:
   - Genius.com
   - LyricsMint
   - AZLyrics
   - BollywoodMDB
   - ETC

4. Extract the FULL lyrics exactly as shown on the page.
   Do not rewrite the lyrics yourself — copy them exactly from the source.

5. After extracting the lyrics:
   - Print the lyrics clearly in your final output.
   - Format them as plain text, line by line.
   - Make sure no lines are missing.

6. If one lyrics website fails to load or blocks access:
   - Try another lyrics website.
   - Continue until you successfully find and print the lyrics.

Your final output MUST contain:
- The full lyrics of “Paro”
- Clean formatting
"""

browser = Browser()
llm = ChatOpenAI(model="gpt-4o")

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
