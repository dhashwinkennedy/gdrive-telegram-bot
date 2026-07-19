from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
TOKEN_URL = os.getenv("TOKEN_URL")
USER_INFO_URL = os.getenv("USER_INFO_URL")
ACCESS_TOKEN_URL = os.getenv("ACCESS_TOKEN_URL")
BOT_HMAC_SECRET = os.getenv("BOT_HMAC_SECRET")
GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")