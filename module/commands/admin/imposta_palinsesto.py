from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import logging
from module import shared as shared
from module.utils import telegramTimeKeyboards

async def imposta_palinsesto(update: Update, context: CallbackContext):
    # Check if the user is an admin
    if update.effective_user.id not in shared.config["ADMINS"].values():
        return await update.message.reply_text("Non sei autorizzato ad utilizzare questo comando.")
    
    daysKeyboard = telegramTimeKeyboards.get_week_days_keyboard(6)

    await update.message.reply_text("Seleziona il giorno:", reply_markup=daysKeyboard)
    return "select_start_hour"

async def select_start_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    day = query.data
    context.user_data["day"] = day
    logging.info(f"Day selected: {day}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Giorno selezionato: {day}")

    hoursKeyboard = telegramTimeKeyboards.get_hours_keyboard(6, 22)
    
    await query.edit_message_text(f"Seleziona l'ora di inizio per {day}:", reply_markup=hoursKeyboard)
    return "select_start_minute"

async def select_start_minute(update: Update, context: CallbackContext):
    query = update.callback_query
    start_hour = query.data
    context.user_data["start_hour"] = start_hour
    logging.info(f"Start hour selected: {start_hour}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Ora di inizio selezionata: {start_hour}")

    partitionsKeyboard = telegramTimeKeyboards.get_hours_partitions_keyboard(15)
    
    await query.edit_message_text(f"Seleziona i minuti di inizio:", reply_markup=partitionsKeyboard)
    return "select_end_hour"
    
async def select_end_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    start_minute = query.data
    context.user_data["start_minute"] = start_minute
    logging.info(f"Start minute selected: {start_minute}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Minuti di inizio selezionati: {start_minute}")

    hoursKeyboard = telegramTimeKeyboards.get_hours_keyboard(6, 22)
    
    await query.edit_message_text("Seleziona l'ora di fine:", reply_markup=hoursKeyboard)
    return "select_end_minute"

async def select_end_minute(update: Update, context: CallbackContext):
    query = update.callback_query
    end_hour = query.data
    context.user_data["end_hour"] = end_hour
    logging.info(f"End hour selected: {end_hour}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Ora di fine selezionata: {end_hour}")

    partitionsKeyboard = telegramTimeKeyboards.get_hours_partitions_keyboard(15)
    
    await query.edit_message_text("Seleziona i minuti di fine:", reply_markup=partitionsKeyboard)
    return "save_palinsesto_class"

async def save_palinsesto_class(update: Update, context: CallbackContext):
    query = update.callback_query
    end_minute = query.data
    context.user_data["end_minute"] = end_minute
    logging.info(f"End minute selected: {end_minute}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Minuti di fine selezionati: {end_minute}")

    # Workout class data dict
    workout_class = {
        "day": context.user_data["day"],
        "start_hour": context.user_data["start_hour"],
        "start_minute": context.user_data["start_minute"],
        "end_hour": context.user_data["end_hour"],
        "end_minute": context.user_data["end_minute"]
    }

    # Save workout class to database
    database = shared.get_db()
    palinsesto = database["palinsesto"]
    # palinsesto.insert_one(workout_class) this doesent avoid overlapping classes
    # check if there is already a class at that time
    dayClasses = palinsesto.find({"day": workout_class["day"]})
    for dayClass in dayClasses:
        if workout_class["start_hour"] >= dayClass["start_hour"] and workout_class["start_hour"] < dayClass["end_hour"]:
            await query.message.reply_text("Esiste già una classe in quell'orario:")
            await query.message.reply_text(f"Ora di inizio: {dayClass['start_hour']}:{dayClass['start_minute']}\nOra di fine: {dayClass['end_hour']}:{dayClass['end_minute']}")
            return ConversationHandler.END
        if workout_class["end_hour"] > dayClass["start_hour"] and workout_class["end_hour"] <= dayClass["end_hour"]:
            await query.message.reply_text("Esiste già una classe in quell'orario:")
            await query.message.reply_text(f"Ora di inizio: {dayClass['start_hour']}:{dayClass['start_minute']}\nOra di fine: {dayClass['end_hour']}:{dayClass['end_minute']}")
            return ConversationHandler.END
    palinsesto.insert_one(workout_class)
    database.client.close()

    await query.edit_message_text("Classe aggiunta al palinsesto!")

    return ConversationHandler.END