#!/usr/bin/env python3
"""
BINOMO RAILWAY BOT - FULLY WORKING
✅ Fixed f-string errors
✅ Proper error handling
✅ Chrome auto setup for Railway
"""

import os
import time
import sys
import logging
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==================== DETAILS ====================
BINOMO_EMAIL = "wdqghwdhhwh@gmail.com"
BINOMO_PASSWORD = "Treding_4792"
TELEGRAM_BOT_TOKEN = "8524378866:AAGlA9W3AS6ns8qUFqIZuZApaGkJwKwSWNA"
# =================================================

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
driver = None
is_logged_in = False
login_error = None
current_step = "Not started"

# ==================== CHROME SETUP ====================
def setup_chrome():
    global current_step, login_error
    
    current_step = "Setting up Chrome"
    logger.info("Setting up Chrome driver...")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Try to find Chrome
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser", 
        "/usr/bin/chromium",
        "/opt/google/chrome/chrome"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            options.binary_location = path
            logger.info(f"Found Chrome: {path}")
            break
    
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver created successfully")
        current_step = "Chrome ready"
        return driver
    except Exception as e:
        logger.error(f"Chrome setup failed: {e}")
        login_error = str(e)
        current_step = f"Chrome failed: {str(e)[:50]}"
        return None

