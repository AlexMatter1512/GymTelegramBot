from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import pymongo
from module import shared as shared
import logging
config = shared.config

async def iscriviti(update: Update, context: CallbackContext):
    database = shared.get_db()
    members = database["members"]
    waiting_list = database["waiting_list"]
    userDict = (update.effective_user).to_dict()
    userDict["id"] = str(userDict["id"])

    # check if the user is already subscribed or in the waiting list
    waiting = waiting_list.find_one({"id": userDict["id"]})
    subscribed = members.find_one({"id": userDict["id"]})
    if subscribed is not None:
        logging.info(f"User {userDict['id']} is already subscribed")
        await update.message.reply_text("Sei già iscritto!")
        return ConversationHandler.END
    if waiting is not None:
        logging.info(f"User {userDict['id']} is already in the waiting list")
        await update.message.reply_text("Sei già in lista d'attesa!")
        return ConversationHandler.END
    
    # Ask the user for the name and surname she wants to be identified with by the gym owner
    await update.message.reply_text("Inserisci il tuo nome e cognome (es. Mario Rossi):")
    database.client.close()
    return "insert_user"

async def insert_user(update: Update, context: CallbackContext):
    fullName = update.message.text
    database = shared.get_db()
    waiting_list = database["waiting_list"]
    userDict = (update.effective_user).to_dict()
    userDict["id"] = str(userDict["id"])
    if waiting_list.find_one({"id": userDict["id"]}) is not None:
        logging.info(f"User {userDict['id']} is already in the waiting list")
        await update.message.reply_text("Sei già in lista d'attesa!")
        return ConversationHandler.END
    userDict["full_name"] = fullName
    waiting_list.insert_one(userDict)
    logging.info(f"User {userDict['id']} {userDict['username']} added to the waiting list")
    database.client.close()

    await update.message.reply_text(f"Ti sei iscritto alla lista d'attesa con il nome: {fullName}, riceverai un messaggio quando sarai stato aggiunto ai membri!")
    for admin in config["ADMINS"].values():
        await context.bot.send_message(chat_id=admin, text=f"Nuova richiesta di iscrizione da:\n{fullName} ({userDict['username']} {userDict['id']})")
    return ConversationHandler.END