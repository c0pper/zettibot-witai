import datetime
import os
import json
from pathlib import Path
import random
import logging

import requests
import rx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.ext.filters import MessageFilter
from wit import Wit
from dotenv import load_dotenv
import re

load_dotenv()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8433'))
TELE_TOKEN = os.environ.get('TELE_TOKEN')
AI_TOKEN = os.environ.get('AI_TOKEN')


class FilterAwesome(MessageFilter):
    def filter(self, message):
        # return 'python-telegram-bot is awesome' in message.text
        if message.reply_to_message:
            return str(message.reply_to_message.from_user.id) == "672782236"
        else:
            return False
    
filter_awesome = FilterAwesome()


# Assets

photos = list(Path("pics").glob("*"))
audios = list(Path("audio").glob("*"))
quotefile = 'quotes.txt'
audiofile = 'audio.txt'

keyboard = [
    [InlineKeyboardButton("👍 Spaccat", callback_data='feedback_yes'), InlineKeyboardButton("Fo cess", callback_data='feedback_no')]
]
reply_markup = InlineKeyboardMarkup(keyboard)

with open(quotefile) as q:
    qlines = q.readlines()

with open('intents.json', 'r') as f:
    intents = json.load(f)


def reply_with_ollama(update: Update, context: CallbackContext, intent):
    url = f'{os.getenv("OLLAMA_FLASK_SERVICE")}/generate_message'

    try:
        logger.info("\n\tTrying to generate LLM Message...")
        user_message = update.message.text

        response = requests.post(url, json={
                "user_message": user_message,
                "intent": intent
            }
        )
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        llm_response = response.json().get('llm_response')

        if len(llm_response) > 2:
            context.bot.send_message(
                chat_id=update.message.chat_id, 
                text=llm_response,
                reply_to_message_id=update.message.message_id, 
                reply_markup=reply_markup
            )
            logger.info(f"\t\tLLM Message: {llm_response}")
        else:
            logger.info("\t\tLLM message not generated, is Ollama able to find model?")

    except requests.RequestException as e:
        logger.info("\n\nCould not generate LLM message:", e)
        return None


# Define Command Handlers
def start(update: Update, context: CallbackContext):
    """Handler for /start command"""
    update.message.reply_text('Mo accumminciamm nata vot mo')


def userText(update: Update, context: CallbackContext):
    """Function to reply to user text"""

    logger.info (f"\n\n[+] Request from: {update.message.from_user.full_name} - {update.message.from_user.name}\n\n")

    ai = Wit(access_token=AI_TOKEN)
    user_message = update.message.text
    logger.info (f"\tMessage: {user_message}\n\n")

    resp = ai.message(user_message)
    if resp['intents']:
        logger.info(f"\tIntent: {resp['intents'][0]['name']}")
        if resp['intents'][0]['confidence'] > 0.60:
            detected_intent = resp['intents'][0]['name']
            for intent in intents["intents"]:
                if detected_intent == intent["tag"]:

                    if intent["tag"] == "insulto":
                        entity = resp["entities"]["person:object"][0]["body"]
                        logger.info(entity)

                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{entity} {random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])


                    elif intent["tag"] == "saluti_persona":
                        if "person:object" in resp["entities"]:
                            logger.info("persona")
                            entity = resp["entities"]["person:object"][0]["body"]

                            random_sample = random.choice(intent['responses'])['nap']
                            context.bot.send_message(
                                chat_id=update.message.chat_id, 
                                text=f"{entity} {random_sample}", 
                                reply_to_message_id=update.message.message_id, 
                                
                            )

                            reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "saluti":
                            logger.info("no persona")

                            random_sample = random.choice(intent['responses'])['nap']
                            context.bot.send_message(
                                chat_id=update.message.chat_id, 
                                text=f"{random_sample}", 
                                reply_to_message_id=update.message.message_id, 
                                
                            )

                            reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "audio":
                        audio = random.choice(audios)
                        update.message.reply_voice(open(audio, "rb"))

                    elif intent["tag"] == "foto":
                        photo = random.choice(photos) 
                        update.message.reply_photo(open(photo, "rb"), random.choice(qlines))

                    elif intent["tag"] == "parere":
                        random_sample = random.choice(intent['responses'])['nap']
                        if "person:object" in resp["entities"]:
                            entity = resp["entities"]["person:object"][0]["body"]
                            logger.info(entity)
                            answer_text = f"{entity} {random_sample}"

                        else:
                            logger.info("no persona")
                            answer_text = f"{random_sample}"
                        
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=answer_text, 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "perche":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "incazzo":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "ringraziamento":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "accordo":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "neutro":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "social":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "femmine":
                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            
                        )

                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "auguri":
                        random_sample = random.choice(intent['responses'])['nap']
                        if "person:object" in resp["entities"]:
                            entity = resp["entities"]["person:object"][0]["body"]
                            logger.info(entity)
                            answer_text = f"{entity} {random_sample}"

                        else:
                            logger.info("no persona")
                            answer_text = f"{random_sample}"

                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=answer_text, 
                            reply_to_message_id=update.message.message_id, 
                            
                        )
                        
                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    else:
                        logger.info(f"using found tag {intent['tag']}")

                        random_sample = random.choice(intent['responses'])['nap']
                        context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=random_sample, 
                            reply_to_message_id=update.message.message_id, 
                            
                        )
                        
                        reply_with_ollama(update=update, context=context, intent=intent["tag"])

        else:
            logger.info("not enough confidence")
            random_sample = random.choice(intent['responses'])['nap']
            context.bot.send_message(
                chat_id=update.message.chat_id, 
                text=random_sample, 
                reply_to_message_id=update.message.message_id, 
                
            )
            
            reply_with_ollama(update=update, context=context, intent=intent["tag"])
            update.message.reply_text(f"{random.choice(qlines)}")

    else:
        logger.info("no response from witai")
        random_sample = random.choice(qlines)
        context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=random_sample, 
            reply_to_message_id=update.message.message_id, 
            
        )
        
        all_intents = [i["tag"] for i in intents["intents"]]
        random_intent = random.choice(all_intents)
        reply_with_ollama(update=update, context=context, intent=random_intent)


