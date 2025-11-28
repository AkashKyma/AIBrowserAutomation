from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os

# -----------------------------------------
# TASK: FACEBOOK LOGIN + PROFILE IMAGE UPLOAD
# -----------------------------------------
FACEBOOK_USERNAME = os.getenv("FACEBOOK_USERNAME") or "<edgar.navarro@suroscuraec.com>"
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD") or "<Ruhani@123>"
PROFILE_IMAGE_URL = os.getenv("FACEBOOK_PROFILE_IMAGE_URL") or "<https://img.freepik.com/free-photo/lifestyle-people-emotions-casual-concept-confident-nice-smiling-asian-woman-cross-arms-chest-confident-ready-help-listening-coworkers-taking-part-conversation_1258-59335.jpg>"

task = f"""
You are a browser automation agent.

Goal:
Log in to Facebook and update the profile picture for the given account.

Credentials:
- Email/Phone: {FACEBOOK_USERNAME}
- Password: {FACEBOOK_PASSWORD}

Profile image to use:
- Image URL or path: {PROFILE_IMAGE_URL}

High-level steps:

1. Go to https://www.facebook.com/.
2. If any popups appear (cookies, login dialogs, language selection, etc.), close or skip them.
3. Check if the user is already logged in:
   - If already logged in, continue to the profile page.
   - If not logged in:
     - Find the email/phone input.
     - Find the password input.
     - Type the given credentials in a human-like manner.
     - Click the Login button and wait for the home feed/profile UI to load.

4. Navigate to the user's profile page:
   - Use the profile/avatar button, or
   - Use the menu that usually leads to "See your profile" or similar.

5. Start the profile photo change flow:
   - Locate the current profile picture area.
   - Look for a button or link like:
     - "Update profile picture"
     - "Edit picture"
     - A camera icon on the profile photo
   - Click it to open the upload/change dialog.

6. Upload the new profile picture:
   - If there is an option to paste or enter a URL, use the provided image URL: {PROFILE_IMAGE_URL}.
   - If a file upload dialog is available and the environment supports local file upload, select or upload the file that corresponds to this path or URL.
   - Wait for the upload and preview step to complete.

7. Confirm and save:
   - If there are options to crop, zoom, or reposition, apply reasonable defaults.
   - Click the button to save/apply the new profile picture (e.g., "Save", "Apply", "Done").

8. Verification:
   - After saving, ensure that the new profile photo is visible on the profile page.
   - Optionally refresh the page once and verify that the new image persists.

9. Output:
   - Provide a short summary of what you did:
     - Whether login succeeded
     - Whether the profile picture upload flow was reached
     - Whether the new picture appears to be set
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
