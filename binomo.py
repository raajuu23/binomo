#!/usr/bin/env python3
"""
BINOMO REAL SCREENSHOT BOT - Asli Binomo Page Ka Screenshot
✅ Binomo.com pe REAL login karega
✅ Real candlestick chart ka screenshot lega
✅ Real prices, real indicators
✅ Telegram pe bhejega asli screenshot
"""

import os
import time
import asyncio
import logging
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==================== 📝 TERI DETAILS ====================
BINOMO_EMAIL = "wdqghwdhhwh@gmail.com"
BINOMO_PASSWORD = "Treding_4792"
TELEGRAM_BOT_TOKEN = "8524378866:AAGlA9W3AS6ns8qUFqIZuZApaGkJwKwSWNA"
# =========================================================

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ASSETS URLS ====================
ASSETS = {
    "EURUSD": {"name": "💵 EUR/USD", "url": "https://binomo.com/en/trading/eurusd", "symbol": "EURUSD"},
    "GBPUSD": {"name": "💷 GBP/USD", "url": "https://binomo.com/en/trading/gbpusd", "symbol": "GBPUSD"},
    "BTCUSD": {"name": "🪙 BTC/USD", "url": "https://binomo.com/en/trading/btcusd", "symbol": "BTCUSD"},
    "ETHUSD": {"name": "🔷 ETH/USD", "url": "https://binomo.com/en/trading/ethusd", "symbol": "ETHUSD"},
    "XAUUSD": {"name": "🥇 Gold", "url": "https://binomo.com/en/trading/xauusd", "symbol": "XAUUSD"},
}

# ==================== BINOMO REAL BROWSER ====================
class BinomoRealBot:
    def __init__(self):
        self.driver = None
        self.logged_in = False
        
    def setup_driver(self):
        """Setup Chrome driver with proper options"""
        options = Options()
        
        # Important: Keep visible for screenshot, but can be headless for server
        # options.add_argument('--headless')  # Server pe headless karo
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return self.driver
    
    def login(self):
        """Login to Binomo"""
        try:
            logger.info("🔐 Setting up browser...")
            self.setup_driver()
            
            logger.info("🌐 Opening Binomo login page...")
            self.driver.get("https://binomo.com/en/login")
            time.sleep(3)
            
            # Accept cookies
            try:
                cookie_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                cookie_btn.click()
                time.sleep(1)
                logger.info("🍪 Cookies accepted")
            except:
                pass
            
            # Enter email
            logger.info("📧 Entering email...")
            email_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.clear()
            email_input.send_keys(BINOMO_EMAIL)
            time.sleep(1)
            
            # Enter password
            logger.info("🔑 Entering password...")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys(BINOMO_PASSWORD)
            time.sleep(1)
            
            # Click login
            logger.info("🚪 Clicking login button...")
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if logged in
            current_url = self.driver.current_url
            if "dashboard" in current_url or "trading" in current_url or "account" in current_url:
                logger.info("✅ Binomo Login Successful!")
                self.logged_in = True
                return True
            else:
                logger.error(f"❌ Login failed. Current URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def navigate_to_asset(self, asset_url):
        """Navigate to specific asset trading page"""
        try:
            logger.info(f"🌐 Navigating to {asset_url}...")
            self.driver.get(asset_url)
            time.sleep(5)  # Wait for chart to load
            
            # Wait for chart to be visible
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "canvas, .chart-container, [class*='chart']"))
                )
                logger.info("✅ Chart loaded")
            except:
                logger.warning("Chart might not be fully loaded")
            
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def take_screenshot(self, asset_name):
        """Take screenshot of the trading page"""
        try:
            # Wait a bit for everything to load
            time.sleep(3)
            
            # Try to find chart area and scroll to it
            try:
                chart_element = self.driver.find_element(By.CSS_SELECTOR, "canvas, [class*='chart'], [class*='Chart']")
                self.driver.execute_script("arguments[0].scrollIntoView();", chart_element)
                time.sleep(1)
            except:
                pass
            
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            logger.info(f"📸 Screenshot taken for {asset_name}")
            return BytesIO(screenshot)
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None
    
    def get_current_price(self):
        """Try to get current price from the page"""
        try:
            price_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='price'], [class*='Price'], [data-type='price']")
            for elem in price_elements:
                text = elem.text
                if text and any(c.isdigit() for c in text):
                    return text
            return "N/A"
        except:
            return "N/A"
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Browser closed")

