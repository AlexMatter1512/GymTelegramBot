import logging
from logging.handlers import RotatingFileHandler
import argparse
import colorlog
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from telegram.ext import filters
from telegram.ext import (
    Application,
    Updater,
    CommandHandler,
    CallbackContext,
    ApplicationBuilder,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
)
from module.commands import (
    cancel as cancel_command,
    start as start_command,
    prenota as prenota_command,
    iscriviti as iscriviti_command,
    info as info_command,
    palinsesto as palinsesto_command,
)
from module.commands.admin import (
    accetta_iscrizione as accetta_iscrizione_command,
    rimuovi_utente as rimuovi_utente_command,
    messaggio_broadcast as messaggio_broadcast_command,
    imposta_palinsesto as imposta_palinsesto_command,
    gestisci_corsi as gestisci_corsi_command,
)
import module.shared as shared

config = None

# Logging
def setup_logging(logLevel=logging.INFO):
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    # Create the formatters
    color_formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)s%(reset)s: %(funcName)s: %(message)s',)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(module)s: %(funcName)s: %(message)s')

    # Create console handler with color formatter
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(color_formatter)

    # Create file handler with file formatter
    file_handler = RotatingFileHandler("bot.log", maxBytes=1024000, backupCount=3)  # Rotate log files
    file_handler.setFormatter(file_formatter)

    telegram_logger = logging.getLogger("telegram")
    telegram_logger.setLevel(logging.INFO)
    telegram_logger.addHandler(console_handler)
    telegram_logger.addHandler(file_handler)
    telegram_logger.propagate = False

    # Set up the custom logger
    myLogger = logging.getLogger("gym_bot")
    myLogger.setLevel(logLevel)
    myLogger.addHandler(console_handler)
    myLogger.addHandler(file_handler)
    myLogger.propagate = False

    myLogger.info("Logging setup completed")

def add_handlers(app: Application):
    logging.getLogger("gym_bot").info("Adding handlers")
    startHandler = CommandHandler("start", start_command.start)
    admin_commandsHandler = MessageHandler(filters.Regex(r"admin commands ->"), start_command.admin_commands)
    normal_commandsHandler = MessageHandler(filters.Regex(r"<- normal commands"), start_command.start)

    # Admin commands
    accetta_iscrizioneHandler = ConversationHandler(
        entry_points=[CommandHandler("accetta_iscrizione", accetta_iscrizione_command.accetta_iscrizione)],
        states={
            "user_selected": [CallbackQueryHandler(accetta_iscrizione_command.user_selected, pattern="^[0-9]+$")]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$"),
        ]
    )
    rimuovi_iscrizioneHandler = ConversationHandler(
        entry_points=[CommandHandler("rimuovi_utente", rimuovi_utente_command.rimuovi_utente)],
        states={
            "choose_list": [CallbackQueryHandler(rimuovi_utente_command.choose_list)],
            "get_id": [MessageHandler(~filters.COMMAND, rimuovi_utente_command.get_id)],
            "confirm": [CallbackQueryHandler(rimuovi_utente_command.confirm)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )
    imposta_palinsestoHandler = ConversationHandler(
        entry_points=[CommandHandler("imposta_palinsesto", imposta_palinsesto_command.imposta_palinsesto)],
        states={
            "select_day": [CallbackQueryHandler(imposta_palinsesto_command.select_day, pattern="^(?!/).*$")],
            "select_start_hour": [CallbackQueryHandler(imposta_palinsesto_command.select_start_hour, pattern="^(?!/).*$")],
            "select_start_minute": [CallbackQueryHandler(imposta_palinsesto_command.select_start_minute, pattern="^(?!/).*$")],
            "select_end_hour": [CallbackQueryHandler(imposta_palinsesto_command.select_end_hour, pattern="^(?!/).*$")],
            "select_end_minute": [CallbackQueryHandler(imposta_palinsesto_command.select_end_minute, pattern="^(?!/).*$")],
            "save_palinsesto_class": [CallbackQueryHandler(imposta_palinsesto_command.save_palinsesto_class, pattern="^(?!/).*$")]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )
    messaggio_broadcastHandler = ConversationHandler(
        entry_points=[CommandHandler("messaggio_broadcast", messaggio_broadcast_command.messaggio_broadcast)],
        states={
            "get_message": [MessageHandler(~filters.COMMAND, messaggio_broadcast_command.get_message)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )
    gestisci_corsiHandler = ConversationHandler(
        entry_points=[CommandHandler("gestisci_corsi", gestisci_corsi_command.gestisci_corsi)],
        states={
            # "select_action": [CallbackQueryHandler(gestisci_corsi_command.select_action, pattern="^(add_course|remove_course)$")],
            # "ask_course_name": [MessageHandler(~filters.COMMAND, gestisci_corsi_command.ask_course_name)],
            "ask_course_name": [CallbackQueryHandler(gestisci_corsi_command.ask_course_name, pattern="^(add_course|remove_course)$")],
            "get_course_name": [MessageHandler(~filters.COMMAND, gestisci_corsi_command.get_course_name)],
            "confirm_course_name": [CallbackQueryHandler(gestisci_corsi_command.confirm_course_name, pattern="^(confirm|cancel)$")]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )

    # User commands
    infoHandler = CommandHandler("info", info_command.info)

    iscriviHandler = ConversationHandler(
        entry_points=[CommandHandler("iscriviti", iscriviti_command.iscriviti)],
        states={
            "insert_user": [MessageHandler(~filters.COMMAND, iscriviti_command.insert_user)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$"),
        ]
    )
    prenotaHandler = CommandHandler("prenota", prenota_command.prenota)
    palinsestoHandler = ConversationHandler(
        entry_points=[CommandHandler("palinsesto", palinsesto_command.selezionaCorso)],
        states={
            "selezionaGiorno": [CallbackQueryHandler(palinsesto_command.selezionaGiorno, pattern="^(?!/).*$")],
            "sendPalinsesto": [CallbackQueryHandler(palinsesto_command.sendPalinsesto, pattern="^(?!/).*$")]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )

    app.add_handler(startHandler)
    app.add_handler(admin_commandsHandler)
    app.add_handler(normal_commandsHandler)
    
    # Admin commands
    app.add_handler(accetta_iscrizioneHandler)
    app.add_handler(rimuovi_iscrizioneHandler)
    app.add_handler(imposta_palinsestoHandler)
    app.add_handler(messaggio_broadcastHandler)
    app.add_handler(gestisci_corsiHandler)
    
    # User commands
    app.add_handler(infoHandler)
    app.add_handler(iscriviHandler)
    app.add_handler(prenotaHandler)
    app.add_handler(palinsestoHandler)

def load_config():
    global config
    config = shared.load_config()
    logging.getLogger("gym_bot").info("Config loaded")

def main(logLevel=logging.INFO):
    # setup_logging()
    setup_logging(logLevel)
    load_config()
    app = ApplicationBuilder().token(config["TOKEN"]).build()
    add_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram bot for gym management")
    parser.add_argument("-l", "--log-level", type=str, default="INFO", help="Set the log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    args = parser.parse_args()
    logLevel = getattr(logging, args.log_level.upper(), None)
    main(logLevel)