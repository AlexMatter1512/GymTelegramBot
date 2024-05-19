from telegram.ext import CommandHandler, CallbackContext, ConversationHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from module import shared as shared
from module.vars import WEEKDAYS
from module.commands import palinsesto
import pymongo
from bson.objectid import ObjectId
import logging
import datetime

config = shared.config

# @shared.command_decorator is not needed here because palinsesto.selezionaCorso already has it
async def prenota(update: Update, context: CallbackContext):
    if shared.is_allowed(update.effective_user):
        return await palinsesto.selezionaCorso(update, context) # -> "selezionaGiorno"
    await update.message.reply_text("Non sei autorizzato ad eseguire questo comando.")
    return shared.end_conversation(update, context)

async def choose_day(update: Update, context: CallbackContext):
    context.user_data["corso"] = update.callback_query.data
    # Choose today or tomorrow
    keyboard = [
        [InlineKeyboardButton("Oggi", callback_data="today"), InlineKeyboardButton("Domani", callback_data="tomorrow")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Scegli il giorno per cui prenotare:", reply_markup=reply_markup)
    return "choose_class"

async def choose_class(update: Update, context: CallbackContext):
    choice = update.callback_query.data
    if choice == "today":
        day = datetime.datetime.now().date()
    elif choice == "tomorrow":
        day = datetime.datetime.now().date() + datetime.timedelta(days=1)
    else:
        return await update.callback_query.message.reply_text("Errore nella scelta del giorno.")
    
    

    # convert day to weekday name in Italian
    weekday = day.strftime("%A").capitalize()
    index = WEEKDAYS["eng"].index(weekday)
    weekday = WEEKDAYS["ita"][index]
    logging.getLogger("gym_bot").debug(f"weekday: {weekday}")

    day = day.strftime("%d/%m/%Y")
    context.user_data["day"] = day

    database = shared.get_db()
    palinsesto = database["palinsesto"]
    prenotazioni = database["prenotazioni"]

    if palinsesto.count_documents({"corso": context.user_data["corso"], "day": weekday}) == 0:
        await update.callback_query.message.reply_text("Nessuna lezione disponibile per questo corso.")
        return shared.end_conversation(update, context)

    cursor = palinsesto.find({"corso": context.user_data["corso"], "day": weekday})
    
    classKeyboard = []
    for doc in cursor:
        maxP = int(doc.get("max_people"))
        nPeople = prenotazioni.count_documents({"class_id": str(doc["_id"]), "day": day})
        classId = str(doc["_id"])
        logging.getLogger("gym_bot").debug(f"classId: {classId}")
        emoji = "✅" if nPeople < maxP else "❌"
        classKeyboard.append([InlineKeyboardButton(f"{emoji} {doc['start_hour']}:{doc['start_minute']} - {doc['end_hour']}:{doc['end_minute']} ({nPeople}/{doc['max_people']})", callback_data=classId)])
    classKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
    keyboard = InlineKeyboardMarkup(classKeyboard)
    await update.callback_query.edit_message_text("Seleziona una classe:", reply_markup=keyboard)
    return "display_class_info_and_confirm"

async def display_class_info_and_confirm(update: Update, context: CallbackContext):
    class_id = update.callback_query.data
    context.user_data["class_id"] = class_id
    logging.getLogger("gym_bot").debug(f"class_id: {class_id}")
    database = shared.get_db()
    palinsesto = database["palinsesto"]
    prenotazioni = database["prenotazioni"]
    members = database["members"]

    doc = palinsesto.find_one({"_id": ObjectId(class_id)})
    if doc is None:
        await update.callback_query.message.reply_text("Classe non trovata.")
        return shared.end_conversation(update, context)
    
    people = []
    cursor = prenotazioni.find({"class_id": class_id, "day": context.user_data["day"]})
    for person in cursor:
        user = members.find_one({"id": person["user_id"]})
        people.append(user["full_name"])
    peopleString = "\n".join(people)

    text = f"Corso: {context.user_data["corso"]}\n"
    text += f"Classe: {doc['start_hour']}:{doc['start_minute']} - {doc['end_hour']}:{doc['end_minute']}\n"
    text += f"Giorno: {context.user_data['day']}\n"
    text += f"Persone prenotate: {len(people)}\n"
    text += f"Massimo: {doc['max_people']}\n"
    text += f"Persone:\n{peopleString}"
    keyboard = [
        [InlineKeyboardButton("Conferma", callback_data="confirm"), InlineKeyboardButton("Annulla", callback_data="/cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    return "handle_confirmation"

async def handle_confirmation(update: Update, context: CallbackContext):
    choice = update.callback_query.data
    database = shared.get_db()
    prenotazioni = database["prenotazioni"]
    palinsesto = database["palinsesto"]

    if choice == "confirm":
        if prenotazioni.count_documents({"user_id": str(update.effective_user.id), "class_id": context.user_data["class_id"], "day": context.user_data["day"]}) > 0:
            await update.callback_query.message.reply_text("Hai già prenotato questa classe.")
            return shared.end_conversation(update, context)
        nPrenotati = prenotazioni.count_documents({"class_id": context.user_data["class_id"], "day": context.user_data["day"]})
        nPrenotabili = int(palinsesto.find_one({"_id": ObjectId(context.user_data["class_id"])})["max_people"])
        if nPrenotati >= nPrenotabili:
            await update.callback_query.message.reply_text("La classe è piena.")
            return shared.end_conversation(update, context)
        prenotazioni.insert_one({
            "user_id": str(update.effective_user.id),
            "class_id": context.user_data["class_id"],
            "day": context.user_data["day"]
        })
        await update.callback_query.message.reply_text("Prenotazione effettuata.")
    return shared.end_conversation(update, context)