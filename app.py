import os
import logging
from telegram import Update
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from wit import Wit

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

HEROKU_URL = "https://zettibot-witai.herokuapp.com/"
PORT = int(os.environ.get('PORT','8433'))
TELE_TOKEN = "919532199:AAFU7pBcj_L310q3Ud6QkKw2K6KFo9OvaN0"
AI_TOKEN = "Q7EA3FPHULCOYH5DVZU3Y2PY43DKKOXW"


#Define Command Handlers
def start(update: Update, context: CallbackContext):
   """Handler for /start command"""
   update.message.reply_text('Hi, how are you')
def helpCommand(update: Update, context: CallbackContext):
   """Handler for /help command"""
   update.message.reply_text('Help!')
def userText(update: Update, context: CallbackContext):
   """Function to reply to user text"""
   ai = Wit(access_token=AI_TOKEN)
   resp = ai.message(update.message.text)
   update.message.reply_text(str(resp['intents'][0]['name']))


def main():
    """starting bot"""
    updater = Updater(TELE_TOKEN, use_context=True)

    # getting the dispatchers to register handlers
    dp = updater.dispatcher

    # registering commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    # registering Message Handler to reply to user messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, userText))
    # starting the bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TELE_TOKEN,
                          webhook_url=HEROKU_URL + TELE_TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()