# Global bot instance
binomo_bot = None

# ==================== TELEGRAM BOT ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("💵 EUR/USD", callback_data="ss_EURUSD"),
         InlineKeyboardButton("💷 GBP/USD", callback_data="ss_GBPUSD")],
        [InlineKeyboardButton("🪙 BTC/USD", callback_data="ss_BTCUSD"),
         InlineKeyboardButton("🔷 ETH/USD", callback_data="ss_ETHUSD")],
        [InlineKeyboardButton("🥇 Gold", callback_data="ss_XAUUSD")],
        [InlineKeyboardButton("🔐 Login Binomo First", callback_data="login_binomo")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    
    text = """
🤖 *BINOMO REAL SCREENSHOT BOT* 🔥

✅ *Features:*
• Real Binomo.com Login
• Real Trading Page Screenshots
• Real Candlestick Charts
• Live Prices

📌 *Instructions:*
1. Click "Login Binomo First"
2. Wait for login confirmation
3. Select any asset
4. Get REAL screenshot from Binomo

⚠️ *Bot will take screenshot directly from Binomo website!*
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    global binomo_bot
    
    query = update.callback_query
    await query.answer()
    data = query.data
    
    try:
        if data == "login_binomo":
            await handle_login(query)
        
        elif data.startswith("ss_"):
            symbol = data.replace("ss_", "")
            await handle_screenshot(query, symbol)
        
        elif data == "help":
            await handle_help(query)
        
        elif data == "back":
            await handle_back(query)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)[:100]}\n\nUse /start", parse_mode=ParseMode.MARKDOWN)

async def handle_login(query):
    """Handle Binomo login"""
    global binomo_bot
    
    await query.edit_message_text(
        "🔐 *Logging into Binomo...*\n\n"
        "├ 🌐 Opening browser\n"
        "├ 📧 Entering credentials\n"
        "├ 🔑 Submitting login\n"
        "└ ⏳ Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Create bot instance if not exists
        if binomo_bot is None:
            binomo_bot = BinomoRealBot()
        
        # Login
        if binomo_bot.login():
            # Keep browser alive in background
            keyboard = [[InlineKeyboardButton("📸 Take Screenshot", callback_data="back")]]
            await query.edit_message_text(
                "✅ *Binomo Login Successful!*\n\n"
                "Now you can:\n"
                "├ Click on any asset to get REAL screenshot\n"
                "├ Bot will capture the actual Binomo trading page\n"
                "└ Chart will show real candlesticks\n\n"
                "👇 *Select an asset from menu:*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await handle_back(query)
        else:
            await query.edit_message_text(
                "❌ *Login Failed!*\n\n"
                "Please check:\n"
                "├ Email and password are correct\n"
                "├ Internet connection is working\n"
                "└ Binomo website is accessible\n\n"
                "Use /start to try again",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        await query.edit_message_text(f"❌ Login error: {str(e)[:200]}", parse_mode=ParseMode.MARKDOWN)

async def handle_screenshot(query, symbol):
    """Take screenshot of asset"""
    global binomo_bot
    
    asset = ASSETS.get(symbol)
    if not asset:
        await query.edit_message_text("❌ Asset not found!", parse_mode=ParseMode.MARKDOWN)
        return
    
    await query.edit_message_text(
        f"📸 *Taking REAL screenshot from Binomo...*\n\n"
        f"├ Asset: {asset['name']}\n"
        f"├ Opening trading page\n"
        f"├ Capturing chart\n"
        f"└ Sending...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Check if logged in
        if binomo_bot is None or not binomo_bot.logged_in:
            await query.edit_message_text(
                "❌ *Not logged in!*\n\n"
                "Please click 'Login Binomo First' before taking screenshot.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Navigate to asset
        if binomo_bot.navigate_to_asset(asset["url"]):
            # Get current price
            price = binomo_bot.get_current_price()
            
            # Take screenshot
            screenshot = binomo_bot.take_screenshot(asset["name"])
            
            if screenshot:
                # Prepare caption
                caption = f"""
📸 *REAL BINOMO SCREENSHOT*

{asset['name']}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ *This is a REAL screenshot directly from Binomo.com*
├ Real candlestick chart
├ Real live prices
├ Real indicators
└ Current price: {price}

⚠️ Screenshot shows the actual Binomo trading page!
"""
                keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data=f"ss_{symbol}")],
                           [InlineKeyboardButton("🔙 Back", callback_data="back")]]
                
                await query.edit_message_text("📤 *Sending screenshot...*", parse_mode=ParseMode.MARKDOWN)
                await query.message.reply_photo(
                    photo=InputFile(screenshot, filename=f"binomo_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"),
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_text(
                    "❌ *Failed to take screenshot!*\n\n"
                    "The Binomo page might not have loaded properly.\n"
                    "Please try again.",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await query.edit_message_text(
                "❌ *Failed to load trading page!*\n\n"
                "Please try again or re-login.",
                parse_mode=ParseMode.MARKDOWN
            )
            
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)[:200]}", parse_mode=ParseMode.MARKDOWN)

async def handle_help(query):
    """Help menu"""
    text = """
ℹ️ *BINOMO REAL SCREENSHOT BOT - HELP*

📌 *How to use:*

1️⃣ *First, login to Binomo*
   • Click "Login Binomo First"
   • Bot will login with your credentials
   • Wait for confirmation

2️⃣ *Take REAL screenshots*
   • Select any asset (EUR/USD, BTC, etc.)
   • Bot opens actual Binomo trading page
   • Takes screenshot of REAL chart

3️⃣ *Get Screenshot*
   • You receive actual Binomo page screenshot
   • Shows real candlesticks, prices, indicators

⚠️ *Important:*
• Login only once per session
• Bot keeps browser open for faster access
• Screenshots are from REAL Binomo.com

✅ *This is NOT a simulated chart - It's REAL!*
"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_back(query):
    """Back to main menu"""
    keyboard = [
        [InlineKeyboardButton("💵 EUR/USD", callback_data="ss_EURUSD"),
         InlineKeyboardButton("💷 GBP/USD", callback_data="ss_GBPUSD")],
        [InlineKeyboardButton("🪙 BTC/USD", callback_data="ss_BTCUSD"),
         InlineKeyboardButton("🔷 ETH/USD", callback_data="ss_ETHUSD")],
        [InlineKeyboardButton("🥇 Gold", callback_data="ss_XAUUSD")],
        [InlineKeyboardButton("🔐 Login Binomo First", callback_data="login_binomo")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    text = "🤖 *BINOMO REAL SCREENSHOT BOT*\n\n📌 *First, click 'Login Binomo First'*\n\n👇 *Then select an asset:*"
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== MAIN ====================
def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     🔥 BINOMO REAL SCREENSHOT BOT - ASLI WALA 🔥             ║
    ║                                                              ║
    ║  ✅ Real Binomo.com Login                                    ║
    ║  ✅ Real Trading Page Screenshot                             ║
    ║  ✅ Real Candlestick Charts                                  ║
    ║  ✅ Real Prices & Indicators                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📧 Email: {BINOMO_EMAIL}")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("\n🚀 Starting Telegram Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot is running! Send /start on Telegram")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
