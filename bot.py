
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    welcome_message_mm = (
        f"မင်္ဂလာပါ {user.mention_html()}!\n"  # Myanmar for "Hello"
        "ကျွန်ုပ်သည် သင်၏ AI လက်ထောက်ဖြစ်ပါသည်။\n"  # Myanmar for "I am your AI assistant."
        "မည်သည့်အရာတွင်မဆို ကူညီရန် အသင့်ရှိပါသည်။ /help ကိုနှိပ်၍ ကျွန်ုပ်လုပ်ဆောင်နိုင်သည်များကို ကြည့်ရှုပါ။"
    )  # Myanmar for "I am ready to help with anything. Click /help to see what I can do."
    await update.message.reply_html(welcome_message_mm)

async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Hello! I am PaiClone, your friendly AI assistant.\n\n"
        "I can help you with a variety of tasks, including:\n"
        "- Answering your questions\n"
        "- Providing information\n"
        "- Engaging in general conversation\n\n"
        "You can ask me anything in both English and Myanmar language.\n\n"
        "Just type your message, and I'll do my best to assist you!"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context) -> None:
    """Handle general messages and respond using OpenAI."""
    user_message = update.message.text
    if not user_message:
        return

    logger.info(f"User {update.effective_user.id} said: {user_message}")

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a friendly and helpful AI assistant named PaiClone. You can understand and respond in both English and Myanmar (Burmese) language. Provide concise and helpful answers."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        bot_response = response.choices[0].message.content
        await update.message.reply_text(bot_response)
    except Exception as e:
        logger.error(f"Error communicating with OpenAI: {e}")
        await update.message.reply_text(
            "I apologize, but I'm having trouble connecting to my AI brain right now. Please try again later."
        )

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # On non-command messages - handle with OpenAI
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
