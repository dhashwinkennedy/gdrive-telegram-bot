from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BACKEND_URL
from utils.security import create_signature

def accounts_buttons(accounts):

    keyboard = []

    for account in accounts:
        email = account["email"]

        keyboard.append([
            InlineKeyboardButton(
                text=f"📧 {email}",
                callback_data=f"verify:{email}"
            )
        ])


    markup = InlineKeyboardMarkup(keyboard)
    return markup

def verify_button(telegram_id,email):
    ts, sig = create_signature(telegram_id)
    url = (
    f"{BACKEND_URL}/verify"
    f"?telegram_id={telegram_id}"
    f"&email={email}"
    f"&ts={ts}" 
    f"&sig={sig}")
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Verify Now",
                url=url
            )
        ],
        
    ]
    return InlineKeyboardMarkup(keyboard)