from dotenv import load_dotenv
from browser_use import Browser
import asyncio
import os
import logging
import requests
from typing import Optional
import urllib.parse
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

    This handles both:
    - Simple checkbox clicks
    - Image challenge solving

    CapSolver returns a token that can be used to bypass the entire process.
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
# Optimized CAPTCHA solving flow
# --------------------------------------------------------------
async def solve_captcha_flow_optimized(browser: Browser):
    """
    Optimized flow that properly handles reCAPTCHA v2:

    1. Navigate to page
    2. Extract sitekey from DOM
    3. Solve with CapSolver (handles checkbox + image challenges)
    4. Inject token and trigger callbacks
    5. Submit form directly
    6. Verify success
    """
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Starting OPTIMIZED CAPTCHA bypass automation")
    logger.info("=" * 60 + "\n")

    page_url = "https://www.google.com/recaptcha/api2/demo"

    # Step 1: Start the browser
    logger.info("🔍 Step 1: Starting browser session...")
    await browser.start()

    # Step 2: Navigate to the page
    logger.info("🔍 Step 2: Navigating to CAPTCHA page...")
    page = await browser.new_page(page_url)
    await asyncio.sleep(3)  # Wait for page load

    # Step 3: Extract sitekey from the page
    logger.info("🔍 Step 3: Extracting sitekey from page DOM...")

    iframe_info_raw = await page.evaluate("""
        () => {
            // Look for the reCAPTCHA iframe
            const iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
            if (iframes.length > 0) {
                return {
                    found: true,
                    src: iframes[0].src,
                    title: iframes[0].title
                };
            }

            // Also check for data-sitekey attribute
            const recaptchaDiv = document.querySelector('.g-recaptcha');
            if (recaptchaDiv) {
                return {
                    found: true,
                    sitekey: recaptchaDiv.getAttribute('data-sitekey'),
                    callback: recaptchaDiv.getAttribute('data-callback')
                };
            }

            return {found: false};
        }
    """)

    # Parse result
    if isinstance(iframe_info_raw, str):
        iframe_info = json.loads(iframe_info_raw)
    else:
        iframe_info = iframe_info_raw

    if not iframe_info.get('found'):
        logger.error("❌ Could not find reCAPTCHA on the page")
        return False

    # Extract sitekey
    sitekey = iframe_info.get('sitekey')
    if not sitekey and iframe_info.get('src'):
        sitekey = extract_sitekey_from_url(iframe_info['src'])

    if not sitekey:
        logger.error("❌ Could not extract sitekey")
        return False

    logger.info(f"✅ Extracted sitekey: {sitekey}")
    callback_name = iframe_info.get('callback', 'onSuccess')
    logger.info(f"✅ Found callback function: {callback_name}")

    # Step 4: Solve CAPTCHA with CapSolver
    logger.info("\n🔧 Step 4: Solving CAPTCHA with CapSolver...")
    logger.info("   CapSolver will handle:")
    logger.info("   - Checkbox clicking")
    logger.info("   - Image challenge solving (if shown)")
    logger.info("   - Token generation")

    token = await solve_recaptcha_with_capsolver(sitekey, page_url)

    if not token:
        logger.error("❌ Failed to get solution from CapSolver")
        return False

    # Step 5: Inject token and trigger callbacks
    logger.info("\n💉 Step 5: Injecting token and triggering reCAPTCHA callbacks...")

    injection_result_raw = await page.evaluate(f"""
        () => {{
            // 1. Inject token into the hidden textarea
            const textarea = document.querySelector('#g-recaptcha-response');
            if (textarea) {{
                textarea.innerHTML = '{token}';
                textarea.value = '{token}';
                textarea.style.display = 'block'; // Make visible for debugging
                console.log('✅ Token injected into textarea');
            }} else {{
                console.error('❌ g-recaptcha-response textarea not found');
                return {{success: false, error: 'textarea not found'}};
            }}

            // 2. Remove error messages
            const errorDivs = document.getElementsByClassName("recaptcha-error");
            if (errorDivs.length) {{
                errorDivs[0].className = "";
            }}
            const errorMsgs = document.getElementsByClassName("recaptcha-error-message");
            if (errorMsgs.length) {{
                errorMsgs[0].style.display = 'none';
            }}

            // 3. Try to trigger the callback function
            let callbackExecuted = false;
            try {{
                if (typeof window['{callback_name}'] === 'function') {{
                    window['{callback_name}']('{token}');
                    callbackExecuted = true;
                    console.log('✅ Callback {callback_name} executed');
                }} else {{
                    console.warn('⚠️  Callback {callback_name} not found');
                }}
            }} catch (e) {{
                console.error('❌ Error executing callback:', e);
            }}

            // 4. Trigger change events
            if (textarea) {{
                textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}

            // 5. Check if form submit button is enabled
            const submitBtn = document.querySelector('#recaptcha-demo-submit');
            const submitEnabled = submitBtn ? !submitBtn.disabled : false;

            return {{
                success: true,
                textareaFound: !!textarea,
                textareaVisible: textarea ? textarea.style.display !== 'none' : false,
                callbackExecuted: callbackExecuted,
                submitEnabled: submitEnabled,
                tokenLength: '{token}'.length
            }};
        }}
    """)

    # Parse result
    if isinstance(injection_result_raw, str):
        injection_result = json.loads(injection_result_raw)
    else:
        injection_result = injection_result_raw

    logger.info(f"✅ Token injection result:")
    logger.info(f"   - Textarea found: {injection_result.get('textareaFound')}")
    logger.info(f"   - Callback executed: {injection_result.get('callbackExecuted')}")
    logger.info(f"   - Submit button enabled: {injection_result.get('submitEnabled')}")

    # Step 6: Submit the form directly using JavaScript
    logger.info("\n📝 Step 6: Submitting the form...")

    submit_result_raw = await page.evaluate("""
        () => {
            const submitBtn = document.querySelector('#recaptcha-demo-submit');
            if (submitBtn) {
                submitBtn.click();
                console.log('✅ Submit button clicked');
                return {success: true, method: 'button_click'};
            }

            // Fallback: submit form directly
            const form = document.querySelector('#recaptcha-demo-form');
            if (form) {
                form.submit();
                console.log('✅ Form submitted directly');
                return {success: true, method: 'form_submit'};
            }

            return {success: false, error: 'No submit method found'};
        }
    """)

    if isinstance(submit_result_raw, str):
        submit_result = json.loads(submit_result_raw)
    else:
        submit_result = submit_result_raw

    if not submit_result.get('success'):
        logger.error("❌ Failed to submit form")
        return False

    logger.info(f"✅ Form submitted using: {submit_result.get('method')}")

    # Step 7: Wait and verify success
    logger.info("\n⏳ Step 7: Waiting for response...")
    await asyncio.sleep(5)

    # Check if we got a success response
    verification_raw = await page.evaluate("""
        () => {
            const url = window.location.href;
            const html = document.body.innerHTML;

            // Look for success indicators
            const hasSuccessInUrl = url.includes('success') || url.includes('passed');
            const hasSuccessInHtml = html.toLowerCase().includes('success') ||
                                     html.toLowerCase().includes('verification') ||
                                     html.toLowerCase().includes('passed');

            return {
                url: url,
                hasSuccessInUrl: hasSuccessInUrl,
                hasSuccessInHtml: hasSuccessInHtml,
                bodyText: document.body.innerText.substring(0, 500)
            };
        }
    """)

    if isinstance(verification_raw, str):
        verification = json.loads(verification_raw)
    else:
        verification = verification_raw

    logger.info("\n" + "=" * 60)
    logger.info("📊 Verification Results:")
    logger.info(f"   URL: {verification.get('url')}")
    logger.info(f"   Success in URL: {verification.get('hasSuccessInUrl')}")
    logger.info(f"   Success in HTML: {verification.get('hasSuccessInHtml')}")
    logger.info(f"   Page text preview: {verification.get('bodyText', '')[:100]}...")
    logger.info("=" * 60)

    success = verification.get('hasSuccessInUrl') or verification.get('hasSuccessInHtml')

    if success:
        logger.info("🎉 CAPTCHA SUCCESSFULLY BYPASSED!")
    else:
        logger.warning("⚠️  Form submitted but success verification unclear")
        logger.info("💡 The page may have redirected or the CAPTCHA may need manual verification")

    # Keep browser open for inspection
    logger.info("\n🔍 Keeping browser open for 30 seconds for inspection...")
    await asyncio.sleep(30)

    return True


async def main():
    browser = Browser(headless=False)  # Set to False to see what's happening

    try:
        success = await solve_captcha_flow_optimized(browser)

        if success:
            logger.info("🎉 All done! CAPTCHA bypass completed.")
        else:
            logger.error("❌ CAPTCHA bypass failed. Check the logs above for details.")

    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
    finally:
        logger.info("🔒 Closing browser...")
        try:
            await browser.kill()
        except Exception as e:
            logger.warning(f"⚠️  Error closing browser: {e}")


if __name__ == '__main__':
    asyncio.run(main())
