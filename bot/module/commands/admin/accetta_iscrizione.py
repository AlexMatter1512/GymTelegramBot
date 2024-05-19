from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from module import shared as shared
import pymongo
import logging
config = shared.config

@shared.entry_point_decorator
async def accetta_iscrizione(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id not in config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    database = shared.get_db()
    waiting_list = database["waiting_list"]

    if waiting_list.count_documents({}) == 0:
        await update.message.reply_text("Nessun utente in lista d'attesa.")
        return shared.end_conversation(update, context)
    
    users = waiting_list.find()

    usersKeyboard = []
    for user in users:
        usersKeyboard.append([InlineKeyboardButton(f"{user['full_name']} {user['id']}", callback_data=user['id'])])

    usersKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
    reply_markup = InlineKeyboardMarkup(usersKeyboard)
    await update.message.reply_text("Seleziona l'utente da accettare:", reply_markup=reply_markup)

    database.client.close()
    return "user_selected"

 
async def user_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.data
    logging.getLogger("gym_bot").info(f"User {user_id} is being added to the members.")

    database = shared.get_db()
    waiting_list = database["waiting_list"]
    members = database["members"]
    user = waiting_list.find_one({"id": user_id})
    if user is None:
        await query.message.reply_text("Utente non trovato.")
        return shared.end_conversation(update, context)
    
    members.insert_one(user)
    waiting_list.delete_one(user)

    await context.bot.send_message(chat_id=user_id, text="🥳 Congratulazioni 🎉, sei stato accettato come membro. Adesso puoi usare tutti i comandi!\n/start")

    database.client.close()
    await query.edit_message_text(f"{user['full_name']} è stato aggiunto ai membri.")

    return shared.end_conversation(update, context)
    