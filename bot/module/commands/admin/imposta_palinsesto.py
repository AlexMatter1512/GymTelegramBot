from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import logging
from module import shared
from module.utils.telegramTimeKeyboards import telegramTimeKeyboards
from module.vars import WEEKDAYS

async def imposta_palinsesto(update: Update, context: CallbackContext): #selezione corso
    # Check if the user is an admin
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    database = shared.get_db()
    if database["corsi"].count_documents({}) == 0:
        await update.message.reply_text("Non ci sono corsi disponibili, aggiungine uno con il comando /aggiungi_corso.")
        return ConversationHandler.END
    
    corsi = database["corsi"].find()
    corsiKeyboard = [[InlineKeyboardButton(corso["nome"], callback_data=corso["nome"])] for corso in corsi]
    database.client.close()
    corsiKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
    await update.message.reply_text("Seleziona il corso:", reply_markup=InlineKeyboardMarkup(corsiKeyboard))
    return "select_day"

async def select_day(update: Update, context: CallbackContext):
    query = update.callback_query
    corso = query.data
    context.user_data["corso"] = corso
    logging.info(f"Corso selected: {corso}")
    await query.edit_message_text(text=f"Corso selezionato: {corso}")
    weekdays = WEEKDAYS["ita"]
    daysKeyboard = telegramTimeKeyboards.get_week_days_keyboard(end_day=6, days=weekdays)

    await query.message.reply_text("Seleziona il giorno:", reply_markup=daysKeyboard)
    return "select_start_hour"

async def select_start_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    day = query.data
    context.user_data["day"] = day
    logging.info(f"Day selected: {day}")
    await query.edit_message_text(text=f"Giorno selezionato: {day}")

    hoursKeyboard = telegramTimeKeyboards.get_hours_keyboard(0, 23)
    
    await context.bot.send_message(chat_id=query.message.chat_id, text="Seleziona l'ora di inizio della classe:", reply_markup=hoursKeyboard)
    return "select_start_minute"

async def select_start_minute(update: Update, context: CallbackContext):
    query = update.callback_query
    start_hour = query.data
    context.user_data["start_hour"] = start_hour
    logging.info(f"Start hour selected: {start_hour}")
    # await context.bot.send_message(chat_id=query.message.chat_id, text=f"Ora di inizio selezionata: {start_hour}")
    context.user_data["start_hour_message"] = await query.edit_message_text(f"Ora di inizio selezionata: {start_hour}")

    partitionsKeyboard = telegramTimeKeyboards.get_hours_partitions_keyboard(15)
    
    # await query.edit_message_text(f"Seleziona i minuti di inizio:", reply_markup=partitionsKeyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Seleziona i minuti di inizio:", reply_markup=partitionsKeyboard)
    return "select_end_hour"
    
async def select_end_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    start_hour = context.user_data["start_hour"]
    start_minute = query.data
    start_hour_message = context.user_data["start_hour_message"]
    context.user_data["start_minute"] = start_minute
    logging.info(f"Start minute selected: {start_minute}")

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=start_hour_message.message_id, text=f"Ora di inizio selezionata: {start_hour}:{start_minute}")

    hoursKeyboard = telegramTimeKeyboards.get_hours_keyboard(int(start_hour), 24)
    
    # await query.edit_message_text("Seleziona l'ora di fine:", reply_markup=hoursKeyboard)
    await query.message.delete()
    await context.bot.send_message(chat_id=query.message.chat_id, text="Seleziona l'ora di fine:", reply_markup=hoursKeyboard)
    return "select_end_minute"

async def select_end_minute(update: Update, context: CallbackContext):
    query = update.callback_query
    end_hour = query.data
    context.user_data["end_hour"] = end_hour
    logging.info(f"End hour selected: {end_hour}")
    context.user_data["end_hour_message"] = await query.edit_message_text(f"Ora di fine selezionata: {end_hour}")

    partitionsKeyboard = telegramTimeKeyboards.get_hours_partitions_keyboard(15)
    await context.bot.send_message(chat_id=query.message.chat_id, text="Seleziona i minuti di fine:", reply_markup=partitionsKeyboard)
    return "save_palinsesto_class"

async def save_palinsesto_class(update: Update, context: CallbackContext):
    query = update.callback_query
    end_hour = context.user_data["end_hour"]
    end_minute = query.data
    context.user_data["end_minute"] = end_minute
    end_hour_message = context.user_data["end_hour_message"]
    logging.info(f"End minute selected: {end_minute}")
    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=end_hour_message.message_id, text=f"Ora di fine selezionata: {end_hour}:{end_minute}")

    # Workout class data dict
    workout_class = {
        "corso": context.user_data["corso"],
        "day": context.user_data["day"],
        "start_hour": context.user_data["start_hour"],
        "start_minute": context.user_data["start_minute"],
        "end_hour": context.user_data["end_hour"],
        "end_minute": context.user_data["end_minute"]
    }

    # Save workout class to database
    database = shared.get_db()
    palinsesto = database["palinsesto"]
    
    # Check if an index with constraints for the uniqueness of the day already exists otherwise create it
    if "corso_1_day_1_start_hour_1_end_hour_1" not in palinsesto.index_information():
        index = palinsesto.create_index([("corso", 1), ("day", 1), ("start_hour", 1), ("end_hour", 1)], unique=True)
        logging.info(f"Index created: {index}")

    # check if there is already a class at that time
    dayClasses = palinsesto.find({"day": workout_class["day"], "corso": workout_class["corso"]})
    for dayClass in dayClasses:
        if workout_class["start_hour"] >= dayClass["start_hour"] and workout_class["start_hour"] < dayClass["end_hour"] or workout_class["end_hour"] > dayClass["start_hour"] and workout_class["end_hour"] <= dayClass["end_hour"]:
            await query.edit_message_text("⚠️ Esiste già una classe per quel corso in quell'orario:")
            await query.message.reply_text(f"{dayClass["corso"]} {dayClass["day"]}\nOra di inizio: {dayClass['start_hour']}:{dayClass['start_minute']}\nOra di fine: {dayClass['end_hour']}:{dayClass['end_minute']}")
            return ConversationHandler.END
    palinsesto.insert_one(workout_class)
    database.client.close()

    await query.edit_message_text("Classe aggiunta al palinsesto!")

    return ConversationHandler.END