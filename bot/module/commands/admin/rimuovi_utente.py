from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from module import shared as shared
import pymongo

@shared.entry_point_decorator
async def rimuovi_utente(update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    # Chose between members and waiting list
    keyboard = [[InlineKeyboardButton("Membri", callback_data="members"), InlineKeyboardButton("Lista d'attesa", callback_data="waiting_list")]]
    await update.message.reply_text("Da quale lista vuoi rimuovere l'utente?", reply_markup=InlineKeyboardMarkup(keyboard))
    return "choose_list"

async def choose_list(update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    query = update.callback_query
    effective_list = query.data
    context.user_data["effective_list"] = effective_list
    database = shared.get_db()
    users_list = database[effective_list]
    if users_list.count_documents({}) == 0:
        await query.edit_message_text("Nessun utente in lista.")
        return shared.end_conversation(update, context)
    # Create a message with all the members names and IDs
    message_list = ""
    # for member in users_list.find(): ordered by full_name alphabetically
    for member in users_list.find().sort("full_name", pymongo.ASCENDING):
        message_list += f"*{member['full_name']}* :\t`{member['id']}`\n"

    database.client.close()
    effective_list = effective_list.replace("_", " ")
    await update.callback_query.message.reply_text(f"{effective_list}:\n{message_list}\nInserisci l'ID dell'utente da rimuovere:\n\nPer annullare /cancel", parse_mode="MarkdownV2")
    
    return "get_id"

async def get_id(update: Update, context: CallbackContext):
    database = shared.get_db()
    effective_list = context.user_data["effective_list"]
    users_list = database[effective_list]
    user_id = update.message.text
    
    user = users_list.find_one({"id": user_id})
    database.client.close()
    if not user:
        await update.message.reply_text("ID non valido. Ricomincia -> /rimuovi_utente")
        return shared.end_conversation(update, context)
    
    context.user_data["user_to_remove"] = user
    keyboard = [[InlineKeyboardButton("Si", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]]
    await update.message.reply_text(f"Rimuovere {user['full_name']} ({user['id']})?", reply_markup=InlineKeyboardMarkup(keyboard))

    return "confirm"

 
async def confirm(update: Update, context: CallbackContext):
    query = update.callback_query
    user = context.user_data["user_to_remove"]
    database = shared.get_db()
    users_list = database[context.user_data["effective_list"]]

    if query.data == "yes":
        users_list.delete_one(user)
        await query.edit_message_text(f"{user['full_name']} è stato rimosso.")
    else:
        await query.edit_message_text("Operazione annullata.")

    database.client.close()
    return shared.end_conversation(update, context)