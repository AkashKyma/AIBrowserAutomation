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
    "Great post! 👍",
    "Love this! ❤️",
    "Amazing content!",
    "Awesome! 🔥",
    "This is so cool!",
    "Nice shot! 📸",
    "Very impressive!",
    "Beautiful! 😍",
    "So inspiring!"
]

# This prints the values to confirm what's being used (remove these in production)
print(f"Username being used: {INSTAGRAM_USERNAME}")
print(f"Password being used: {INSTAGRAM_PASSWORD}")

task = f"""
### Instagram Feed Scrolling and Commenting Task

**Objective:**
Log in to Instagram, scroll through the home feed, and leave comments on posts using specific stable selectors.

### Step 1: Navigate to Instagram and Login
- Go to Instagram.com
- Enter username: {INSTAGRAM_USERNAME}
- Enter password: {INSTAGRAM_PASSWORD}
- Click the login button
- Handle any popups that appear after login (like notifications, save login info, etc.)

### Step 2: Scroll through the Feed
- Once logged in, scroll down the main feed slowly
- Scroll through 10-15 posts to simulate natural browsing
- Pause briefly (2-3 seconds) at each post to simulate reading

### Step 3: Comment on Posts (DO NOT LIKE POSTS)
- For 4-5 posts, add a comment using these specific steps and selectors:

  1. First, locate and click the comment button using this XPath:
     "//div[@role='button'][.//svg[@aria-label='Comment']]"
     
  2. Once the comment area appears, find the textarea using:
     "//textarea[@aria-label='Add a comment…']"
     
  3. Click the textarea to focus it
     
  4. Type one of these comments randomly:
     - "{COMMENTS[0]}"
     - "{COMMENTS[1]}"
     - "{COMMENTS[2]}"
     - "{COMMENTS[3]}"
     - "{COMMENTS[4]}"
     - "{COMMENTS[5]}"
     - "{COMMENTS[6]}"
     - "{COMMENTS[7]}"
     - "{COMMENTS[8]}"
     
  5. After typing the comment, click the "Post" button using:
     "//div[@role='button' and (normalize-space()='Post' or .//span[normalize-space()='Post'])]"
     
  6. If the "Post" button is disabled, wait until aria-disabled!="true"
  
  7. If you encounter ElementClickIntercepted errors, use scrollIntoViewIfNeeded

- Wait 5-7 seconds between each comment to avoid triggering spam detection
- Continue scrolling down to see more posts if needed

### IMPORTANT NOTES:
- DO NOT CLICK ANY LIKE BUTTONS OR SHARE BUTTONS
- ONLY COMMENT ON POSTS - DO NOT PERFORM ANY OTHER INTERACTIONS
- Move at a natural pace to avoid triggering Instagram's bot detection
- Select public posts that appear to have good engagement already
- If any login verification or challenge appears, pause and notify
- If Instagram shows any warning about automated activity, stop immediately
- Avoid commenting on sensitive content or controversial topics
"""

browser = Browser()

# Initialize the OpenAI chat model
llm = ChatOpenAI(model="gpt-4o")

agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
)

async def main():
    await agent.run()
    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main()) 