def handle_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    feedback_author_fullname = query.from_user.full_name
    feedback_author_handle = query.from_user.name
    bot_answer = query.message.text
    user_message = query.message.reply_to_message.text
    feedback = {
        "feedback_author_fullname": feedback_author_fullname,
        "feedback_author_handle": feedback_author_handle,
        "bot_answer": bot_answer,
        "user_message": user_message
    }

    current_date = datetime.datetime.now().strftime("%d_%m_%Y")
    processed_handle = re.sub(r'\W+', '', query.from_user.name)
    filename = f"{processed_handle}_{current_date}_{query.data}.json"
    
    if query.data == 'feedback_yes':
        feedback["feedback"] = query.data
        logger.info(f"\t\tFeedback: {query.data}")
        with open(os.path.join("feedback/yes", filename), "w") as file:
            json.dump(feedback, file, indent=4)
    elif query.data == 'feedback_no':
        feedback["feedback"] = query.data
        logger.info(f"\t\tFeedback: {query.data}")
        with open(os.path.join("feedback/no", filename), "w") as file:
            json.dump(feedback, file, indent=4)
    query.edit_message_text(bot_answer + "\n\nGrazie del feedback brother")
    






def send_audio(update: Update, context: CallbackContext) -> None:
    audio = random.choice(audios)
    update.message.reply_voice(open(audio, "rb"))


def send_rand_photo(update: Update, context: CallbackContext) -> None:
    photo = random.choice(photos) #open("pics/xp.jpg", "rb")
    update.message.reply_photo(open(photo, "rb"), random.choice(qlines))


def main():
    """starting bot"""
    updater = Updater(TELE_TOKEN, use_context=True)

    # getting the dispatchers to register handlers
    dp = updater.dispatcher

    # registering commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("audio", send_audio))
    dp.add_handler(CommandHandler("pic", send_rand_photo))
    # registering Message Handler to reply to user messages
    # dp.add_handler(MessageHandler(Filters.text & Filters.regex(rx.trigger_regex) & Filters.regex(rx.audio_regex) & Filters.regex(rx.inviare_regex) & ~Filters.command, send_audio))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(rx.trigger_regex) & ~Filters.command, userText))
    dp.add_handler(CallbackQueryHandler(handle_feedback))
    dp.add_handler(MessageHandler(filter_awesome, userText))
    # dp.add_handler(MessageHandler(Filters.reply, userText))

    # starting the bot
    updater.start_polling()


if __name__ == '__main__':
    main()
