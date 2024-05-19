from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import random
from module import shared
import logging

@shared.command_decorator
async def info(update: Update, context: CallbackContext):
    # if await shared.is_in_conversation(update, context):
    #     return
    
    picsFile = shared.get_res("community_pics") 
    if picsFile is not None:
        logging.getLogger("gym_bot").info("Sending random picture from community_pics")
        # every line in the resource file is a URL, send a random one
        pics = picsFile.split("\n")
        try:
            await update.message.reply_photo(photo=random.choice(pics))
        except Exception as e:
            logging.getLogger("gym_bot").error(f"Error sending photo: {e}")
         
    infoMsgFile = shared.get_res("info_text")
    if infoMsgFile is not None:
        await update.message.reply_text(infoMsgFile, "Markdown")
    else:
        logging.getLogger("gym_bot").error("Error loading info message resource file")
        await update.message.reply_text("This is our gym official bot!")