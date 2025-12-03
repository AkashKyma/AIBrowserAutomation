from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os
import logging
import requests
from typing import Optional

load_dotenv()

# --------------------------------------------------------------
# PLACEHOLDER: Where your CapSolver API logic WOULD go
# --------------------------------------------------------------
async def call_capsolver_placeholder(captcha_info):
    """
    This function represents where you would call the CapSolver API.
    For safety reasons, this is a placeholder and DOES NOT solve CAPTCHA.
    """
    # New: attempt to call CapSolver API using key from .env
    key = _get_capsolver_key()
    if not key:
        logging.error("CapSolver API key not found in environment (.env). Falling back to manual flow.")
        return None

    # captcha_info is expected to be a dict containing at least a page URL and/or sitekey
    sitekey = None
    page_url = None
    if isinstance(captcha_info, dict):
        sitekey = captcha_info.get('sitekey') or captcha_info.get('site_key') or captcha_info.get('websiteKey')
        page_url = captcha_info.get('pageurl') or captcha_info.get('page_url') or captcha_info.get('websiteURL')

    # If we only have an iframe src, try to extract sitekey from it
    if not sitekey and isinstance(captcha_info, dict):
        iframe_src = captcha_info.get('iframe_src') or captcha_info.get('src')
        if iframe_src and 'k=' in iframe_src:
            # common pattern in some recaptcha iframe URLs: k=<sitekey>
            import urllib.parse
            qs = urllib.parse.parse_qs(urllib.parse.urlsplit(iframe_src).query)
            if 'k' in qs:
                sitekey = qs['k'][0]

    if not sitekey or not page_url:
        logging.warning('Incomplete captcha_info (need sitekey and page_url). Attempting with what we have.')

    # Build CapSolver createTask payload (NoCaptchaTaskProxyless for reCAPTCHA v2/v3)
    task_type = 'NoCaptchaTaskProxyless'
    task_payload = {
        'type': task_type,
    }
    if page_url:
        task_payload['websiteURL'] = page_url
    if sitekey:
        task_payload['websiteKey'] = sitekey

    create_payload = {
        'clientKey': key,
        'task': task_payload
    }

    try:
        # Use asyncio.to_thread to avoid blocking event loop with requests
        resp = await asyncio.to_thread(lambda: requests.post('https://api.capsolver.com/createTask', json=create_payload, timeout=30))
        data = resp.json()
    except Exception as e:
        logging.exception('Error creating CapSolver task: %s', e)
        return None

    if data.get('errorId', 1) != 0:
        logging.error('CapSolver createTask error: %s', data.get('errorDescription'))
        return None

    task_id = data.get('taskId')
    if not task_id:
        logging.error('CapSolver returned no taskId')
        return None

    # Poll for result
    check_payload = {'clientKey': key, 'taskId': task_id}
    for _ in range(60):
        try:
            await asyncio.sleep(1)
            check_resp = await asyncio.to_thread(lambda: requests.post('https://api.capsolver.com/getTaskResult', json=check_payload, timeout=30))
            check_data = check_resp.json()
        except Exception as e:
            logging.exception('Error polling CapSolver task result: %s', e)
            continue

        if check_data.get('status') == 'ready':
            solution = check_data.get('solution', {})
            # Many CapSolver tasks put the token in gRecaptchaResponse or token
            token = solution.get('gRecaptchaResponse') or solution.get('token') or solution.get('response')
            return token

    logging.error('CapSolver: timed out waiting for solution')
    return None


# --------------------------------------------------------------
# CALLBACK: Triggered when CAPTCHA is detected
# --------------------------------------------------------------
async def on_captcha_detected(captcha_info=None):
    print("\n⚠ CAPTCHA detected!")
    
    # 1. Call placeholder CapSolver API (SAFE)
    response = await call_capsolver_placeholder(captcha_info)

    if response:
        print(f"🔍 CapSolver returned token: {response}\n")
        print("👉 You can now inject the token into the page or let the agent use it to verify the CAPTCHA.")
        # Keep manual confirmation so user can continue if injection isn't automated
        input("Press ENTER after verifying the CAPTCHA was accepted (or to continue)...\n")
    else:
        print("⚠ CapSolver did not return a solution. Please solve the CAPTCHA manually in the browser.")
        input("👉 Solve the CAPTCHA manually, then press ENTER here to continue...\n")
        print("✔ CAPTCHA solved manually. Continuing automation...\n")


def _get_capsolver_key() -> Optional[str]:
    """Try common env variable names for the CapSolver API key."""
    candidates = [
        'CAPSOLVER_API_KEY',
        'CAPSOLVER',
        'capsolver',
        'CAPSOLVER_KEY'
    ]
    for name in candidates:
        val = os.getenv(name)
        if val:
            # strip common noise like surrounding quotes or semicolons
            return val.strip().strip('"').strip("'").strip(';')
    # If not found, attempt to read .env directly as a last resort
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip().lower().startswith('capsolver'):
                            return v.strip().strip('"').strip("'" ).strip(';')
    except Exception:
        pass
    return None


# --------------------------------------------------------------
# TASK to detect CAPTCHA & pass info to callback
# --------------------------------------------------------------
task = """
Visit: https://www.google.com/recaptcha/api2/demo
Detect the CAPTCHA iframe:
- reCAPTCHA: iframe containing 'recaptcha'
If detected:
- Extract basic data such as iframe src or sitekey
- Call Python callback: on_captcha_detected(captcha_info)
- DO IT AUTOMATICALLY WITHOUT STOPPING THE AGENT.
- If you cannot solve automatically,call the callback to call_capsolver_placeholder placeholder or skip and try to solve another one
- Resume execution after callback completes.
- Do not Stop try to solve that CAPTCHA solving is required automatically.
"""

browser = Browser()
llm = ChatOpenAI(model="gpt-5")

# Agent with callback
agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
    callbacks={
        "captcha_detected": on_captcha_detected
    }
)

async def main():
    await agent.run()

if __name__ == '__main__':
    asyncio.run(main())
