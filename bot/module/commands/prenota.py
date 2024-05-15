from telegram.ext import CommandHandler, CallbackContext, ConversationHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from module import shared as shared
import pymongo

config = shared.config

async def prenota(update: Update, context: CallbackContext):
    if not shared.is_allowed(update.effective_user):
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    user = (update.effective_user).to_dict()

    
