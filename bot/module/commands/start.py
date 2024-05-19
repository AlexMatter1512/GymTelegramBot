from telegram.ext import CommandHandler, CallbackContext, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import logging
import module.shared as shared

async def start(update: Update, context: CallbackContext):
    config = shared.load_config()
    database = shared.get_db()
    user = update.effective_user
    await update.effective_message.delete()
    logging.getLogger("gym_bot").info(f"user {user.id} has called start command")

    # if user is a gym member or an admin, show all commands
    if (database["members"].count_documents({"id": f"{user.id}"}) > 0) or (user.id in config["ADMINS"].values()):
        commandKeyboard = [
            [KeyboardButton("/info"), KeyboardButton("/palinsesto")],
            [KeyboardButton("/prenota"), KeyboardButton("/annullaPrenotazione")],
            [KeyboardButton("/workout"), KeyboardButton("/credits")],
            [KeyboardButton("/cancel")]
        ]
    else:
        commandKeyboard = [
        [KeyboardButton("/info")],
        [KeyboardButton("/iscriviti")]
    ]

    # if user is an admin, add admin commands button
    if user.id in config["ADMINS"].values():
        commandKeyboard.insert(0, [KeyboardButton("admin commands ->")])

    reply_markup = ReplyKeyboardMarkup(commandKeyboard, resize_keyboard=True)

    # if there is a message_id in user_data, delete the message
    last_message_id = context.user_data.get("message_id")
    if last_message_id:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_message_id)
    
    sentMessage = await update.message.reply_text(f"Ciao, {update.effective_user.first_name}!\nSeleziona uno dei comandi per continuare:", reply_markup=reply_markup)
    context.user_data["message_id"] = sentMessage.message_id
    return

async def admin_commands (update: Update, context: CallbackContext):
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    commandKeyboard = [
        [KeyboardButton("<- normal commands")],
        [KeyboardButton("/accetta_iscrizione"), KeyboardButton("/rimuovi_utente")],
        [KeyboardButton("/annulla_prenotazione"), KeyboardButton("/aggiungi_workout")],
        [KeyboardButton("/imposta_palinsesto"), KeyboardButton("/messaggio_broadcast")],
        [KeyboardButton("/gestisci_corsi")],#, KeyboardButton("/rimuovi_corso")],
        [KeyboardButton("/cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(commandKeyboard, resize_keyboard=True)
    await update.effective_message.delete()

    last_message_id = context.user_data.get("message_id")
    if last_message_id:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_message_id)

    sentMessage = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Comandi amministratore:", reply_markup=reply_markup)
    context.user_data["message_id"] = sentMessage.message_id

    return