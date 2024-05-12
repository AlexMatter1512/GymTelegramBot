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
    # startHandler = CommandHandler("start", start_command.start)
    startHandler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command.start)],
        states={
            "admin_commands": [MessageHandler(filters.Regex(r"admin commands ->"), start_command.admin_commands)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$"),
        ]
    )
    # admin_commandsHandler = MessageHandler("admin commands ->", start_command.admin_commands)
    admin_commandsHandler = MessageHandler(filters.Regex(r"admin commands ->"), start_command.admin_commands)
    normal_commandsHandler = MessageHandler(filters.Regex(r"<- normal commands"), start_command.start)
    accetta_iscrizioneHandler = ConversationHandler(
        entry_points=[CommandHandler("accetta_iscrizione", accetta_iscrizione_command.accetta_iscrizione)],
        states={
            "user_selected": [CallbackQueryHandler(accetta_iscrizione_command.user_selected)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command.cancel),
            CallbackQueryHandler(cancel_command.cancelQuery, pattern="^/cancel$"),
        ]
    )
    # iscriviHandler = CommandHandler("iscriviti", iscriviti_command.iscriviti)
    iscriviHandler = ConversationHandler(
        entry_points=[CommandHandler("iscriviti", iscriviti_command.iscriviti)],
        states={
            "insert_user": [MessageHandler(None, iscriviti_command.insert_user)]
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
    app.add_handler(accetta_iscrizioneHandler)
    app.add_handler(iscriviHandler)
    app.add_handler(prenotaHandler)

def load_config():
    global config
    config = shared.load_config()
    logging.info("Config loaded")

def main():
    setup_logging()
    load_config()
    logging.info("TOKEN: %s", config["TOKEN"])
    app = ApplicationBuilder().token(config["TOKEN"]).build()
    add_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()