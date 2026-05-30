#!/usr/bin/env python3
"""
BINOMO FULL FUNCTIONAL BOT - WITH DEBUG MODE
✅ Har step ka status dikhega
✅ Proper error messages
✅ Real-time logging
✅ Railway compatible
"""

import os
import time
import sys
import json
import logging
import requests
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# ==================== DETAILS ====================
BINOMO_EMAIL = "wdqghwdhhwh@gmail.com"
BINOMO_PASSWORD = "Treding_4792"
TELEGRAM_BOT_TOKEN = "8524378866:AAGlA9W3AS6ns8qUFqIZuZApaGkJwKwSWNA"
# =================================================

# Setup logging - VERBOSE MODE
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Global bot instance
binomo_driver = None
login_status = {"logged_in": False, "error": None, "step": "Not started"}

# ==================== CHROME SETUP WITH DEBUG ====================
def setup_chrome():
    """Setup Chrome with full debugging"""
    global login_status
    
    logger.info("="*50)
    logger.info("🔧 STEP 1: Setting up Chrome Driver")
    login_status["step"] = "Setting up Chrome"
    
    options = Options()
    
    # Headless mode for Railway
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Chrome binary paths for Railway
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/opt/google/chrome/chrome",
        "/.chromium/chrome",
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            options.binary_location = path
            logger.info(f"✅ Chrome binary found: {path}")
            break
    else:
        logger.warning("⚠️ Chrome binary not found, using default")
    
    try:
        logger.info("🚀 Launching Chrome driver...")
        driver = webdriver.Chrome(options=options)
        logger.info("✅ Chrome driver launched successfully!")
        login_status["step"] = "Chrome ready"
        return driver
    except Exception as e:
        logger.error(f"❌ Chrome driver failed: {e}")
        login_status["error"] = f"Chrome error: {str(e)[:200]}"
        return None

# ==================== BINOMO LOGIN WITH STEP-BY-STEP DEBUG ====================
def login_binomo(driver):
    """Login with full debugging"""
    global login_status
    
    logger.info("="*50)
    logger.info("🔐 STEP 2: Starting Binomo Login")
    login_status["step"] = "Opening Binomo"
    
    try:
        # Step 1: Open login page
        logger.info("🌐 Opening https://binomo.com/en/login")
        driver.get("https://binomo.com/en/login")
        time.sleep(5)
        logger.info(f"✅ Page loaded. Current URL: {driver.current_url}")
        login_status["step"] = "Page loaded"
        
        # Step 2: Check for login form
        logger.info("📝 Looking for email input field...")
        try:
            email_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            logger.info("✅ Email input field found")
        except TimeoutException:
            logger.error("❌ Email input field not found!")
            logger.info("📸 Saving page source for debugging...")
            with open("debug_page.html", "w") as f:
                f.write(driver.page_source)
            logger.info("Page source saved to debug_page.html")
            login_status["error"] = "Login form not found"
            return False
        
        # Step 3: Enter email
        logger.info(f"📧 Entering email: {BINOMO_EMAIL}")
        email_input.clear()
        email_input.send_keys(BINOMO_EMAIL)
        time.sleep(1)
        logger.info("✅ Email entered")
        login_status["step"] = "Email entered"
        
        # Step 4: Find password field
        logger.info("🔑 Looking for password input field...")
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            logger.info("✅ Password input field found")
        except NoSuchElementException:
            logger.error("❌ Password field not found!")
            login_status["error"] = "Password field not found"
            return False
        
        # Step 5: Enter password
        logger.info("🔐 Entering password...")
        password_input.clear()
        password_input.send_keys(BINOMO_PASSWORD)
        time.sleep(1)
        logger.info("✅ Password entered")
        login_status["step"] = "Password entered"
        
        # Step 6: Find login button
        logger.info("🔘 Looking for login button...")
        login_button = None
        button_selectors = [
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]",
            "//button[@type='submit']",
            "//button[contains(@class, 'login')]"
        ]
        
        for selector in button_selectors:
            try:
                login_button = driver.find_element(By.XPATH, selector)
                logger.info(f"✅ Login button found with selector: {selector}")
                break
            except:
                continue
        
        if not login_button:
            logger.error("❌ Login button not found!")
            login_status["error"] = "Login button not found"
            return False
        
        # Step 7: Click login
        logger.info("👉 Clicking login button...")
        login_button.click()
        time.sleep(5)
        logger.info("✅ Login button clicked")
        login_status["step"] = "Login clicked"
        
        # Step 8: Check login result
        current_url = driver.current_url
        logger.info(f"📍 Current URL after login: {current_url}")
        
        if "dashboard" in current_url or "trading" in current_url or "account" in current_url:
            logger.info("🎉 LOGIN SUCCESSFUL!")
            login_status["logged_in"] = True
            login_status["step"] = "Logged in"
            return True
        else:
            logger.error("❌ Login failed - URL doesn't indicate success")
            
            # Check for error message
            try:
                error_msg = driver.find_element(By.CSS_SELECTOR, "[class*='error'], [class*='Error'], .alert")
                logger.error(f"Error message on page: {error_msg.text}")
                login_status["error"] = f"Login error: {error_msg.text[:100]}"
            except:
                pass
            
            login_status["error"] = "Login failed - check credentials"
            return False
            
    except Exception as e:
        logger.error(f"❌ Login exception: {e}")
        login_status["error"] = str(e)[:200]
        return False

