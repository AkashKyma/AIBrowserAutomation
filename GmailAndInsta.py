from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# CONFIG: INSTAGRAM LOGIN + LIKE & COMMENT ON PROFILE POSTS
# -----------------------------------------

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME") or "edgar.navarro@suroscuraec.com"
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD") or "Ruhani@123"

INSTAGRAM_TARGET_PROFILE = os.getenv("INSTAGRAM_TARGET_PROFILE") or "instagram"
NUM_POSTS_TO_INTERACT = int(os.getenv("INSTAGRAM_NUM_POSTS", 5))
COMMENT_TEXT = os.getenv("INSTAGRAM_COMMENT_TEXT") or "Nice post! 😊"

# -----------------------------------------
# TASK WITH SAFE OTP FLOW
# -----------------------------------------

task = f"""
You are a browser automation agent.

Goal:
Log in to Instagram with the given credentials. 
If Instagram asks for a verification code (OTP), open Gmail in a new tab so the HUMAN USER can manually retrieve the OTP.
After the user manually enters the OTP into Instagram and login completes, continue the automation:
- Like posts
- Comment on posts on the specified profile

Credentials:
- Username: {INSTAGRAM_USERNAME}
- Password: {INSTAGRAM_PASSWORD}

Target profile:
- {INSTAGRAM_TARGET_PROFILE}


1. Go to https://www.instagram.com/.
2. Handle any popups (cookies, login dialogs, "Save Login Info", "Turn on Notifications", etc.) by closing or accepting them as needed.

3. Check if the user is already logged in:
   - If already logged in, continue to step 4.
   - If not logged in:
     - Find the username input field (usually labeled "Phone number, username, or email" or similar).
     - Find the password input field.
     - Type the given credentials in a human-like manner:
       - Username: {INSTAGRAM_USERNAME}
       - Password: {INSTAGRAM_PASSWORD}
     - Click the "Log in" button and wait until the main Instagram UI is loaded.
     - Dismiss "Save login info" and "Turn on notifications" dialogs to continue.

# --------------------------------------------------------
# ### STEP 1 — OPEN INSTAGRAM
# --------------------------------------------------------
# 1. Navigate to https://www.instagram.com/.
# 2. Close cookies or popup dialogs.

# --------------------------------------------------------
# ### STEP 2 — LOGIN ATTEMPT
# --------------------------------------------------------
# 3. If not already logged in:
#    - Enter username: "{INSTAGRAM_USERNAME}"
#    - Enter password: "{INSTAGRAM_PASSWORD}"
#    - Click "Log in"

# --------------------------------------------------------
# ### STEP 3 — OTP / SECURITY CODE HANDLING (SAFE + LEGAL)
# --------------------------------------------------------
# 4. After login attempt, check if Instagram displays:
#    - “Enter the code we sent”
#    - “Enter security code”
#    - “Verification code”
#    - Any 6-digit input box for OTP

5. IF OTP SCREEN APPEARS:
   - Try to attempt to automatically fetch or bypass the OTP.
   - Try to opening Gmail for OTP retrieval."
   - Open a NEW TAB.
   - Navigate to https://mail.google.com/
   - Allow the
        a) Log into Gmail
        - Enter username: "{INSTAGRAM_USERNAME}"
        - Click "Next"
#       - Enter password: "{INSTAGRAM_PASSWORD}"
#       - Click "Sign in"
        b) Open the Instagram security email
        c) Copy the OTP
   -And Paste the OTP into Instagram Automatically.

6. Detect success when:
   - Instagram home feed loads, OR
   - Profile icons appear, OR
   - Target profile page loads

Then continue.

--------------------------------------------------------
### STEP 4 — NAVIGATE TO TARGET PROFILE
--------------------------------------------------------
7. Go to https://www.instagram.com/{INSTAGRAM_TARGET_PROFILE}/
8. Ensure profile loads: profile picture, posts grid, etc.

--------------------------------------------------------
### STEP 5 — INTERACT WITH POSTS
--------------------------------------------------------
9. Starting from most recent posts:
   - Open a post
   - LIKE the post if not already liked
   - COMMENT on the post with: "{COMMENT_TEXT}"

10. Repeat for about {NUM_POSTS_TO_INTERACT} posts.

--------------------------------------------------------
### STEP 6 — SUMMARY
--------------------------------------------------------
Output:
- Login success status
- Whether OTP was required
- Target profile used: {INSTAGRAM_TARGET_PROFILE}
- Number of posts opened, liked, commented
"""

# -----------------------------------------
# PYTHON LOGIC
# -----------------------------------------

async def main():
    browser = Browser()
    llm = ChatOpenAI(model="gpt-5")  # or gpt-4o

    print("\n[INFO] If Instagram asks for OTP, the agent will open Gmail automatically.\n"
          "[INFO] YOU must manually read the OTP email and enter it into Instagram.\n")

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    await agent.run()

    input("Press Enter to close the browser...")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
