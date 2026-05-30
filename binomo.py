#!/usr/bin/env python3
"""
BINOMO RAILWAY BOT - WITH CHROME FIX
"""

import os
import time
import logging
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ==================== DETAILS ====================
BINOMO_EMAIL = "wdqghwdhhwh@gmail.com"
BINOMO_PASSWORD = "Treding_4792"
TELEGRAM_BOT_TOKEN = "8524378866:AAGlA9W3AS6ns8qUFqIZuZApaGkJwKwSWNA"
# =================================================

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

driver = None
is_logged_in = False
last_error = None

def get_chrome_path():
    """Find Chrome/Chromium path on Railway"""
    paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/nix/store/*/bin/chromium",
    ]
    import glob
    for path in paths:
        if '*' in path:
            matches = glob.glob(path)
            if matches:
                return matches[0]
        elif os.path.exists(path):
            return path
    return None

def setup_driver():
    global last_error
    try:
        logger.info("Setting up Chrome driver...")
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        chrome_path = get_chrome_path()
        if chrome_path:
            options.binary_location = chrome_path
            logger.info(f"Using Chrome at: {chrome_path}")
        
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver ready!")
        return driver
    except Exception as e:
        last_error = str(e)
        logger.error(f"Chrome setup failed: {e}")
        return None

def login():
    global driver, is_logged_in, last_error
    if driver is None:
        driver = setup_driver()
    if driver is None:
        return False
    
    try:
        driver.get("https://binomo.com/en/login")
        time.sleep(5)
        
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(BINOMO_EMAIL)
        time.sleep(1)
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(BINOMO_PASSWORD)
        time.sleep(1)
        
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_btn.click()
        time.sleep(5)
        
        if "dashboard" in driver.current_url or "trading" in driver.current_url:
            is_logged_in = True
            logger.info("Login successful!")
            return True
        else:
            last_error = "Login failed - invalid credentials"
            return False
    except Exception as e:
        last_error = str(e)
        logger.error(f"Login error: {e}")
        return False

def take_ss(asset):
    global driver, last_error
    urls = {"EURUSD": "https://binomo.com/en/trading/eurusd", "GBPUSD": "https://binomo.com/en/trading/gbpusd", "BTCUSD": "https://binomo.com/en/trading/btcusd"}
    url = urls.get(asset)
    if not url:
        return None
    try:
        driver.get(url)
        time.sleep(8)
        return BytesIO(driver.get_screenshot_as_png())
    except Exception as e:
        last_error = str(e)
        return None

# ==================== TELEGRAM ====================
async def start(update, context):
    status = "✅ Ready" if driver else "❌ Not ready"
    login_status = "✅ Done" if is_logged_in else "❌ Pending"
    text = f"🤖 *Binomo Bot*\n\n*Chrome:* {status}\n*Login:* {login_status}\n*Error:* `{last_error or 'None'}`\n\nClick 'Login Binomo' first."
    keyboard = [[InlineKeyboardButton("🔐 Login", callback_data="login")],
                [InlineKeyboardButton("💵 EUR/USD", callback_data="ss_EURUSD")],
                [InlineKeyboardButton("💷 GBP/USD", callback_data="ss_GBPUSD")],
                [InlineKeyboardButton("🪙 BTC/USD", callback_data="ss_BTCUSD")],
                [InlineKeyboardButton("📊 Status", callback_data="status")]]
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def handler(update, context):
    global driver, is_logged_in
    query = update.callback_query
    await query.answer()
    data = query.data
    
    try:
        if data == "login":
            await query.edit_message_text("🔐 Logging in...")
            if login():
                await query.edit_message_text("✅ Login successful! Now click any asset.")
            else:
                await query.edit_message_text(f"❌ Login failed: {last_error}")
        
        elif data == "status":
            text = f"Chrome: {'✅' if driver else '❌'}\nLogin: {'✅' if is_logged_in else '❌'}\nError: {last_error or 'None'}"
            await query.edit_message_text(text)
        
        elif data.startswith("ss_"):
            if not is_logged_in:
                await query.edit_message_text("❌ Login first!")
                return
            asset = data.replace("ss_", "")
            await query.edit_message_text(f"📸 Taking screenshot of {asset}...")
            ss = take_ss(asset)
            if ss:
                await query.message.reply_photo(photo=InputFile(ss, filename=f"{asset}.png"), caption=f"📸 {asset} - Real Binomo screenshot")
                await query.delete_message()
            else:
                await query.edit_message_text(f"❌ Screenshot failed: {last_error}")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)[:100]}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handler))
    print("Bot running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