# ==================== SCREENSHOT FUNCTION ====================
def take_trading_screenshot(driver, asset_symbol):
    """Take screenshot of trading page"""
    global login_status
    
    logger.info("="*50)
    logger.info(f"📸 STEP: Taking screenshot for {asset_symbol}")
    login_status["step"] = f"Opening {asset_symbol}"
    
    urls = {
        "EURUSD": "https://binomo.com/en/trading/eurusd",
        "GBPUSD": "https://binomo.com/en/trading/gbpusd",
        "BTCUSD": "https://binomo.com/en/trading/btcusd",
    }
    
    url = urls.get(asset_symbol)
    if not url:
        logger.error(f"❌ Unknown symbol: {asset_symbol}")
        return None
    
    try:
        logger.info(f"🌐 Navigating to: {url}")
        driver.get(url)
        time.sleep(8)  # Wait for chart to load
        logger.info(f"✅ Page loaded: {driver.current_url}")
        login_status["step"] = f"Chart loading"
        
        # Scroll to chart
        try:
            chart_selectors = ["canvas", "[class*='chart']", "[class*='Chart']", "[id*='chart']"]
            for selector in chart_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    driver.execute_script("arguments[0].scrollIntoView();", elements[0])
                    logger.info(f"✅ Scrolled to chart element: {selector}")
                    time.sleep(2)
                    break
        except Exception as e:
            logger.warning(f"Could not scroll to chart: {e}")
        
        # Take screenshot
        logger.info("📸 Capturing screenshot...")
        screenshot = driver.get_screenshot_as_png()
        logger.info(f"✅ Screenshot captured! Size: {len(screenshot)} bytes")
        login_status["step"] = "Screenshot taken"
        
        return BytesIO(screenshot)
        
    except Exception as e:
        logger.error(f"❌ Screenshot error: {e}")
        login_status["error"] = str(e)[:200]
        return None

