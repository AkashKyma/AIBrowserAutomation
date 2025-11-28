from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# TASK: FACEBOOK LOGIN + LIKE & COMMENT ON POST
# -----------------------------------------
FACEBOOK_USERNAME = os.getenv("FACEBOOK_USERNAME") or "edgar.navarro@suroscuraec.com"
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD") or "Ruhani@123"

# URL of the specific Facebook post you want to interact with
FACEBOOK_POST_URL = os.getenv("FACEBOOK_POST_URL") or "https://www.facebook.com/your-post-url-here"

# Comment text you want to leave
COMMENT_TEXT = os.getenv("FACEBOOK_COMMENT_TEXT") or "Nice post! 👌"

task = f"""
You are a browser automation agent.

Goal:
Log in to Facebook with the given credentials, navigate to a specific post, like it, and add a comment.

Credentials:
- Email/Phone: {FACEBOOK_USERNAME}
- Password: {FACEBOOK_PASSWORD}

Target post:
- Post URL: {FACEBOOK_POST_URL}

Comment to post:
- Comment text: {COMMENT_TEXT}

High-level steps:

1. Go to https://www.facebook.com/.
2. If any popups appear (cookies, login dialogs, language selection, etc.), close or skip them.
3. Check if the user is already logged in:
   - If already logged in, continue to the target post URL.
   - If not logged in:
     - Find the email/phone input.
     - Find the password input.
     - Type the given credentials in a human-like manner.
     - Click the Login button and wait for the home feed/profile UI to load.

4. Navigate directly to the target post:
   - Open the URL: {FACEBOOK_POST_URL}
   - Wait for the post content to fully load (text, reactions bar, comment box).

5. Like the post:
   - Locate the main "Like" button for the post (usually a button near the reactions bar).
   - If the post is not already liked:
     - Click the "Like" button.
   - If it is already liked, leave it as is.

6. Add a comment:
   - Find the comment input box for the post (e.g., "Write a comment..." field).
   - Click into the comment box to focus it.
   - Type the comment text in a human-like manner:
     - {COMMENT_TEXT}
   - Submit the comment (press Enter or click the appropriate "Post" button).

7. Verification:
   - Confirm that the "Like" state for the post appears active (filled icon, "Liked" label, or similar).
   - Confirm that the new comment appears under the post with the expected text.
   - Optionally refresh the page once and verify that:
     - The like is still active.
     - The comment is still present.

8. Output:
   - Provide a short summary of what you did:
     - Whether login succeeded
     - Whether the target post loaded
     - Whether the post was liked (or already liked)
     - Whether the comment was successfully posted
   - If any step fails, explain which step failed and why (as far as visible in the UI).

Behavior:
- Interact in a human-like way (small delays, natural scrolling).
- Prefer stable, visible elements; avoid brittle selectors.
- Be resilient to minor layout or text changes.
"""

async def main():
    # Initialize browser + LLM
    browser = Browser()
    llm = ChatOpenAI(model="gpt-5")  # adjust model if needed, e.g. "gpt-4.1" / "gpt-4o"

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
