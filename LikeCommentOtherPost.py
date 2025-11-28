from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# TASK: FACEBOOK LOGIN + LIKE & COMMENT ON FEED POSTS
# -----------------------------------------
FACEBOOK_USERNAME = os.getenv("FACEBOOK_USERNAME") or "edgar.navarro@suroscuraec.com"
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD") or "Ruhani@123"

# How many posts to interact with in the feed
NUM_POSTS_TO_INTERACT = int(os.getenv("FACEBOOK_NUM_POSTS", 5))

# Comment text to use on each post
COMMENT_TEXT = os.getenv("FACEBOOK_COMMENT_TEXT") or "Nice post! 😊"

task = f"""
You are a browser automation agent.

Goal:
Log in to Facebook with the given credentials, scroll the home feed, and for several posts:
- Like the post
- Leave a comment with the given text

Credentials:
- Email/Phone: {FACEBOOK_USERNAME}
- Password: {FACEBOOK_PASSWORD}

Behavior:
- Do NOT go to the user's own profile.
- Work only from the home feed (news feed).
- Interact with around {NUM_POSTS_TO_INTERACT} distinct posts.
- Use the following text when commenting:
  "{COMMENT_TEXT}"

High-level steps:

1. Go to https://www.facebook.com/.
2. Handle any popups (cookies, login dialogs, language selection, etc.) by closing or accepting them as needed.
3. Check if the user is already logged in:
   - If already logged in, go directly to the home feed (News Feed).
   - If not logged in:
     - Find the email/phone input.
     - Find the password input.
     - Type the given credentials in a human-like manner.
     - Click the "Log In" button and wait until the home feed UI is loaded.

4. Make sure you are on the main home feed, not the profile page:
   - Home feed usually shows multiple posts from friends/pages in a vertical scroll.
   - Avoid clicking on the profile/avatar area or "See your profile".

5. Interact with posts in the feed:
   - Scroll slowly through the feed.
   - For each distinct post:
     - Make sure it’s a normal post with a visible reactions bar (Like, Comment, Share).
     - First, LIKE the post:
       - Find the "Like" button for that specific post (not a random one).
       - If the post is not already liked, click "Like".
     - Then, COMMENT on the post:
       - Find the comment input for that same post (usually "Write a comment..." or similar).
       - Click into the comment box to focus it.
       - Type the comment text: "{COMMENT_TEXT}" in a human-like manner.
       - Submit the comment (e.g., press Enter or click the "Post" button).
   - Do this for approximately {NUM_POSTS_TO_INTERACT} posts.
   - Avoid interacting with the same post more than once.

6. Scrolling behavior:
   - Scroll the page gradually, like a human user.
   - After finishing with one post, scroll down to reveal new posts.
   - If you reach the end of currently loaded posts, you can scroll further to load more.

7. Verification:
   - For a few of the interacted posts, verify that:
     - The "Like" state appears active (e.g., filled icon or "Liked").
     - The new comment with text "{COMMENT_TEXT}" appears under the post.
   - It is okay if Facebook slightly changes the wording/icon, as long as the intent is clear.

8. Output:
   - Provide a concise summary of actions:
     - Whether login was successful.
     - Approximately how many posts were liked.
     - Approximately how many posts were commented on.
   - If a step fails (e.g., can’t find Like button, comment box, or feed doesn’t load), explain which step failed and what was visible in the UI.

General behavior:
- Interact in a human-like way (short delays, natural scrolling, avoiding extremely fast clicking).
- Use visible, stable elements (labels like "Like", "Comment", "Write a comment…", recognizable icons).
- Be resilient to small UI or text changes.
"""

async def main():
    # Initialize browser + LLM
    browser = Browser()
    llm = ChatOpenAI(model="gpt-5")  # or "gpt-4o", etc.

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
