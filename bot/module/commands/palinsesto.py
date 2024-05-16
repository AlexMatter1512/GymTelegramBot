from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from module import shared
from module.vars import WEEKDAYS
import logging

async def selezionaCorso(update: Update, context: CallbackContext): #Entry point
    context.user_data["in_conversation"] = True

    logging.info(f"user {update.effective_user.id} has called palinsesto command")
    database = shared.get_db()
    corsi = database["corsi"]
    cursor = corsi.find({})
    corsiKeyboard = []
    for corso in cursor:
        corsiKeyboard.append([InlineKeyboardButton(corso["nome"], callback_data=f"{corso['nome']}")])
    corsiKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
    keyboard = InlineKeyboardMarkup(corsiKeyboard)
    mainMessage = await update.message.reply_text("Seleziona un corso:", reply_markup=keyboard)
    context.user_data["mainMessageId"] = mainMessage.message_id
    database.client.close()
    return "selezionaGiorno"

async def selezionaGiorno(update: Update, context: CallbackContext):
    context.user_data["corso"] = update.callback_query.data
    logging.info(f"Corso selezionato: {context.user_data['corso']}")
    await update.callback_query.edit_message_text(context.user_data['corso'])
    # await context.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=context.user_data.get("mainMessageId"), text=context.user_data["corso"])
    giorniKeyboard = []
    for giorno in WEEKDAYS["ita"]:
        giorniKeyboard.append([InlineKeyboardButton(giorno, callback_data=f"{giorno}")])
    giorniKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
    keyboard = InlineKeyboardMarkup(giorniKeyboard)
    await update.callback_query.message.reply_text("Seleziona un giorno:", reply_markup=keyboard)
    return "sendPalinsesto"

async def sendPalinsesto(update: Update, context: CallbackContext):
    context.user_data["giorno"] = update.callback_query.data
    logging.info(f"Giorno selezionato: {context.user_data['giorno']}")
    # await update.callback_query.edit_message_text(f"Hai selezionato il giorno {context.user_data['giorno']}.")
    await context.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=context.user_data.get("mainMessageId"), text=f"{context.user_data['corso']} - {context.user_data['giorno']}")
    await update.callback_query.message.delete()
    database = shared.get_db()
    palinsesto = database["palinsesto"]
    if palinsesto.count_documents({"corso": context.user_data["corso"], "day": context.user_data["giorno"]}) == 0:
        await update.callback_query.message.reply_text("Nessuna lezione disponibile. Prova con un altro giorno o un altro corso.")

        context.user_data["in_conversation"] = False
        return ConversationHandler.END
    
    cursor = palinsesto.find({"corso": context.user_data["corso"], "day": context.user_data["giorno"]})
    palinsestoText = ""
    for doc in cursor:
        # logging.info(doc)
        palinsestoText += f"{doc['start_hour']}:{doc['start_minute']} - {doc['end_hour']}:{doc['end_minute']}\n"
    await update.callback_query.message.reply_text(palinsestoText)
    database.client.close()

    context.user_data["in_conversation"] = False
    return ConversationHandler.END
