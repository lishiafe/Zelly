import logging
import praw
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from decouple import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = config("TOKEN")

# Reddit Configuration
SUBREDDIT_NAME = "askreddit"  # Default subreddit to check
POST_LIMIT = 10             # Number of recent posts to fetch

# --- Reddit Setup ---
reddit = praw.Reddit(
    client_id="SdlhaOk-J5V1tNebwbIj-g",
    client_secret="9aTFhYB2qjLK4kcz0u-_I6dKnRvtYQ",
    user_agent="my_reddit_bot by u/ZealousidealStill451"
)

# --- Function to get recent Reddit posts ---
def get_recent_posts(subreddit_name=SUBREDDIT_NAME, limit=POST_LIMIT):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.new(limit=limit):
        safe_title = post.title.replace("*", "").replace("_", "")
        posts.append({
            "title": safe_title,
            "url": post.url,
            "created": post.created_utc
        })
    return posts

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /check command"""
    if update.message.chat.type in ['group', 'supergroup', 'private']:  # Include private
        try:
            # Get recent Reddit posts
            posts = get_recent_posts()

            # Send the checked confirmation
            user = update.message.from_user
            user_mention = f"@{user.username}" if user.username else user.first_name
            await update.message.reply_text(f"✅ {user_mention} checked\n\n📰 Showing {len(posts)} recent posts from r/{SUBREDDIT_NAME}:")

            for post in posts:
                message_text = f"🆕 {post['title']}\n🔗 {post['url']}"
                await update.message.reply_text(message_text, disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"Error in check_command: {e}")
            await update.message.reply_text("⚠️ Sorry, I couldn't fetch Reddit posts at the moment.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for all messages that start with /check but aren't commands"""
    if update.message.text and update.message.text.startswith('/check'):
        if update.message.chat.type in ['group', 'supergroup', 'private']:  # Include private
            try:
                posts = get_recent_posts()

                user = update.message.from_user
                user_mention = f"@{user.username}" if user.username else user.first_name
                await update.message.reply_text(f"✅ {user_mention} checked\n\n📰 Showing {len(posts)} recent posts from r/{SUBREDDIT_NAME}:")

                for post in posts:
                    message_text = f"🆕 {post['title']}\n🔗 {post['url']}"
                    await update.message.reply_text(message_text, disable_web_page_preview=True)

            except Exception as e:
                logger.error(f"Error in handle_message: {e}")
                await update.message.reply_text("⚠️ Sorry, I couldn't fetch Reddit posts at the moment.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until you press Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as err:
        print("stopped by user")
