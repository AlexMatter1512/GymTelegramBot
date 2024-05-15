import logging
import colorlog
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from telegram.ext import filters
from telegram.ext import (
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
)
from module.commands.admin import (
    accetta_iscrizione as accetta_iscrizione_command,
    rimuovi_utente as rimuovi_utente_command,
    messaggio_broadcast as messaggio_broadcast_command,
    imposta_palinsesto as imposta_palinsesto_command,
)
import module.shared as shared

config = None

# Logging
def setup_logging():
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    console_handler = colorlog.StreamHandler()
    file_handler = logging.FileHandler("bot.log")

    color_formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)s%(reset)s: %(funcName)s: %(message)s',)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(module)s: %(funcName)s: %(message)s')

    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(file_formatter)

    logging.basicConfig(handlers=[console_handler, file_handler], level=logging.INFO)
    # disable logging from pymongo module
    logging.getLogger("pymongo").setLevel(logging.WARNING)

def add_handlers(app):
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
            "select_start_hour": [CallbackQueryHandler(imposta_palinsesto_command.select_start_hour, pattern="^[1-7]$")],
            "select_start_minute": [CallbackQueryHandler(imposta_palinsesto_command.select_start_minute, pattern="^[0-9]{2}$")],
            "select_end_hour": [CallbackQueryHandler(imposta_palinsesto_command.select_end_hour, pattern="^[0-9]{2}$")],
            "select_end_minute": [CallbackQueryHandler(imposta_palinsesto_command.select_end_minute, pattern="^[0-9]{2}$")],
            "save_palinsesto_class": [CallbackQueryHandler(imposta_palinsesto_command.save_palinsesto_class, pattern="^[0-9]{2}$")]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )
    messaggio_broadcastHandler = ConversationHandler(
        entry_points=[CommandHandler("messaggio_broadcast", messaggio_broadcast_command.messaggio_broadcast)],
        states={
            "get_message": [MessageHandler(None, messaggio_broadcast_command.get_message)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$")
        ]
    )

    # User commands
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

    app.add_handler(startHandler)
    app.add_handler(admin_commandsHandler)
    app.add_handler(normal_commandsHandler)
    # Admin commands
    app.add_handler(accetta_iscrizioneHandler)
    app.add_handler(rimuovi_iscrizioneHandler)
    app.add_handler(imposta_palinsestoHandler)
    app.add_handler(messaggio_broadcastHandler)
    # User commands
    app.add_handler(iscriviHandler)
    app.add_handler(prenotaHandler)

def load_config():
    global config
    config = shared.load_config()
    logging.info("Config loaded")

def main():
    setup_logging()
    load_config()
    app = ApplicationBuilder().token(config["TOKEN"]).build()
    add_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()