import os
import json
from pathlib import Path
import random
import logging
import rx
from telegram import Update
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from wit import Wit
from dotenv import load_dotenv
from generative import llm, is_ollama_available, prompts
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



# Assets

photos = list(Path("pics").glob("*"))
audios = list(Path("audio").glob("*"))
quotefile = 'quotes.txt'
audiofile = 'audio.txt'

with open(quotefile) as q:
    qlines = q.readlines()

with open('intents.json', 'r') as f:
    intents = json.load(f)


def remove_parenthesis(text):
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^)]*\]', '', text)
    return text

# Define Command Handlers
def start(update: Update, context: CallbackContext):
    """Handler for /start command"""
    update.message.reply_text('Mo accumminciamm nata vot mo')


def userText(update: Update, context: CallbackContext):
    """Function to reply to user text"""
    ai = Wit(access_token=AI_TOKEN)
    user_message = update.message.text
    resp = ai.message(user_message)
    if resp['intents']:
        print(resp['intents'][0]['name'])
        if resp['intents'][0]['confidence'] > 0.60:
            detected_intent = resp['intents'][0]['name']
            for intent in intents["intents"]:
                if detected_intent == intent["tag"]:

                    if intent["tag"] == "insulto":
                        entity = resp["entities"]["person:object"][0]["body"]
                        print(entity)
                        # update.message.reply_text(f"{entity} {random.choice(intent['responses'])['nap']}")
                        if is_ollama_available():
                            examples = [f"{x['nap']} ({x['it']})" for x in random.sample(intent['responses'], 3)]
                            formatted_prompt = prompts["insulto"].format(
                                message=user_message, 
                                examples="\n".join(examples),
                                entity=entity
                            )
                            print(formatted_prompt)
                            llm_reponse = remove_parenthesis(llm.invoke(formatted_prompt))
                            llm_reponse = llm_reponse.replace("\"", "")
                            llm_reponse = llm_reponse.replace("### RISPOSTA:", "")
                            print(llm_reponse)
                            update.message.reply_text(llm_reponse)

                    elif intent["tag"] == "audio":
                        audio = random.choice(audios)
                        update.message.reply_voice(open(audio, "rb"))

                    elif intent["tag"] == "foto":
                        photo = random.choice(photos) 
                        update.message.reply_photo(open(photo, "rb"), random.choice(qlines))

                    elif intent["tag"] == "parere":
                        if "person:object" in resp["entities"]:
                            entity = resp["entities"]["person:object"][0]["body"]
                            print(entity)
                            update.message.reply_text(f"{entity} {random.choice(intent['responses'])}")
                        else:
                            print("no persona")
                            update.message.reply_text(random.choice(intent['responses']))

                    elif intent["tag"] == "perche":
                        update.message.reply_text(random.choice(intent['responses']))

                    elif intent["tag"] == "saluti_persona":
                        if "person:object" in resp["entities"]:
                            print("persona")
                            entity = resp["entities"]["person:object"][0]["body"]
                            update.message.reply_text(f"{random.choice(intent['responses'])} {entity}")
                        else:
                            print("no persona")
                            update.message.reply_text(random.choice(intent['responses']))

                    else:
                        print(f"using found tag {intent['tag']}")
                        update.message.reply_text(f"{random.choice(intent['responses'])}")

        else:
            print("not enough confidence")
            update.message.reply_text(f"{random.choice(qlines)}")

    else:
        print("no response from witai")
        update.message.reply_text(f"{random.choice(qlines)}")


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

    # starting the bot
    updater.start_polling()
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=TELE_TOKEN,
    #                       webhook_url=HEROKU_URL + TELE_TOKEN)
    # updater.idle()


if __name__ == '__main__':
    main()
