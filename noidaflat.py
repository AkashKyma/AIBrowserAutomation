from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio

# -----------------------------------------
# TASK: FIND GOOD RENTAL FLATS IN NOIDA
# -----------------------------------------
task = """
Your goal is to find good rental flats in Noida with decent space.

Steps:

1. Open a popular Indian real-estate/rental website.
   Prefer one of:
   - https://www.magicbricks.com
   - https://www.99acres.com
   - https://www.nobroker.in

   If one site fails to load or blocks you, try another from the list.

2. Search for flats/apartments for RENT in NOIDA (not Greater Noida, not Noida Extension unless clearly part of Noida).

3. Apply sensible filters:
   - Property type: Apartment/Flat (not PG, not hostel, not plot, not villa)
   - BHK: Prefer 2 BHK or 3 BHK
   - Budget: mid-range (avoid ultra-luxury very high-rent options)
   - Area / size: Prefer built-up area >= 900 sq.ft (more is better)
   - Family-friendly / decent locality if the site indicates this
   - Ignore clearly fake / duplicate / incomplete listings

4. From the listings, collect AT LEAST 10 good options.

For each shortlisted flat, capture:
- Title / short description
- Locality / Sector (e.g. Sector 62, Sector 76, Noida Extension etc. but prefer core Noida)
- BHK + bathrooms if visible
- Built-up area (sq.ft)
- Monthly rent
- Furnishing status (unfurnished / semi-furnished / furnished)
- Floor + total floors if visible
- Key amenities (parking, lift, security, etc., if visible)
- Distance/close to metro or main road if mentioned
- Listing URL

5. After collecting data:
   - Filter out clearly small / cramped flats or bad deals.
   - Rank and recommend the TOP 5–7 flats.
   - Consider: space, rent value, locality, amenities, and overall balance.

6. Output:
   1) A structured list or table of ALL collected flats.
   2) A clear "Recommended Flats in Noida for Rent" section with your top picks,
      each with a brief explanation of why it is recommended (e.g. best value,
      biggest space, near metro, good locality, etc.).
"""

# Initialize browser + LLM
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
