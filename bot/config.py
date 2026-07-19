from dotenv import load_dotenv
import os

load_dotenv()



BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
UPLOAD_LENGTH = os.getenv("UPLOAD_LENGTH")
UPLOAD_TIME = os.getenv("UPLOAD_TIME")