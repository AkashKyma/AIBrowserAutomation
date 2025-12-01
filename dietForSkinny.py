from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# TASK: SEARCH GOOGLE & FIND WEIGHT GAIN DIET FOR SKINNY GUY
# ---------------------------------------------------------
task = """
Your job is to search Google and find a good, high-calorie diet plan for a lean or skinny person 
who wants to gain weight.

Steps to follow:

1. Open https://www.google.com
2. Search: "best weight gain diet plan for skinny guys" or "high calorie diet for muscle gain"
3. Open 1–2 trusted websites such as:
   - Healthline
   - Medical News Today
   - NHS
   - WebMD
   - Any reputable nutrition blog

4. Extract the diet plan EXACTLY as shown:
   - Meals (breakfast, lunch, snacks, dinner)
   - Foods included
   - Estimated calories
   - Any tips or recommendations
   - Nutritional advice from the website

5. Summarize the results into ONE clear diet plan:
   - Breakfast
   - Mid-morning snack
   - Lunch
   - Evening snack
   - Dinner
   - Optional bedtime snack
   - Approximate calories per meal
   - Total daily calories estimate

6. DO NOT rewrite nutritional data on your own.
   Only extract what is written on the website.

7. In the final output:
   - Print the diet plan clearly
   - Organize it in bullet points or section format
   - Include source website names
"""

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
