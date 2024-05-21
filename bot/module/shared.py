import yaml
import os
import logging
import pymongo
from telegram import User, Update
from telegram.ext import ConversationHandler
from datetime import datetime
from module.vars import ALWAYS_ALLOWED_COMMANDS

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                # print(f"Error loading YAML file: {exc}")
                logging.getLogger("gym_bot").error(f"Error loading YAML file: {exc}")
    return config

config = load_config()

def get_db():
    HOST = config["MONGO"]["host"]
    PORT = config["MONGO"]["port"]
    USERNAME = config["MONGO"]["username"]
    PASSWORD = config["MONGO"]["password"]
    DB = config["MONGO"]["db"]
    # database = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")[DB]
    database = pymongo.MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}")[DB]
    return database

async def is_allowed(update, context):
    user = update.effective_user
    # if user is an admin return true
    if user.id in config["ADMINS"].values():
        return True
    userDoc = user.to_dict()
    userDoc["id"] = str(userDoc["id"])

    # DB connection
    database = get_db()
    allowed_users = database["members"]
    member = allowed_users.find_one(userDoc)# is not None
    
    if member is None:
        await update.message.reply_text("Non sei ancora un membro. /iscriviti")
        database.client.close()
        return False
    
    # check that the time difference between the "last_payment" field and the current time is less than 30 days
    last_payment = member.get("last_payment")
    if last_payment is None:
        isAllowed = False
        await update.message.reply_text("La quota iscrizione o mensile non è stata pagata. Contatta un coach per effettuare il pagamento. /info")
        logging.getLogger("gym_bot").info("No last payment")
    else:
        elapsed = (datetime.now() - last_payment).days
        logging.getLogger("gym_bot").debug(f"Elapsed days: {elapsed}")
        isAllowed = elapsed < 30
        if not isAllowed:
            await update.message.reply_text("Il tuo abbonamento è scaduto. L'ultimo pagamento è stato effettuato il " + last_payment.strftime("%d/%m/%Y") + ". Contatta un coach per rinnovarlo. /info")
    
    database.client.close()
    return isAllowed

def get_res(name: str):
     #Read the respective resource file
    resource_path = os.path.join(os.path.dirname(__file__), f'../res/{name}.txt')
    try:
        with open(resource_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.getLogger("gym_bot").error(f"Resource file {name}.txt not found")
        return None
    
async def is_in_conversation(update, context):
    if context.user_data.get("in_conversation"):
        await update.message.reply_text("Completa o termina (/cancel) la conversazione corrente prima di iniziarne una nuova.")
        return True
    return False

# This decorator ensures that the command is not called while in a conversation
def command_decorator(func):
    async def wrapper(update: Update, context):
        user: User = update.effective_user
        message = update.effective_message
        logging.getLogger("gym_bot").debug(f"Conversation status: {context.user_data.get('in_conversation')}")
        logging.getLogger("gym_bot").info(f"Command {message.text} called by {user.full_name} ({user.id})")
        if update.effective_message.text not in ALWAYS_ALLOWED_COMMANDS:
            if not await is_allowed(update, context):
                return end_conversation(update, context)
        if await is_in_conversation(update, context):
            return end_conversation(update, context)
        return await func(update, context)
    return wrapper

# This decorator sets the user_data["in_conversation"] flag to True before calling the function, so that any other command decorated with command_decorator will not be called
# every entry point is also a command, so it is decorated with command_decorator

def entry_point_decorator(func):
    @command_decorator
    async def wrapper(update, context):
        context.user_data["in_conversation"] = True
        logging.getLogger("gym_bot").debug(f"Conversation started, in_conversation set to {context.user_data['in_conversation']}")
        return await func(update, context)
    return wrapper

# def exit_point_decorator(func):
#     async def wrapper(update, context):
#         context.user_data["in_conversation"] = False
#         return await func(update, context)
#     return wrapper

def end_conversation(update, context):
    context.user_data["in_conversation"] = False
    logging.getLogger("gym_bot").debug(f"Conversation ended, in_conversation set to {context.user_data['in_conversation']}")
    return ConversationHandler.END