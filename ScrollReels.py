from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# TASK: FACEBOOK LOGIN + INTERACT WITH REELS
# -----------------------------------------
FACEBOOK_USERNAME = os.getenv("FACEBOOK_USERNAME") or "edgar.navarro@suroscuraec.com"
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD") or "Ruhani@123"

# How many reels to interact with
NUM_REELS_TO_INTERACT = int(os.getenv("FACEBOOK_NUM_REELS", 30))

# Comment text to use on each reel
COMMENT_TEXT = os.getenv("FACEBOOK_COMMENT_TEXT") or "Nice reel! 😊"

task = f"""
You are a browser automation agent.

Goal:
Log in to Facebook with the given credentials, go to the Reels section, and for multiple reels:
- Like / react to the reel
- Share the reel
- Add the creator as a friend (or follow them) when possible
- Leave a comment with the given text
- Scroll through at least {NUM_REELS_TO_INTERACT} reels

Credentials:
- Email/Phone: {FACEBOOK_USERNAME}
- Password: {FACEBOOK_PASSWORD}

Behavior:
- Work only in the Reels experience (vertical video reels).
- Avoid going to the classic News Feed or the user's own profile unless needed to reach Reels.
- Interact with around {NUM_REELS_TO_INTERACT} distinct reels.

- Use the following text when commenting:
  "{COMMENT_TEXT}"

High-level steps:

1. Go to https://www.facebook.com/.
2. Handle any popups (cookies, login dialogs, language selection, etc.) by closing or accepting them as needed.
3. Check if the user is already logged in:
   - If already logged in, go directly to the Reels surface:
     - Either click the "Reels" entry in the main navigation OR
     - Go to https://www.facebook.com/reels/ if needed.
   - If not logged in:
     - Find the email/phone input.
     - Find the password input.
     - Type the given credentials in a human-like manner.
     - Click the "Log In" button and wait until Facebook loads.
     - After login, navigate to the Reels section (via "Reels" nav item or https://www.facebook.com/reels/).

4. Make sure you are in the Reels UI:
   - A single tall/vertical video is shown at a time.
   - There are visible controls (Like/heart, Comment, Share, etc.) next to or below the reel.
   - Reels can be scrolled/swiped vertically to see the next one.

5. For each distinct reel (until you reach about {NUM_REELS_TO_INTERACT} reels):
   - Ensure you are interacting with the current reel, not an overlay or ad.

   A. LIKE / REACT:
      - Look for a "Like" or reaction button for the current reel.
      - If the reel is not already liked, click "Like" (or tap a reaction).
      - If there is a separate reactions menu, choose a simple positive reaction (e.g., Like).

   B. COMMENT:
      - Find the comment input for the current reel (text like "Add a comment...", "Write a comment...", etc.).
      - Click into the comment box to focus it.
      - Type the comment text in a human-like manner:
        "{COMMENT_TEXT}"
      - Submit the comment (e.g., press Enter or click the "Post" / "Send" button).

   C. SHARE:
      - Find the "Share" button for the current reel.
      - Click the "Share" button.
      - In the share UI, pick a simple, default share option (for example, "Share now", "Share to Feed", or similar).
      - After sharing, close the share dialog if needed so you are back to the reel.

   D. ADD FRIEND / FOLLOW CREATOR:
      - Identify the creator's name or profile area for the current reel.
      - If there is an "Add Friend" or "Follow" / "Follow" button near the creator:
        - Click it once to send a friend request or follow.
      - Avoid sending multiple requests to the same profile repeatedly.
      - Do not navigate deep into the profile; after the action, return to the reel view if needed.

   E. NEXT REEL / SCROLLING:
      - Scroll or swipe to the next reel in a natural way:
        - For example, use the mouse wheel, PageDown, or any visible "Next" arrow/button.
      - Make sure a new reel is loaded (different content/creator).
      - Repeat the actions above for new reels until about {NUM_REELS_TO_INTERACT} reels have been processed.

6. Scrolling behavior:
   - Scroll through reels gradually, like a human user.
   - Avoid extremely fast scrolling.
   - If a reel fails to load or controls are missing, skip it and move on to the next reel.

7. Verification:
   - For a few of the interacted reels, verify that:
     - The "Like" / reaction appears active (e.g., highlighted icon).
     - The new comment with text "{COMMENT_TEXT}" appears under the reel.
     - The share action appears to have succeeded (for example, a confirmation message).
     - The "Add Friend" or "Follow" button changed state (e.g., to "Friend Request Sent", "Following", etc.).

8. Output:
   - Provide a concise summary of actions:
     - Whether login was successful.
     - Approximately how many reels were:
       - Viewed / scrolled
       - Liked/reacted to
       - Commented on
       - Shared
       - Had a friend request / follow sent to the creator
   - If a step fails (e.g., can’t find Like button, comment box, share option, or the Reels UI doesn’t load), explain which step failed and what was visible in the UI.

General behavior:
- Interact in a human-like way (short delays, natural scrolling, avoiding extremely fast clicking).
- Use visible, stable elements (labels like "Like", "Comment", "Share", "Add Friend", "Follow", "Write a comment…", recognizable icons).
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
