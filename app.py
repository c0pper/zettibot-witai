import datetime
import os
import json
from pathlib import Path
import random
import logging

import requests
import rx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, Defaults
from telegram.ext.filters import MessageFilter
from wit import Wit
from dotenv import load_dotenv
import re

load_dotenv()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

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

def build_feedback_reply_markup(intent):
    cb_data_yes = json.dumps({'fb': 'feedback_yes', 'intent': f'{intent}'})
    cb_data_no = json.dumps({"fb": "feedback_no", "intent": f"{intent}"})
    keyboard = [
        [
            InlineKeyboardButton("👍 Spaccat", callback_data=cb_data_yes),
            InlineKeyboardButton("👎 Fo cess", callback_data=cb_data_no)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

with open(quotefile) as q:
    qlines = q.readlines()

with open('intents.json', 'r') as f:
    intents = json.load(f)


async def reply_with_ollama(update: Update, context: CallbackContext, intent):
    url = f'{os.getenv("OLLAMA_FLASK_SERVICE")}/generate_message'

    try:
        logger.info("\tTrying to generate LLM Message...")
        user_message = update.message.text

        response = requests.post(url, json={
                "user_message": user_message,
                "intent": intent
            }
        )
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        llm_response = response.json().get('llm_response')
        llm_samples = response.json().get('examples')
        llm_response = llm_response + "\n\n_Funzione sperimentale_"
        llm_response = llm_response.replace("!", "\!").replace(".", "\.")

        markup_kb = build_feedback_reply_markup(intent)
        if len(llm_response) > 2:
            await context.bot.send_message(
                chat_id=update.message.chat_id, 
                text=llm_response,
                reply_to_message_id=update.message.message_id, 
                reply_markup=markup_kb,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info(f"\t\tLLM Samples: \n{llm_samples}")
            logger.info(f"\t\tLLM Message: {llm_response}")
        else:
            logger.info("\t\tLLM message not generated, is Ollama able to find model?")

    except requests.RequestException as e:
        logger.error("\tCould not generate LLM message: probably zettibot-llmservice offline.")
        return None


# Define Command Handlers
async def start(update: Update, context: CallbackContext):
    """Handler for /start command"""
    await update.message.reply_text('Mo accumminciamm nata vot mo', parse_mode=ParseMode())


async def userText(update: Update, context: CallbackContext):
    """Function to reply to user text"""
    logger.info (f"[+] Request from: {update.message.from_user.full_name} - {update.message.from_user.name}")

    ai = Wit(access_token=AI_TOKEN)
    user_message = update.message.text
    logger.info (f"\tMessage: {user_message}")

    resp = ai.message(user_message)
    if resp['intents']:
        logger.info(f"\tIntent: {resp['intents'][0]['name']}")
        detected_intent = resp['intents'][0]['name']
        markup_kb = build_feedback_reply_markup(detected_intent)
        if resp['intents'][0]['confidence'] > 0.50:
            random_sample = ""
            for intent in intents["intents"]:
                if detected_intent == intent["tag"]:
                    
                    context.user_data["intent"] = intent["tag"]

                    if intent["tag"] == "insulto":
                        entity = resp["entities"]["person:object"][0]["body"]
                        logger.info(entity)

                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{entity} {random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])


                    elif intent["tag"] == "saluti_persona":
                        if "person:object" in resp["entities"]:
                            logger.info("persona")
                            entity = resp["entities"]["person:object"][0]["body"]

                            random_sample = random.choice(intent['responses'])['nap']
                            await context.bot.send_message(
                                chat_id=update.message.chat_id, 
                                text=f"{entity} {random_sample}", 
                                reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                                
                            )

                            # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "saluti":
                        logger.info(f"\tNo entity in message for intent {detected_intent}")

                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "audio":
                        audio = random.choice(audios)
                        await update.message.reply_voice(open(audio, "rb"))

                    elif intent["tag"] == "foto":
                        photo = random.choice(photos) 
                        await update.message.reply_photo(open(photo, "rb"), random.choice(qlines))

                    elif intent["tag"] == "parere":
                        random_sample = random.choice(intent['responses'])['nap']
                        if "person:object" in resp["entities"]:
                            entity = resp["entities"]["person:object"][0]["body"]
                            logger.info(entity)
                            answer_text = f"{entity} {random_sample}"
                            

                        else:
                            logger.info("no persona")
                            answer_text = f"{random_sample}"
                        
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=answer_text, 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "perche":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "incazzo":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "ringraziamento":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "accordo":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "neutro":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "social":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "femmine":
                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=f"{random_sample}", 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )

                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    elif intent["tag"] == "auguri":
                        random_sample = random.choice(intent['responses'])['nap']
                        if "person:object" in resp["entities"]:
                            entity = resp["entities"]["person:object"][0]["body"]
                            logger.info(entity)
                            answer_text = f"{entity} {random_sample}"

                        else:
                            logger.info("no persona")
                            answer_text = f"{random_sample}"
                            
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=answer_text, 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2
                            
                        )
                        
                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

                    else:
                        logger.info(f"using found tag {intent['tag']}")

                        random_sample = random.choice(intent['responses'])['nap']
                        await context.bot.send_message(
                            chat_id=update.message.chat_id, 
                            text=random_sample, 
                            reply_to_message_id=update.message.message_id, 
                            reply_markup=markup_kb,
                            parse_mode=ParseMode.MARKDOWN_V2 
                            
                        )
                        
                        # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

        else:
            logger.info("not enough confidence")
            intent = [i for i in intents["intents"] if i["tag"] == detected_intent][0]
            random_sample = random.choice([i['responses'] for i in intents["intents"] if i["tag"] == detected_intent][0])["nap"]
            await context.bot.send_message(
                chat_id=update.message.chat_id, 
                text=random_sample, 
                reply_to_message_id=update.message.message_id, 
                reply_markup=markup_kb,
                parse_mode=ParseMode.MARKDOWN_V2 
                
            )
            
            # await reply_with_ollama(update=update, context=context, intent=intent["tag"])

    else:
        logger.info("no response from witai")
        all_intents = [i["tag"] for i in intents["intents"] if i["tag"] not in ["parere", "insulto", "saluti_persona", "auguri"]]
        random_intent = random.choice(all_intents)
        random_sample = random.choice(qlines)
        markup_kb = build_feedback_reply_markup(random_intent)
        await context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=random_sample, 
            reply_to_message_id=update.message.message_id, 
            reply_markup=markup_kb,
            parse_mode=ParseMode.MARKDOWN_V2 
            
        )
        
        await reply_with_ollama(update=update, context=context, intent=random_intent)

    context.user_data["entities"] = resp.get("entities")
    logger.info(f"\tPredefined answer: {random_sample}")


