from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import logging
from module import shared

@shared.entry_point_decorator
async def gestisci_corsi(update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    # Ask if the user wants to add a course or remove one
    keyboard = [[InlineKeyboardButton("Aggiungi corso", callback_data="add_course")], [InlineKeyboardButton("Rimuovi corso", callback_data="remove_course")]]
    await update.message.reply_text("Cosa vuoi fare?", reply_markup=InlineKeyboardMarkup(keyboard))
    return "ask_course_name"

async def ask_course_name(update: Update, context: CallbackContext):
    context.user_data["action"] = update.callback_query.data
    logging.getLogger("gym_bot").info(f"Action: {context.user_data['action']}")
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.callback_query.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    await update.callback_query.message.reply_text("Inserisci il nome del corso:")
    return "get_course_name"

async def get_course_name(update: Update, context: CallbackContext):
    course_name = update.message.text # change to all uppercase
    course_name = course_name.upper()
    context.user_data["course_name"] = course_name

    confirmKeyboard = [[InlineKeyboardButton("Conferma", callback_data="confirm"), InlineKeyboardButton("Annulla", callback_data="cancel")]]
    await update.message.reply_text(f"Hai inserito il nome del corso: {course_name}. Sei sicuro di volerlo aggiungere?", reply_markup=InlineKeyboardMarkup(confirmKeyboard))

    return "confirm_course_name"

async def confirm_course_name(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "confirm":
        if context.user_data["action"] == "add_course":
            return await add_course(update, context)
        elif context.user_data["action"] == "remove_course":
            return await remove_course(update, context)

    await query.edit_message_text("Operazione annullata.")

async def add_course(update: Update, context: CallbackContext):
    course_name = context.user_data["course_name"]
    database = shared.get_db()
    if database["corsi"].count_documents({"nome": course_name}) > 0:
        await update.callback_query.edit_message_text("Il corso è già presente.")
        return shared.end_conversation(update, context)
    
    corso = {"nome": course_name}
    database["corsi"].insert_one(corso)

    await update.callback_query.edit_message_text(f"Il corso {course_name} è stato aggiunto.")
    database.client.close()

    return shared.end_conversation(update, context)

 
async def remove_course(update: Update, context: CallbackContext):
    course_name = context.user_data["course_name"]
    database = shared.get_db()
    if database["corsi"].count_documents({"nome": course_name}) == 0:
        await update.callback_query.edit_message_text("Il corso non è presente.")
        return shared.end_conversation(update, context)
    
    database["corsi"].delete_many({"nome": course_name})
    database["palinsesto"].delete_many({"corso": course_name})

    await update.callback_query.edit_message_text(f"Il corso {course_name} è stato rimosso.")
    database.client.close()

    return shared.end_conversation(update, context)
    
