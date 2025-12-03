from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os
import logging
import requests
from typing import Optional, Dict
import urllib.parse
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

# --------------------------------------------------------------
# CapSolver API Integration
# --------------------------------------------------------------
def get_capsolver_key() -> Optional[str]:
    """Get CapSolver API key from environment variables."""
    candidates = ['CAPSOLVER_API_KEY', 'CAPSOLVER', 'CAPSOLVER_KEY']

    for name in candidates:
        val = os.getenv(name)
        if val:
            cleaned = val.strip().strip('"').strip("'").strip(';')
            logger.info(f"✅ Found CapSolver API key in environment variable: {name}")
            return cleaned

    logger.error("❌ CapSolver API key not found in environment variables")
    logger.error("   Please set CAPSOLVER_API_KEY in your .env file")
    return None


async def solve_recaptcha_with_capsolver(sitekey: str, page_url: str) -> Optional[str]:
    """
    Solve reCAPTCHA using CapSolver API.

    Args:
        sitekey: The reCAPTCHA site key
        page_url: The URL of the page with CAPTCHA

    Returns:
        The solved CAPTCHA token or None if failed
    """
    api_key = get_capsolver_key()
    if not api_key:
        return None

    logger.info("=" * 60)
    logger.info("🔧 Starting CapSolver CAPTCHA solving process")
    logger.info(f"   Site Key: {sitekey}")
    logger.info(f"   Page URL: {page_url}")
    logger.info("=" * 60)

    # Create task
    create_payload = {
        'clientKey': api_key,
        'task': {
            'type': 'ReCaptchaV2TaskProxyless',
            'websiteURL': page_url,
            'websiteKey': sitekey,
        }
    }

    logger.info("📤 Sending createTask request to CapSolver...")

    try:
        resp = await asyncio.to_thread(
            lambda: requests.post(
                'https://api.capsolver.com/createTask',
                json=create_payload,
                timeout=30
            )
        )
        data = resp.json()

        logger.info(f"📥 CreateTask response: {data}")

        if data.get('errorId', 1) != 0:
            logger.error(f"❌ CapSolver createTask error: {data.get('errorDescription', 'Unknown error')}")
            logger.error(f"   Error code: {data.get('errorCode', 'N/A')}")
            return None

        task_id = data.get('taskId')
        if not task_id:
            logger.error("❌ CapSolver returned no taskId")
            return None

        logger.info(f"✅ Task created successfully. Task ID: {task_id}")
        logger.info("⏳ Waiting for CapSolver to solve the CAPTCHA (this may take 10-30 seconds)...")

    except Exception as e:
        logger.exception(f"❌ Error creating CapSolver task: {e}")
        return None

    # Poll for result
    check_payload = {'clientKey': api_key, 'taskId': task_id}
    max_attempts = 60

    for attempt in range(1, max_attempts + 1):
        try:
            await asyncio.sleep(2)

            check_resp = await asyncio.to_thread(
                lambda: requests.post(
                    'https://api.capsolver.com/getTaskResult',
                    json=check_payload,
                    timeout=30
                )
            )
            check_data = check_resp.json()

            status = check_data.get('status', 'unknown')

            if attempt % 5 == 0:
                logger.info(f"⏳ Attempt {attempt}/{max_attempts} - Status: {status}")

            if status == 'ready':
                solution = check_data.get('solution', {})
                token = solution.get('gRecaptchaResponse') or solution.get('token')

                if token:
                    logger.info("=" * 60)
                    logger.info("🎉 SUCCESS! CapSolver solved the CAPTCHA")
                    logger.info(f"   Token length: {len(token)} characters")
                    logger.info(f"   Token preview: {token[:50]}...")
                    logger.info("=" * 60)
                    return token
                else:
                    logger.error("❌ CapSolver returned 'ready' but no token found")
                    return None

            elif status == 'failed':
                logger.error(f"❌ CapSolver task failed: {check_data.get('errorDescription', 'Unknown error')}")
                return None

        except Exception as e:
            logger.warning(f"⚠️  Error polling CapSolver (attempt {attempt}): {e}")
            continue

    logger.error(f"❌ CapSolver timeout: No solution after {max_attempts * 2} seconds")
    return None


def extract_sitekey_from_url(iframe_src: str) -> Optional[str]:
    """Extract sitekey from reCAPTCHA iframe src URL."""
    if not iframe_src:
        return None

    try:
        parsed = urllib.parse.urlparse(iframe_src)
        params = urllib.parse.parse_qs(parsed.query)

        if 'k' in params:
            return params['k'][0]
    except Exception as e:
        logger.warning(f"Failed to extract sitekey from URL: {e}")

    return None