async def handle_feedback(update: Update, context: CallbackContext):
    query = update.callback_query
    feedback_author_fullname = query.from_user.full_name
    feedback_author_handle = query.from_user.name
    bot_answer = query.message.text
    funzione_idx = bot_answer.find("\n\nFunzione")
    bot_answer = bot_answer[:bot_answer.find("\n\nFunzione")] if funzione_idx > 0 else bot_answer
    processed_bot_answer = bot_answer.replace("!", "\!").replace(".", "\.")
    user_message = query.message.reply_to_message.text
    query_feedback = json.loads(query.data)
    feedback = {
        "feedback_author_fullname": feedback_author_fullname,
        "feedback_author_handle": feedback_author_handle,
        "bot_answer": bot_answer,
        "intent": query_feedback["intent"],
        "user_message": user_message,
        "eval": query_feedback["fb"]
    }

    feedback_folder = "/feedback"
    if not os.path.exists(feedback_folder):
        feedback_folder = "feedback"

    current_date = datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")

    processed_handle = re.sub(r'\W+', '', query.from_user.name)
    filename = f"{processed_handle}_{current_date}_{query_feedback['fb']}.json"
    filename_yes = os.path.join(feedback_folder, "yes", filename)
    filename_no = os.path.join(feedback_folder, "no", filename)

    fn = "" #"\n\n_Funzione sperimentale_"

    if query_feedback["fb"] == 'feedback_yes':
        logger.info(f"\t\tFeedback: {query_feedback['fb']}")
        with open(filename_yes, "w", encoding="utf8") as file:
            json.dump(feedback, file, indent=4)
        
        if context.user_data["entities"]:
            if "person:object" in list(context.user_data["entities"].keys()):
                ent_entity = context.user_data['entities']['person:object'][0]["name"] + ":" + context.user_data['entities']['person:object'][0]["role"]
                ent_start = context.user_data['entities']['person:object'][0]["start"]
                ent_end = context.user_data['entities']['person:object'][0]["end"]
                ent_body = context.user_data['entities']['person:object'][0]["body"]
                entities = [{
                    "entity": ent_entity,
                    "start": ent_start,
                    "end": ent_end,
                    "body": ent_body,
                    "entities": []
                }]
            else:
                entities = []
        else:
            entities = []

        body = [{
            "text": user_message,
            "intent": context.user_data["intent"],
            "entities": entities,
            "traits": []
        }]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('WITAI_SERVER_TOKEN')}"
        }
        train_url = "https://api.wit.ai/utterances"
        response = requests.post(train_url, headers=headers, data=json.dumps(body))
        await query.edit_message_text(processed_bot_answer + fn + "\n\n_Grazie brother quando vieni al bar mary stai pavat_", parse_mode=ParseMode.MARKDOWN_V2)
    elif query.data == 'feedback_no':
        feedback["feedback"] = query.data
        logger.info(f"\t\tFeedback: {query.data}")
        with open(filename_no, "w", encoding="utf8") as file:
            json.dump(feedback, file, indent=4)
        await query.edit_message_text(processed_bot_answer + fn + "\n\n_Azz no ma m fa piacer_", parse_mode=ParseMode.MARKDOWN_V2)
    



