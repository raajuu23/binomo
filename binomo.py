#!/usr/bin/env python3
"""
BINOMO RAILWAY BOT - Chrome Auto Setup
"""

import os
import time
import asyncio
import logging
import requests
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Selenium with Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ==================== 📝 TERI DETAILS ====================
BINOMO_EMAIL = "wdqghwdhhwh@gmail.com"
BINOMO_PASSWORD = "Treding_4792"
TELEGRAM_BOT_TOKEN = "8524378866:AAGlA9W3AS6ns8qUFqIZuZApaGkJwKwSWNA"
# =========================================================

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway Chrome paths
CHROME_PATHS = [
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/opt/google/chrome/chrome",
    "/.chromium/chrome",
]

class BinomoRailwayBot:
    def __init__(self):
        self.driver = None
        self.logged_in = False
    
    def get_chrome_path(self):
        """Find Chrome executable"""
        for path in CHROME_PATHS:
            if os.path.exists(path):
                return path
        return None
    
    def setup_driver(self):
        """Setup Chrome for Railway"""
        options = Options()
        
        # Railway specific options
        options.add_argument('--headless=new')  # Headless mode for Railway
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
        
        # User agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36')
        
        # Set binary if found
        chrome_path = self.get_chrome_path()
        if chrome_path:
            options.binary_location = chrome_path
            logger.info(f"Using Chrome at: {chrome_path}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("✅ Chrome driver setup complete")
            return True
        except Exception as e:
            logger.error(f"Chrome setup failed: {e}")
            return False
    
    def login(self):
        """Login to Binomo"""
        try:
            if not self.setup_driver():
                return False
            
            logger.info("Opening Binomo...")
            self.driver.get("https://binomo.com/en/login")
            time.sleep(5)
            
            # Accept cookies
            try:
                cookie_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                cookie_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Email
            email_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.send_keys(BINOMO_EMAIL)
            time.sleep(1)
            
            # Password
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.send_keys(BINOMO_PASSWORD)
            time.sleep(1)
            
            # Login button
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            time.sleep(5)
            
            self.logged_in = True
            logger.info("✅ Binomo Login Successful!")
            return True
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def take_screenshot(self, asset_url):
        """Take screenshot"""
        try:
            self.driver.get(asset_url)
            time.sleep(5)
            
            # Scroll to chart
            try:
                chart = self.driver.find_element(By.CSS_SELECTOR, "canvas, [class*='chart']")
                self.driver.execute_script("arguments[0].scrollIntoView();", chart)
                time.sleep(2)
            except:
                pass
            
            screenshot = self.driver.get_screenshot_as_png()
            return BytesIO(screenshot)
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None
    
    def close(self):
        if self.driver:
            self.driver.quit()

# ==================== TELEGRAM BOT ====================
binomo_bot = None

ASSETS = {
    "EURUSD": {"name": "💵 EUR/USD", "url": "https://binomo.com/en/trading/eurusd"},
    "GBPUSD": {"name": "💷 GBP/USD", "url": "https://binomo.com/en/trading/gbpusd"},
    "BTCUSD": {"name": "🪙 BTC/USD", "url": "https://binomo.com/en/trading/btcusd"},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💵 EUR/USD", callback_data="ss_EURUSD"),
         InlineKeyboardButton("💷 GBP/USD", callback_data="ss_GBPUSD")],
        [InlineKeyboardButton("🪙 BTC/USD", callback_data="ss_BTCUSD")],
        [InlineKeyboardButton("🔐 Login Binomo", callback_data="login")],
    ]
    text = "🤖 *Binomo Railway Bot*\n\nFirst click 'Login Binomo'"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global binomo_bot
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "login":
            await query.edit_message_text("🔐 Logging in... Please wait...")
            binomo_bot = BinomoRailwayBot()
            if binomo_bot.login():
                keyboard = [[InlineKeyboardButton("📸 Take Screenshot", callback_data="back")]]
                await query.edit_message_text("✅ Login successful!\n\nSelect an asset:", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💵 EUR/USD", callback_data="ss_EURUSD"),
                     InlineKeyboardButton("💷 GBP/USD", callback_data="ss_GBPUSD")],
                    [InlineKeyboardButton("🪙 BTC/USD", callback_data="ss_BTCUSD")],
                ]))
            else:
                await query.edit_message_text("❌ Login failed! Check credentials.")
        
        elif query.data.startswith("ss_"):
            if not binomo_bot or not binomo_bot.logged_in:
                await query.edit_message_text("❌ Please login first!")
                return
            
            symbol = query.data.replace("ss_", "")
            asset = ASSETS.get(symbol)
            if asset:
                await query.edit_message_text(f"📸 Taking screenshot of {asset['name']}...")
                screenshot = binomo_bot.take_screenshot(asset["url"])
                if screenshot:
                    await query.message.reply_photo(
                        photo=InputFile(screenshot, filename=f"{symbol}.png"),
                        caption=f"📸 *{asset['name']}*\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✅ Real Binomo.com screenshot!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text("❌ Screenshot failed!")
        
        elif query.data == "back":
            await start(update, context)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)[:100]}")

# ==================== MAIN ====================
def main():
    print("🚀 Binomo Railway Bot Starting...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
