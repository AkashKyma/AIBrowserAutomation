from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# CONFIG: INSTAGRAM LOGIN + LIKE & COMMENT ON PROFILE POSTS
# -----------------------------------------

# Credentials (use env vars in real usage)
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME") or "jose.santana@suroscuraec.com"
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD") or "Ruhani@123"

# Target profile username (without @), e.g. "natgeo"
INSTAGRAM_TARGET_PROFILE = os.getenv("INSTAGRAM_TARGET_PROFILE") or "instagram"

# How many posts to interact with on the profile
NUM_POSTS_TO_INTERACT = int(os.getenv("INSTAGRAM_NUM_POSTS", 5))

# Comment text to use on each post
COMMENT_TEXT = os.getenv("INSTAGRAM_COMMENT_TEXT") or "Nice post! 😊"

task = f"""
You are a browser automation agent.

Goal:
Log in to Instagram with the given credentials, navigate to a specific profile, and for several posts:
- Like the post
- Leave a comment with the given text

Credentials:
- Username: {INSTAGRAM_USERNAME}
- Password: {INSTAGRAM_PASSWORD}

Target:
- Profile username (without @): {INSTAGRAM_TARGET_PROFILE}

Behavior:
- Do NOT change account settings.
- Work only on the target profile's posts.
- Interact with around {NUM_POSTS_TO_INTERACT} distinct posts.
- Use the following text when commenting:
  "{COMMENT_TEXT}"

High-level steps:

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

4. Handling OTP / two-factor authentication:
   - If Instagram shows a screen asking for a security code, verification code, or any form of OTP / two-factor authentication:
     - DO NOT attempt to bypass or circumvent this verification.
     - Stop any further automated actions on that screen.
     - Wait while the HUMAN USER manually enters the OTP in the open browser window and completes the verification flow.
     - Once the OTP is accepted and Instagram loads the main UI (home feed or profile view), resume with the next steps.
   - You can detect successful login by:
     - Presence of the main navigation bar (Home, Search, Reels, Profile icons), or
     - Successful load of the target profile page.

5. Navigate to the target profile:
   - Go to https://www.instagram.com/{INSTAGRAM_TARGET_PROFILE}/
   - Wait for the profile page to load fully.
   - Confirm you are on the profile page:
     - You should see the profile picture, bio, follower/following counts, and a grid of posts (thumbnails).

6. Interact with posts on the profile:
   - Focus on standard feed posts (image/video posts in the grid).
   - Start from the most recent posts at the top of the grid.
   - For each distinct post (open the post one by one in a modal/lightbox):
     - Click on the post thumbnail to open it.
     - Wait for the post modal to appear, showing:
       - The media (image/video)
       - A like button (heart icon)
       - A comment area

     A. LIKE the post:
        - Find the Like (heart) button for this post.
        - If the post is not already liked (heart is not filled), click the Like button.
        - Make sure you are clicking the Like button for this post, not another element.

     B. COMMENT on the post:
        - Locate the comment input field (text like "Add a comment..." or similar).
        - Click into the comment box to focus it.
        - Type the comment text in a human-like manner:
          "{COMMENT_TEXT}"
        - Submit the comment (e.g., press Enter or click the "Post" button).
        - Confirm that the comment appears under the post if possible.

     C. Move to the next post:
        - Close the post modal (e.g., click the close button "X" or click outside the modal),
          OR if there is a next arrow/button, you can use it to go to the next post.
        - Ensure you are interacting with a new post each time.
        - Avoid commenting/liking the same post more than once.

   - Do this process for approximately {NUM_POSTS_TO_INTERACT} posts.
   - If some posts fail to load or if elements cannot be found, skip that post and move on.

7. Scrolling behavior on the profile:
   - If you need more posts, scroll down the profile page to load older posts.
   - Scroll gradually, like a human user.
   - Wait briefly after scrolling so new posts can load.

8. Verification:
   - For a few of the interacted posts, verify that:
     - The Like icon appears in the "liked" state (e.g., filled heart).
     - The new comment with text "{COMMENT_TEXT}" appears in the comments list.
   - It is okay if Instagram slightly changes the wording/icon, as long as the intent is clear.

9. Output:
   - Provide a concise summary of actions:
     - Whether login was successful.
     - The target profile that was used: "{INSTAGRAM_TARGET_PROFILE}"
     - Approximately how many posts were:
       - Opened/viewed
       - Liked
       - Commented on
   - If a step fails (e.g., can’t find Like button, comment box, profile page, or posts don’t load), explain which step failed and what was visible in the UI.

General behavior:
- Interact in a human-like way (short delays, natural scrolling, avoiding extremely fast clicking).
- Use visible, stable elements (labels like "Log in", "Add a comment…", recognizable heart/comment icons).
- Be resilient to small UI or text changes.
"""

async def main():
    # Initialize browser + LLM
    browser = Browser()
    llm = ChatOpenAI(model="gpt-5")  # or "gpt-4o", etc.

    print(
        "\\n[INFO] If Instagram asks for an OTP / verification code during login, "
        "enter it manually in the browser window. The agent will continue once login completes.\\n"
    )

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    # Run the agent
    await agent.run()

    # Pause so you can inspect the browser if it's still open
    input("Press Enter to close the browser...")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
