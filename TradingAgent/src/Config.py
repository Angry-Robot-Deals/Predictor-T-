import os
import dotenv
import yaml

dotenv.load_dotenv('../.env')

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASS = os.getenv("DB_PASS")
SCHEMA = os.getenv("DB_SCHEMA")

SETTINGS = os.getenv("SETTINGS")

settings = None
# with open(SETTINGS, 'r') as file:
#     settings = yaml.safe_load(file)

