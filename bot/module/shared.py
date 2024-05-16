import yaml
import os
import logging
import pymongo
from telegram import User

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                # print(f"Error loading YAML file: {exc}")
                logging.error(f"Error loading YAML file: {exc}")
    return config

config = load_config()

def get_db():
    HOST = config["MONGO"]["host"]
    PORT = config["MONGO"]["port"]
    USERNAME = config["MONGO"]["username"]
    PASSWORD = config["MONGO"]["password"]
    DB = config["MONGO"]["db"]
    # database = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")[DB]
    database = pymongo.MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}")[DB]
    return database

def is_allowed(user: User):
    userDoc = user.to_dict()

    # DB connection
    database = get_db()
    allowed_users = database["members"]
    isAllowed = allowed_users.find_one(userDoc) is not None
    database.client.close()

    return isAllowed

def get_res(name: str):
     #Read the respective resource file
    resource_path = os.path.join(os.path.dirname(__file__), f'../res/{name}.txt')
    try:
        with open(resource_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"Resource file {name}.txt not found")
        return None
    
async def is_in_conversation(update, context):
    if context.user_data.get("in_conversation"):
        await update.message.reply_text("Completa o termina (/cancel) la conversazione corrente prima di iniziarne una nuova.")
        return True
    return False