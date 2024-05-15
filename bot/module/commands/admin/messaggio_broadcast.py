from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from module import shared as shared

async def messaggio_broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    await update.message.reply_text("Inserisci il messaggio da inviare:")
    return "get_message"

async def get_message(update: Update, context: CallbackContext):
    message = update.message.text
    database = shared.get_db()
    members = database["members"]
    for member in members.find():
        await context.bot.send_message(chat_id=member["id"], text=message)
    database.client.close()
    await update.message.reply_text("Messaggio inviato!")

    return ConversationHandler.END