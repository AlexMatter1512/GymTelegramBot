from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import logging
from module import shared

async def aggiungi_corso(update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    await update.message.reply_text("Inserisci il nome del corso:")
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
        course_name = context.user_data["course_name"]
        database = shared.get_db()
        if database["corsi"].count_documents({"nome": course_name}) > 0:
            await query.edit_message_text("Il corso è già presente.")
            return ConversationHandler.END
        
        corso = {"nome": course_name}
        database["corsi"].insert_one(corso)

        await query.edit_message_text(f"Il corso {course_name} è stato aggiunto.")
        database.client.close()

    return ConversationHandler.END
    