# ==================== TELEGRAM BOT ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Login Binomo", callback_data="login")],
        [InlineKeyboardButton("💰 Check Status", callback_data="status")],
        [InlineKeyboardButton("💵 EUR/USD Chart", callback_data="ss_EURUSD")],
        [InlineKeyboardButton("💷 GBP/USD Chart", callback_data="ss_GBPUSD")],
        [InlineKeyboardButton("🪙 BTC/USD Chart", callback_data="ss_BTCUSD")],
        [InlineKeyboardButton("📊 Debug Info", callback_data="debug")],
    ]
    
    text = """
🤖 *BINOMO REAL BOT* 🔥

*Instructions:*
1. Click *Login Binomo* first
2. Wait for login confirmation
3. Click any asset for REAL screenshot

*Status:* 
• Chrome: {'✅ Ready' if binomo_driver else '❌ Not ready'}
• Login: {'✅ Done' if login_status['logged_in'] else '❌ Pending'}
• Step: `{}`

📌 *Bot takes REAL screenshots from Binomo.com*
""".format(login_status.get('step', 'Not started'))
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global binomo_driver, login_status
    
    query = update.callback_query
    await query.answer()
    data = query.data
    
    try:
        if data == "login":
            await query.edit_message_text(
                "🔐 *Starting Binomo Login...*\n\n"
                "```\n"
                "1️⃣ Setting up Chrome driver...\n"
                "2️⃣ Opening Binomo...\n"
                "3️⃣ Entering credentials...\n"
                "4️⃣ Submitting...\n"
                "```\n\n"
                "⏳ Please wait...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Setup driver
            if binomo_driver is None:
                binomo_driver = setup_chrome()
            
            if binomo_driver:
                # Login
                if login_binomo(binomo_driver):
                    await query.edit_message_text(
                        "✅ *LOGIN SUCCESSFUL!*\n\n"
                        f"📍 Current URL: {binomo_driver.current_url}\n\n"
                        "Now you can:\n"
                        "• Click any asset for REAL screenshot\n"
                        "• Check status anytime",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text(
                        f"❌ *LOGIN FAILED!*\n\n"
                        f"Error: {login_status.get('error', 'Unknown error')}\n\n"
                        f"Step failed at: {login_status.get('step', 'Unknown')}\n\n"
                        "Check:\n"
                        "• Email and password are correct\n"
                        "• Internet connection\n"
                        "• Binomo is accessible",
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await query.edit_message_text(
                    "❌ *CHROME SETUP FAILED!*\n\n"
                    "Chrome driver could not be initialized.\n\n"
                    "Railway needs Chrome installed.\n"
                    "Check build logs.",
                    parse_mode=ParseMode.MARKDOWN
                )
        
        elif data == "status":
            status_text = f"""
📊 *BOT STATUS*

*Chrome Driver:* {'✅ Active' if binomo_driver else '❌ Not initialized'}
*Logged In:* {'✅ Yes' if login_status['logged_in'] else '❌ No'}
*Current Step:* `{login_status.get('step', 'None')}`
*Last Error:* `{login_status.get('error', 'None')}`

*Session Info:*
• Email: `{BINOMO_EMAIL[:5]}***`
• Time: {datetime.now().strftime('%H:%M:%S')}

*Commands:*
• /start - Restart bot
• Login Binomo - First time login
• Asset buttons - Take screenshot
"""
            await query.edit_message_text(status_text, parse_mode=ParseMode.MARKDOWN)
        
        elif data.startswith("ss_"):
            if not binomo_driver or not login_status['logged_in']:
                await query.edit_message_text(
                    "❌ *Not logged in!*\n\n"
                    "Please click 'Login Binomo' first.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            symbol = data.replace("ss_", "")
            asset_names = {"EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "BTCUSD": "BTC/USD"}
            asset_name = asset_names.get(symbol, symbol)
            
            await query.edit_message_text(
                f"📸 *Taking screenshot of {asset_name}...*\n\n"
                f"├ Opening trading page\n"
                f"├ Loading chart\n"
                f"├ Capturing screenshot\n"
                f"└ Sending...\n\n"
                f"⏳ Please wait...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            screenshot = take_trading_screenshot(binomo_driver, symbol)
            
            if screenshot:
                caption = f"""
📸 *REAL BINOMO SCREENSHOT*

*Asset:* {asset_name}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Status:* ✅ Captured from real Binomo.com

⚠️ This is an actual screenshot from Binomo's trading page!
"""
                keyboard = [[InlineKeyboardButton("🔄 Back", callback_data="back")]]
                await query.message.reply_photo(
                    photo=InputFile(screenshot, filename=f"binomo_{symbol}_{int(time.time())}.png"),
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                await query.delete_message()
            else:
                await query.edit_message_text(
                    f"❌ *Screenshot failed!*\n\n"
                    f"Error: {login_status.get('error', 'Unknown')}\n\n"
                    f"Step failed at: {login_status.get('step', 'Unknown')}\n\n"
                    f"Try re-login with /start",
                    parse_mode=ParseMode.MARKDOWN
                )
        
        elif data == "debug":
            debug_text = f"""
🔧 *DEBUG INFORMATION*

*Chrome Driver:* {binomo_driver is not None}
*Logged In:* {login_status['logged_in']}
*Current Step:* {login_status.get('step')}
*Error:* {login_status.get('error')}

*Environment:*
• Python: {sys.version}
• Platform: {sys.platform}

*To see full logs:*
Check Railway deployment logs
"""
            await query.edit_message_text(debug_text, parse_mode=ParseMode.MARKDOWN)
        
        elif data == "back":
            await start(update, context)
            
    except Exception as e:
        logger.error(f"Handler error: {e}", exc_info=True)
        await query.edit_message_text(f"❌ Error: {str(e)[:200]}\n\nCheck logs for details", parse_mode=ParseMode.MARKDOWN)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text(f"❌ Error: {str(context.error)[:200]}")

# ==================== MAIN ====================
def main():
    print("="*60)
    print("🔥 BINOMO FULL FUNCTIONAL BOT")
    print("="*60)
    print(f"📧 Email: {BINOMO_EMAIL}")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("="*60)
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is running! Send /start on Telegram")
    print("="*60)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
