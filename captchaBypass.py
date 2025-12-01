from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.llm.openai.chat import ChatOpenAI
import asyncio
import os


load_dotenv()

task = f"""
### CAPTCHA Detection & Solve the Task

**Goal:**  
Go to a CAPTCHA-heavy website and detect the CAPTCHA.  
Do Not Stop and Try To Solve that CAPTCHA solving is required automatically.

### Steps:

1. Navigate to a website that always shows CAPTCHA, for example:
   # - https://www.indianrail.gov.in/enquiry/PNR/PnrEnquiry.jsp?locale=en
   - https://www.google.com/recaptcha/api2/demo
   - https://accounts.hcaptcha.com/demo

2. Wait for the CAPTCHA iframe to load.
   - reCAPTCHA iframe: "//iframe[contains(@src, 'recaptcha')]"
   - hCaptcha iframe:  "//iframe[contains(@src, 'hcaptcha')]"

3. If a CAPTCHA is detected:
   # - Go on Indian Railways PNR Enquiry page.
   # - And enter Random ten digit number in PNR field.
   # - After do Arithmatic calculation for CAPTCHA solving.
   # - And then:Submit the form.
   
   - Attempt to bypass or solve.
   - Click on I Am Not A Robot checkbox (reCAPTCHA) or interact with hCaptcha.
   - If There Is Image-Based CAPTCHA:Tick the checkbox and wait for the image challenges to appear,Tick the required images which is written on and carefully tick the image automatically,And try to solve it automatically And Verify.
   - If There Is Audio-Based CAPTCHA:Switch to audio challenge,Play the audio file,and verify the audio by converting speech to text and recognizing the words and according to word tick the image automatically.
   - Or Click on Verify button (hCaptcha) and wait for the challenges to appear.
   - If There Is Number Automatic Solve Possible:Extract the numbers and fill them automatically.
   
   - Clearly notify but try to solve by your Self And solve it automatically."
   - Resume the  execution press ENTER to continue.

4. After the solves CAPTCHA automatically:
   - Continue to the next steps.
   - Confirm that the CAPTCHA is marked as solved by checking:
     - Checkbox ticked (reCAPTCHA)
     - Success message present (hCaptcha)

5. Output a final message:
   - "CAPTCHA solved automatically, continuing automation is now possible."
"""

browser = Browser()

llm = ChatOpenAI(model="gpt-5")

agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
)

async def main():
    await agent.run()
    input("\n✔ CAPTCHA detected — solve it in the browser and press ENTER here to continue...")
    print("✔ CAPTCHA marked as solved. Automation can continue from this point.")
    # Add additional automation steps here if needed.

if __name__ == '__main__':
    asyncio.run(main())
