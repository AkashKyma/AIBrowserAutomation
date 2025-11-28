# #!/usr/bin/env python3
# """
# 📘 FACEBOOK LOGIN WITH PROFILE IMAGE UPLOAD
# ============================================
# Selenium script for automatic Facebook login and profile image upload.

# Features:
# - Automatic login to facebook.com
# - Navigate to profile page
# - Upload profile picture from local file or S3 URL
# - Human-like behavior simulation
# - Screenshot documentation
# - Error handling and retry logic
# """

import os
import sys
import time
import traceback
import re
from typing import Optional, Dict, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import shared modules
try:
    from ..core_interactions.shared.utilities import ScreenshotManager, ElementFinder, PageDetector
    from ..core_interactions.shared.human import HumanBehavior
    from ..core_interactions.shared.multilogin import MultiloginManager
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_interactions', 'shared'))
    from utilities import ScreenshotManager, ElementFinder, PageDetector
    from human import HumanBehavior
    try:
        from multilogin import MultiloginManager
    except ImportError:
        MultiloginManager = None


class FacebookLoginWithImage:
    """
    Facebook Login and Profile Image Upload Manager.
    
    Handles:
    - Automatic Facebook login
    - Profile navigation
    - Profile image upload
    - Human-like interactions
    """
    
    def __init__(self,
                 driver: webdriver.Remote,
                 facebook_username: Optional[str] = None,
                 facebook_password: Optional[str] = None,
                 profile_image_path: Optional[str] = None,
                 screenshots_dir: Optional[str] = None,
                 multilogin_manager: Optional[Any] = None):
        """
        Initialize Facebook Login with Image Upload Manager.
        
        Args:
            driver: Selenium WebDriver instance (standard Chrome WebDriver or MultiLogin)
            facebook_username: Facebook email/phone
            facebook_password: Facebook password
            profile_image_path: Path to profile image file (local or S3 URL)
            screenshots_dir: Directory for screenshot storage (defaults to screenshots/{username})
            multilogin_manager: Optional MultiloginManager instance for cleanup
        """
        self.driver = driver
        self.facebook_username = facebook_username or os.getenv("FACEBOOK_USERNAME")
        self.facebook_password = facebook_password or os.getenv("FACEBOOK_PASSWORD")
        self.profile_image_path = profile_image_path
        self.multilogin_manager = multilogin_manager
        
        # Set screenshots directory based on username (ID) if not provided
        if screenshots_dir is None:
            # Use username as ID, sanitize for filesystem
            username_id = self.facebook_username or "unknown"
            # Remove or replace characters that might cause issues in file paths
            username_id = re.sub(r'[<>:"/\\|?*]', '_', username_id)
            screenshots_dir = f"screenshots/{username_id}"
        
        # Initialize shared services
        self.screenshot_manager = ScreenshotManager(screenshots_dir)
        self.element_finder = ElementFinder(driver)
        self.page_detector = PageDetector(driver)
        self.human_behavior = HumanBehavior(driver, self.screenshot_manager, self.element_finder)
        
        # Session statistics
        self.session_stats = {
            'login_attempts': 0,
            'upload_attempts': 0,
            'errors': [],
            'session_start': time.time()
        }
        
        print("📘 Facebook Login with Image Upload Manager initialized")
    
    def navigate_to_facebook(self) -> bool:
        """Navigate to Facebook landing page."""
        try:
            print("🌐 Navigating to Facebook landing page...")
            self.driver.get("https://www.facebook.com/")
            self.human_behavior.natural_delay(3, 5)
            
            # Screenshot 1: Before login
            print("📸 Taking screenshot before login...")
            self.screenshot_manager.take_screenshot(
                self.driver, "before_login", subfolder="login_process"
            )
            
            if "facebook.com" in self.driver.current_url:
                print("✅ Successfully navigated to Facebook landing page")
                return True
            else:
                print("❌ Failed to navigate to Facebook landing page")
                return False
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            self.session_stats['errors'].append(f"Navigation: {str(e)}")
            return False
    
    def check_login_status(self) -> Dict[str, Any]:
        """Check current Facebook login status."""
        try:
            print("🔍 Checking Facebook login status...")
            
            # Check for logged-in indicators
            logged_in_indicators = [
                (By.XPATH, "//a[contains(@href, 'profile.php')]"),
                (By.XPATH, "//div[@aria-label='Account']"),
                (By.XPATH, "//svg[@aria-label='Your profile']"),
                (By.XPATH, "//div[@role='banner']//a[contains(@href, 'profile.php')]"),
            ]
            
            # Check for logged-out indicators
            logged_out_indicators = [
                (By.NAME, "email"),
                (By.NAME, "pass"),
                (By.XPATH, "//button[@name='login']"),
                (By.XPATH, "//input[@data-testid='royal-email']"),
            ]
            
            # Check for logged-in indicators
            logged_in_count = 0
            for locator_type, locator in logged_in_indicators:
                try:
                    elements = self.driver.find_elements(locator_type, locator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        logged_in_count += 1
                except:
                    continue
            
            # Check for logged-out indicators
            logged_out_count = 0
            for locator_type, locator in logged_out_indicators:
                try:
                    elements = self.driver.find_elements(locator_type, locator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        logged_out_count += 1
                except:
                    continue
            
            # Determine login status
            if logged_in_count >= 1:
                status = "logged_in"
                message = f"✅ User appears to be logged in ({logged_in_count} indicators found)"
            elif logged_out_count >= 1:
                status = "logged_out"
                message = f"❌ User appears to be logged out (login form detected)"
            else:
                status = "unknown"
                message = "⚠ Could not determine login status"
            
            result = {
                'status': status,
                'logged_in_indicators': logged_in_count,
                'logged_out_indicators': logged_out_count,
                'message': message,
                'url': self.driver.current_url
            }
            
            print(message)
            return result
            
        except Exception as e:
            print(f"❌ Error checking login status: {str(e)}")
            return {'status': 'unknown', 'error': str(e)}
    
    def perform_login(self) -> bool:
        """
        Perform automatic Facebook login.
        
        Returns:
            True if login successful
        """
        try:
            print("🔐 Performing automatic login...")
            self.session_stats['login_attempts'] += 1
            
            # Check if already logged in
            login_status = self.check_login_status()
            if login_status.get('status') == 'logged_in':
                print("✅ Already logged in!")
                return True
            
            # Wait for login form
            print("⏳ Waiting for login form...")
            self.human_behavior.natural_delay(2, 3)
            
            # Find email input
            print("🔍 Looking for email input...")
            email_strategies = [
                (By.NAME, "email"),
                (By.ID, "email"),
                (By.XPATH, "//input[@name='email']"),
                (By.XPATH, "//input[@data-testid='royal-email']"),
                (By.XPATH, "//input[@type='text' and @name='email']"),
            ]
            
            email_input = None
            for locator_type, locator in email_strategies:
                try:
                    email_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((locator_type, locator))
                    )
                    if email_input and email_input.is_displayed():
                        print("✅ Found email input")
                        break
                except:
                    continue
            
            if not email_input:
                print("❌ Email input not found")
                return False
            
            # Enter email
            print("⌨ Entering email...")
            self.human_behavior.safe_click(email_input)
            self.human_behavior.natural_delay(0.5, 1.0)
            self.human_behavior.human_like_type(email_input, self.facebook_username, clear_first=True)
            self.human_behavior.natural_delay(1, 2)
            
            # Find password input
            print("🔍 Looking for password input...")
            password_strategies = [
                (By.NAME, "pass"),
                (By.ID, "pass"),
                (By.XPATH, "//input[@name='pass']"),
                (By.XPATH, "//input[@data-testid='royal-pass']"),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            password_input = None
            for locator_type, locator in password_strategies:
                try:
                    password_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((locator_type, locator))
                    )
                    if password_input and password_input.is_displayed():
                        print("✅ Found password input")
                        break
                except:
                    continue
            
            if not password_input:
                print("❌ Password input not found")
                return False
            
            # Enter password
            print("⌨ Entering password...")
            self.human_behavior.safe_click(password_input)
            self.human_behavior.natural_delay(0.5, 1.0)
            self.human_behavior.human_like_type(password_input, self.facebook_password, clear_first=True)
            self.human_behavior.natural_delay(1, 2)
            
            # Find and click Login button
            print("🖱 Clicking Login button...")
            login_button_strategies = [
                (By.NAME, "login"),
                (By.XPATH, "//button[@name='login']"),
                (By.XPATH, "//button[@data-testid='royal-login-button']"),
                (By.XPATH, "//button[@type='submit' and @name='login']"),
                (By.XPATH, "//button[contains(text(), 'Log in') or contains(text(), 'Log In')]"),
            ]
            
            login_button = None
            for locator_type, locator in login_button_strategies:
                try:
                    elements = self.driver.find_...