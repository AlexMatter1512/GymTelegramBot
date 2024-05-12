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

def is_allowed(user: User):
    userDoc = user.to_dict()

    # DB connection
    HOST = config["MONGO"]["host"]
    PORT = config["MONGO"]["port"]
    DB = config["MONGO"]["db"]
    database = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")[DB]
    allowed_users = database["members"]
    isAllowed = allowed_users.find_one(userDoc) is not None
    database.client.close()

    return isAllowed

def get_db():
    HOST = config["MONGO"]["host"]
    PORT = config["MONGO"]["port"]
    DB = config["MONGO"]["db"]
    database = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")[DB]
    return database