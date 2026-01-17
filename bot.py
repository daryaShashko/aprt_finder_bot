import os
import logging
import asyncio
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import database
import scraper
import ai_agent

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLX_URL = os.getenv("OLX_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 15)) * 60  # convert to seconds
USER_ID = os.getenv("USER_ID")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def check_for_ads(context: ContextTypes.DEFAULT_TYPE):
    """Background task to check for new ads."""
    logger.info("Checking for new ads...")
    
    if not OLX_URL:
        logger.error("OLX_URL not set in .env")
        return

    ad_urls = scraper.fetch_ad_urls(OLX_URL)
    logger.info(f"Examples of fetched URLs: {ad_urls[:3]}") # Debug log
    
    new_ads_count = 0
    for url in ad_urls:
         # Extract a simple ID from the URL for the DB
         # URL format example: .../mieszkania/wynajem/gdansk/q-.../ or /d/oferta/TITLE-ID.html
         # We'll use the full URL as ID for simplicity and robustness against ID format changes, 
         # but realistically scraping the ID from the end (e.g. ID12345.html) is better.
         # For now, let's just hash the URL or use the URL itself as the key.
         # Using the URL is fine for now.
         ad_id = url
         
         if not database.is_ad_seen(ad_id):
            logger.info(f"New ad found: {url}")
            # Mark as seen immediately to avoid double processing on error, 
            # or move to end if we want strict "only if sent" logic.
            # Best practice: process first, then mark.
            
            content = scraper.fetch_ad_content(url)
            if content:
                analysis = ai_agent.analyze_ad(content)
                
                if analysis:
                    message = (
                        f"🏠 **New Apartment Found!**\n\n"
                        f"💰 **Cost:** {analysis.get('total_cost', 'N/A')}\n"
                        f"💵 **Deposit:** {analysis.get('deposit', 'N/A')}\n"
                        f"🐾 **Pets:** {'✅ Allowed' if analysis.get('pets_allowed') else '❌ Not allowed/Unknown'}\n\n"
                        f"📝 **Summary:** {analysis.get('summary_ru', 'No summary')}\n\n"
                        f"🔗 [Link to Ad]({url})"
                    )
                else:
                    message = f"🏠 **New Apartment Found!**\n\n(AI Analysis Failed)\n\n🔗 [Link to Ad]({url})"
                
                # Send to specific user if defined, or broadcasting could be implemented
                target_chat_id = USER_ID 
                # If USER_ID is not set, we can't push proactively unless we store chat_ids from /start.
                # For this task, we will assume USER_ID is set or we use the chat_id from context if available (only works if job is chat-associated).
                # Since we are using a global job, we need a target.
                
                if target_chat_id:
                    try:
                         await context.bot.send_message(chat_id=target_chat_id, text=message, parse_mode='Markdown')
                         database.add_seen_ad(ad_id)
                         new_ads_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send message: {e}")
                else:
                    logger.warning("USER_ID not set. Cannot send notification.")
                    # Still mark as seen? Maybe not.
            
            # Sleep slightly to be polite to OLX
            await asyncio.sleep(2)
            
    logger.info(f"Check complete. {new_ads_count} new ads sent.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id, 
        text=f"👋 Hello! I am your Apartment Hunter.\n\nYour Chat ID is: `{chat_id}`\nCopy this to your `.env` as `USER_ID` if you want to receive proactive alerts."
    )
    logger.info(f"User started bot. Chat ID: {chat_id}")

async def run_check_manually(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """For testing: Trigger a check manually."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🔍 Checking for ads manually...")
    # Trigger the check function. 
    # Note: check_for_ads expects context, and we need to ensure it has valid bot access.
    # We can pass the current context.
    # However, check_for_ads relies on USER_ID for the target.
    await check_for_ads(context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Manual check done.")


if __name__ == '__main__':
    # Initialize DB
    database.init_db()

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_token_HERE":
        print("Error: TELEGRAM_BOT_TOKEN not found or invalid.")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    check_handler = CommandHandler('check', run_check_manually)
    
    application.add_handler(start_handler)
    application.add_handler(check_handler)
    
    # Set up job queue for periodic checks
    if application.job_queue:
        application.job_queue.run_repeating(check_for_ads, interval=CHECK_INTERVAL, first=10)
        logger.info(f"Scheduled status check every {CHECK_INTERVAL} seconds.")
    else:
        logger.error("JobQueue not available.")
    
    print("Bot is running...")
    application.run_polling()

