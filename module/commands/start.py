from telegram.ext import CommandHandler, CallbackContext, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import logging
import module.shared as shared

async def start(update: Update, context: CallbackContext):
    config = shared.load_config()
    commandKeyboard = [
        [KeyboardButton("/info"), KeyboardButton("/iscriviti")],
        [KeyboardButton("/palinsesto"), KeyboardButton("/prenota")],
        [KeyboardButton("/annullaPrenotazione"), KeyboardButton("/workout")],
        [KeyboardButton("/cancel"), KeyboardButton("/credits")]
    ]
    user = update.effective_user
    #config["ADMINS"] is a dictionary containing the names as keys and the IDs as values
    admin_ids = config["ADMINS"].values()
    if user.id in admin_ids:
        commandKeyboard.insert(0, [KeyboardButton("admin commands ->")])
        reply_markup = ReplyKeyboardMarkup(commandKeyboard, resize_keyboard=True)
        await update.message.reply_text(f"Ciao, {update.effective_user.first_name}!\nSeleziona uno dei comandi per continuare:", reply_markup=reply_markup)
        return "admin_commands"

    reply_markup = ReplyKeyboardMarkup(commandKeyboard, resize_keyboard=True)
    context.user_data["command_message"] = await update.message.reply_text(f"Ciao, {update.effective_user.first_name}!\nSeleziona uno dei comandi per continuare:", reply_markup=reply_markup)
    return ConversationHandler.END

async def admin_commands (update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    commandKeyboard = [
        [KeyboardButton("<- normal commands")],
        [KeyboardButton("/accetta_iscrizione"), KeyboardButton("/rimuovi_iscrizione")],
        [KeyboardButton("/annulla_prenotazione"), KeyboardButton("/aggiungi_workout")],
        [KeyboardButton("/imposta_palinsesto"), KeyboardButton("/messaggio_broadcast")],
        [KeyboardButton("/cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(commandKeyboard, resize_keyboard=True)
    await update.effective_message.delete()
    await context.bot.edit_message_reply_markup(message_id=context.user_data["command_message"].message_id, chat_id=context.user_data["command_message"].chat.id, reply_markup=reply_markup)
    try:
        await context.bot.edit_message_reply_markup(message_id=context.user_data["command_message"].message_id, chat_id=context.user_data["command_message"].chat.id, reply_markup=reply_markup)
    except:
        logging.info("Cannot edit the message, sending a new one.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Comandi amministratore:", reply_markup=reply_markup)
    # await update.message.reply_text(f"Comandi amministratore:", reply_markup=reply_markup)
    return ConversationHandler.END