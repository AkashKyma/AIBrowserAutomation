import asyncio
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import os

# -----------------------------------------
# FACEBOOK LOGIN CREDENTIALS
# -----------------------------------------

FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL") or "edgar.navarro@suroscuraec.com"
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD") or "Ruhani@123"

# -----------------------------------------
# REAL CHROME PROFILE (PERSISTENT SESSION)
# -----------------------------------------

browser = Browser(
    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    user_data_dir="/Users/akash/Library/Application Support/Google/Chrome",
    profile_directory="Default",
)

# -----------------------------------------
# TASK: AUTO-LOGIN + LIKE + COMMENT
# -----------------------------------------

task = f"""
You are a browser automation agent.

Goal:
Log in to Facebook AUTOMATICALLY using the credentials below.
If already logged in (session cookies saved), skip login.

Credentials:
- Email: {FACEBOOK_EMAIL}
- Password: {FACEBOOK_PASSWORD}

AFTER LOGIN:
- Go to Facebook home feed
- Like 5 posts
- Comment on 3 posts with "Nice post! 😊"

------------------------------------------
### STEP 1 — OPEN FACEBOOK
------------------------------------------
1. Navigate to https://www.facebook.com/

------------------------------------------
### STEP 2 — CHECK IF ALREADY LOGGED IN
------------------------------------------
2. If you see the home feed, skip login.

------------------------------------------
### STEP 3 — AUTO LOGIN
------------------------------------------
3. If login form is visible:
   - Enter email: "{FACEBOOK_EMAIL}"
   - Enter password: "{FACEBOOK_PASSWORD}"
   - Click the "Log In" button
   - Wait for Facebook to load the home feed

4. If CAPTCHA, identity check, or OTP appears:
   - STOP AUTOMATION
   - Notify the human user to solve it manually
   - After solved and feed loads, continue

------------------------------------------
### STEP 4 — LIKE & COMMENT ON POSTS
------------------------------------------
5. On the home feed:
   - Scroll slowly like a real human
   - For the first 5 posts:
        A. Like the post (only if not already liked)
        B. For 3 posts, leave comment: "Nice post! 😊"

6. Continue scrolling smoothly.

------------------------------------------
### STEP 5 — SUMMARY
------------------------------------------
7. Output:
   - Login success
   - Whether login was automatic or skipped
   - Number of posts liked
   - Number of comments posted
"""

agent = Agent(
    task=task,
    browser=browser,
    llm=ChatOpenAI(model="gpt-5"),
)

async def main():
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
    