# ==================== BINOMO LOGIN ====================
def login_to_binomo(drv):
    global is_logged_in, login_error, current_step
    
    if drv is None:
        login_error = "Driver not initialized"
        return False
    
    try:
        current_step = "Opening Binomo"
        logger.info("Opening Binomo login page...")
        drv.get("https://binomo.com/en/login")
        time.sleep(5)
        logger.info(f"Page loaded: {drv.current_url}")
        
        current_step = "Finding email field"
        email_input = WebDriverWait(drv, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        email_input.send_keys(BINOMO_EMAIL)
        time.sleep(1)
        logger.info("Email entered")
        
        current_step = "Finding password field"
        password_input = drv.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.clear()
        password_input.send_keys(BINOMO_PASSWORD)
        time.sleep(1)
        logger.info("Password entered")
        
        current_step = "Clicking login button"
        login_btn = drv.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(5)
        
        current_step = "Checking login result"
        current_url = drv.current_url
        logger.info(f"After login URL: {current_url}")
        
        if "dashboard" in current_url or "trading" in current_url:
            is_logged_in = True
            current_step = "Logged in"
            logger.info("Login successful!")
            return True
        else:
            login_error = "Login failed - invalid credentials or page changed"
            current_step = "Login failed"
            logger.error(login_error)
            return False
            
    except Exception as e:
        login_error = str(e)
        current_step = f"Error: {str(e)[:50]}"
        logger.error(f"Login error: {e}")
        return False

# ==================== SCREENSHOT ====================
def take_screenshot(drv, asset):
    global current_step, login_error
    
    urls = {
        "EURUSD": "https://binomo.com/en/trading/eurusd",
        "GBPUSD": "https://binomo.com/en/trading/gbpusd",
        "BTCUSD": "https://binomo.com/en/trading/btcusd",
    }
    
    url = urls.get(asset)
    if not url:
        return None
    
    try:
        current_step = f"Opening {asset}"
        drv.get(url)
        time.sleep(8)
        
        current_step = "Taking screenshot"
        screenshot = drv.get_screenshot_as_png()
        current_step = "Screenshot ready"
        return BytesIO(screenshot)
        
    except Exception as e:
        login_error = str(e)
        current_step = f"Screenshot error: {str(e)[:50]}"
        logger.error(f"Screenshot error: {e}")
        return None

# ==================== TELEGRAM BOT ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver, is_logged_in, current_step, login_error
    
    # Format status message safely
    chrome_status = "✅ Ready" if driver is not None else "❌ Not ready"
    login_status = "✅ Done" if is_logged_in else "❌ Pending"
    step_text = current_step if current_step else "Not started"
    error_text = login_error if login_error else "None"
    
    text = f"""
🤖 *BINOMO REAL BOT* 🔥

*Instructions:*
1. Click *Login Binomo* first
2. Wait for login confirmation
3. Click any asset for REAL screenshot

*Status:* 
• Chrome: {chrome_status}
• Login: {login_status}
• Step: `{step_text}`
• Error: `{error_text}`

📌 *Bot takes REAL screenshots from Binomo.com*
"""
    
    keyboard = [
        [InlineKeyboardButton("🔐 Login Binomo", callback_data="login")],
        [InlineKeyboardButton("💰 Check Status", callback_data="status")],
        [InlineKeyboardButton("💵 EUR/USD Chart", callback_data="ss_EURUSD")],
        [InlineKeyboardButton("💷 GBP/USD Chart", callback_data="ss_GBPUSD")],
        [InlineKeyboardButton("🪙 BTC/USD Chart", callback_data="ss_BTCUSD")],
    ]
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver, is_logged_in, current_step, login_error
    
    query = update.callback_query
    await query.answer()
    data = query.data
    
    try:
        if data == "login":
            await query.edit_message_text(
                "🔐 *Logging in...*\n\n"
                "⏳ Please wait 10-15 seconds...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Setup chrome if needed
            if driver is None:
                driver = setup_chrome()
            
            if driver:
                if login_to_binomo(driver):
                    await query.edit_message_text(
                        "✅ *LOGIN SUCCESSFUL!*\n\n"
                        "Now you can:\n"
                        "• Click any asset for REAL screenshot\n"
                        "• Check status anytime",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text(
                        f"❌ *LOGIN FAILED!*\n\n"
                        f"Error: {login_error}\n\n"
                        f"Check:\n"
                        f"• Email: {BINOMO_EMAIL}\n"
                        f"• Password is correct\n"
                        f"• Binomo is accessible",
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await query.edit_message_text(
                    "❌ *CHROME SETUP FAILED!*\n\n"
                    "Make sure Railway has Chrome installed.\n"
                    "Add nixpacks.toml file.",
                    parse_mode=ParseMode.MARKDOWN
                )
        
        elif data == "status":
            chrome_status = "✅ Ready" if driver is not None else "❌ Not ready"
            login_status = "✅ Yes" if is_logged_in else "❌ No"
            
            text = f"""
📊 *BOT STATUS*

*Chrome:* {chrome_status}
*Logged In:* {login_status}
*Step:* `{current_step}`
*Error:* `{login_error}`

*Email:* `{BINOMO_EMAIL[:5]}***`
*Time:* {datetime.now().strftime('%H:%M:%S')}
"""
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        
        elif data.startswith("ss_"):
            if not is_logged_in:
                await query.edit_message_text(
                    "❌ *Not logged in!*\n\n"
                    "Please click 'Login Binomo' first.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            asset = data.replace("ss_", "")
            asset_names = {"EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "BTCUSD": "BTC/USD"}
            asset_name = asset_names.get(asset, asset)
            
            await query.edit_message_text(
                f"📸 *Taking screenshot of {asset_name}...*\n\n"
                f"⏳ Loading chart...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            screenshot = take_screenshot(driver, asset)
            
            if screenshot:
                caption = f"""
📸 *REAL BINOMO SCREENSHOT*

*Asset:* {asset_name}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Captured from real Binomo.com!
"""
                await query.message.reply_photo(
                    photo=InputFile(screenshot, filename=f"binomo_{asset}.png"),
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
                await query.delete_message()
            else:
                await query.edit_message_text(
                    f"❌ *Screenshot failed!*\n\n"
                    f"Error: {login_error}\n\n"
                    f"Try re-login with 'Login Binomo'",
                    parse_mode=ParseMode.MARKDOWN
                )
                
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)[:100]}", parse_mode=ParseMode.MARKDOWN)

# ==================== MAIN ====================
def main():
    print("="*50)
    print("🔥 BINOMO RAILWAY BOT")
    print("="*50)
    print(f"Email: {BINOMO_EMAIL}")
    print(f"Bot: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("="*50)
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot running! Send /start on Telegram")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
