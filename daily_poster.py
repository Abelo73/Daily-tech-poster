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
        logging.FileHandler('daily_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")

# Validate environment variables
if not TELEGRAM_TOKEN or not CHANNEL_ID or not GROUP_ID:
    logger.error("Missing TELEGRAM_TOKEN, CHANNEL_ID, or GROUP_ID. Exiting.")
    raise ValueError("Required environment variables not set")

logger.info("Starting daily_poster.py")
logger.info(f"TELEGRAM_TOKEN loaded: {'Yes' if TELEGRAM_TOKEN else 'No'}")
logger.info(f"CHANNEL_ID loaded: {CHANNEL_ID}")
logger.info(f"GROUP_ID loaded: {GROUP_ID}")

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

def post_to_telegram(chat_id, destination_name):
    try:
        logger.info(f"Initializing Telegram bot for {destination_name}")
        bot = Bot(token=TELEGRAM_TOKEN)
        message = get_latest_article()
        if not message:
            message = "No news found today."
            logger.info("No article found, using default message")
        logger.info(f"Sending message to {destination_name} ({chat_id}): {message[:100]}...")
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        logger.info(f"Message sent successfully to {destination_name}")
    except Exception as e:
        logger.error(f"Failed to send to {destination_name}: {str(e)}", exc_info=True)
        raise

def post_to_all():
    destinations = [
        (CHANNEL_ID, "Channel"),
        (GROUP_ID, "Group")
    ]
    for chat_id, name in destinations:
        post_to_telegram(chat_id, name)

if __name__ == "__main__":
    try:
        post_to_all()
    except Exception as e:
        logger.critical(f"Script failed: {str(e)}", exc_info=True)