# --------------------------------------------------------------
# Main CAPTCHA solving flow
# --------------------------------------------------------------
async def solve_captcha_flow(browser: Browser):
    """
    Complete flow: Navigate → Detect → Solve → Inject → Verify
    """
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Starting CAPTCHA bypass automation")
    logger.info("=" * 60 + "\n")

    # Extract info from page
    page_url = "https://www.google.com/recaptcha/api2/demo"

    # Step 1: Start the browser (REQUIRED before any operations)
    logger.info("🔍 Step 1: Starting browser session...")
    await browser.start()

    # Step 2: Navigate directly using browser and get page
    logger.info("🔍 Step 2: Navigating to CAPTCHA page and getting page handle...")

    # Create a new page and navigate
    page = await browser.new_page(page_url)

    # Wait for page to load
    await asyncio.sleep(5)

    # Step 3: Extract CAPTCHA information directly
    logger.info("🔍 Step 3: Extracting sitekey from page...")

    iframe_info_raw = await page.evaluate("""
        () => {
            const iframes = document.querySelectorAll('iframe');
            for (let iframe of iframes) {
                const src = iframe.src || '';
                if (src.includes('recaptcha')) {
                    return {
                        found: true,
                        src: src,
                        title: iframe.title || 'reCAPTCHA'
                    };
                }
            }
            return {found: false};
        }
    """)

    # Parse the result if it's a string
    if isinstance(iframe_info_raw, str):
        try:
            iframe_info = json.loads(iframe_info_raw)
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to parse iframe_info: {iframe_info_raw}")
            return False
    else:
        iframe_info = iframe_info_raw

    if not iframe_info.get('found'):
        logger.error("❌ Could not find reCAPTCHA iframe on the page")
        return False

    iframe_src = iframe_info.get('src', '')
    logger.info(f"✅ Found reCAPTCHA iframe: {iframe_src[:100]}...")

    sitekey = extract_sitekey_from_url(iframe_src)

    if not sitekey:
        logger.error("❌ Could not extract sitekey from iframe URL")
        logger.error(f"   Iframe src: {iframe_src}")
        return False

    logger.info(f"✅ Extracted sitekey: {sitekey}")

    # Step 4: Solve with CapSolver
    logger.info("\n🔧 Step 4: Solving CAPTCHA with CapSolver API...")
    token = await solve_recaptcha_with_capsolver(sitekey, page_url)

    if not token:
        logger.error("❌ Failed to get solution from CapSolver")
        logger.info("💡 Please check:")
        logger.info("   1. Your CAPSOLVER_API_KEY is set correctly in .env")
        logger.info("   2. You have credits in your CapSolver account")
        logger.info("   3. The sitekey was extracted correctly")
        return False

    # Step 5: Inject token
    logger.info("\n💉 Step 5: Injecting solution token into the page...")

    injection_script = f"""
        () => {{
            // Find the textarea for g-recaptcha-response
            const textarea = document.querySelector('#g-recaptcha-response');
            if (textarea) {{
                textarea.innerHTML = '{token}';
                textarea.value = '{token}';
                console.log('Token injected into textarea');
            }}

            // Also try to set it via callback if available
            if (window.grecaptcha) {{
                console.log('grecaptcha object found');
            }}

            return {{
                success: true,
                textareaFound: !!textarea,
                token: '{token[:50]}...'
            }};
        }}
    """

    try:
        inject_result_raw = await page.evaluate(injection_script)

        # Parse the result if it's a string
        if isinstance(inject_result_raw, str):
            try:
                inject_result = json.loads(inject_result_raw)
            except json.JSONDecodeError:
                logger.warning(f"⚠️  Token injection returned non-JSON: {inject_result_raw}")
                inject_result = {"success": True}  # Assume success if we got a response
        else:
            inject_result = inject_result_raw

        logger.info(f"✅ Token injection result: {inject_result}")
    except Exception as e:
        logger.error(f"❌ Error injecting token: {e}")
        return False

    # Step 6: Submit the form
    logger.info("\n📝 Step 6: Submitting the form...")

    task_submit = f"""
The CAPTCHA has been solved and the token has been injected.

Now:
1. Find the submit button on the page (it should be near the reCAPTCHA)
2. Click the submit button
3. Wait for the response
4. Report if the submission was successful

The g-recaptcha-response textarea should now contain the solution token.
Click the submit button to verify the CAPTCHA was solved correctly.
"""

    agent_submit = Agent(
        task=task_submit,
        llm=ChatOpenAI(model="gpt-4o"),
        browser=browser,
    )

    await agent_submit.run()

    logger.info("\n" + "=" * 60)
    logger.info("✅ CAPTCHA bypass process completed!")
    logger.info("=" * 60 + "\n")

    # Keep browser open for inspection
    logger.info("🔍 Browser will remain open for 30 seconds for inspection...")
    await asyncio.sleep(30)

    return True


async def main():
    browser = Browser()

    try:
        success = await solve_captcha_flow(browser)

        if success:
            logger.info("🎉 All done! CAPTCHA was successfully bypassed.")
        else:
            logger.error("❌ CAPTCHA bypass failed. Check the logs above for details.")

    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
    finally:
        logger.info("🔒 Closing browser...")
        try:
            # Browser is an alias for BrowserSession, so call kill() directly
            await browser.kill()
        except Exception as e:
            logger.warning(f"⚠️  Error closing browser: {e}")


if __name__ == '__main__':
    asyncio.run(main())