async def send_audio(update: Update, context: CallbackContext) -> None:
    audio = random.choice(audios)
    await update.message.reply_voice(open(audio, "rb"))


async def send_rand_photo(update: Update, context: CallbackContext) -> None:
    photo = random.choice(photos) #open("pics/xp.jpg", "rb")
    await update.message.reply_photo(open(photo, "rb"), random.choice(qlines))


def main():
    """starting bot"""
    app = ApplicationBuilder().token(TELE_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", send_audio))
    app.add_handler(CommandHandler("pic", send_rand_photo))
    app.add_handler(MessageHandler(filters.TEXT & (filters.Regex(rx.trigger_regex) | filter_awesome) & ~filters.COMMAND, userText))
    app.add_handler(CallbackQueryHandler(handle_feedback))

    app.run_polling()


    # updater = Updater(TELE_TOKEN, use_context=True)

    # # getting the dispatchers to register handlers
    # dp = updater.dispatcher

    # # registering commands
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("audio", send_audio))
    # dp.add_handler(CommandHandler("pic", send_rand_photo))
    # # registering Message Handler to reply to user messages
    # # dp.add_handler(MessageHandler(Filters.text & Filters.regex(rx.trigger_regex) & ~Filters.command, userText))
    # dp.add_handler(MessageHandler(Filters.text & (Filters.regex(rx.trigger_regex) | filter_awesome) & ~Filters.command, userText))
    # # dp.add_handler(MessageHandler(filter_awesome, userText))
    # dp.add_handler(CallbackQueryHandler(handle_feedback))


    # # starting the bot
    # updater.start_polling()


if __name__ == '__main__':
    main()
