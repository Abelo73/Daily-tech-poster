import os
import random
import feedparser
from telegram import Bot
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_poster.log'),  # Save logs to a file
        logging.StreamHandler()  # Also print logs to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Log environment variables (avoid logging sensitive data in production)
logger.info("Starting daily_poster.py")
logger.info(f"TELEGRAM_TOKEN loaded: {'Yes' if TELEGRAM_TOKEN else 'No'}")
logger.info(f"CHANNEL_ID loaded: {CHANNEL_ID if CHANNEL_ID else 'Not set'}")

# Check if environment variables are set
if not TELEGRAM_TOKEN or not CHANNEL_ID:
    logger.error("Missing TELEGRAM_TOKEN or CHANNEL_ID. Exiting.")
    raise ValueError("TELEGRAM_TOKEN or CHANNEL_ID not set in environment variables")

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://techcrunch.com/feed/"
]

def get_latest_article():
    feed_url = random.choice(RSS_FEEDS)
    logger.info(f"Fetching article from RSS feed: {feed_url}")
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        logger.warning("No entries found in the RSS feed.")
        return None
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    summary = entry.get("summary", "")
    logger.info(f"Selected article: {title}")
    return f"📰 *{title}*\n\n{summary[:400]}...\n\n🔗 Read more: {link}"

def post_to_telegram():
    try:
        logger.info("Initializing Telegram bot")
        bot = Bot(token=TELEGRAM_TOKEN)
        message = get_latest_article()
        if not message:
            message = "No news found today."
            logger.info("No article found, using default message")
        logger.info(f"Sending message to chat ID {CHANNEL_ID}: {message[:100]}...")  # Log first 100 chars
        bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        logger.info("Message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        post_to_telegram()
    except Exception as e:
        logger.critical(f"Script failed: {str(e)}", exc_info=True)