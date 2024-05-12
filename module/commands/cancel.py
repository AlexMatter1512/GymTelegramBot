from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import logging

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(f"User {update.effective_user.first_name} canceled the operation")
    # reply a random message from the list BAD_ANSWERS
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Operazione annullata."
    )
    return ConversationHandler.END

async def cancelQuery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await cancel(update, context)
    return ConversationHandler.END