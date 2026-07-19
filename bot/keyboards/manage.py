
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BACKEND_URL
from utils.security import create_signature

def accounts_buttons(accounts,telegram_id):

    keyboard = []

    for account in accounts:
        email = account["email"]

        keyboard.append([
            InlineKeyboardButton(
                text=f"📧 {email}",
                callback_data=f"manage:{email}"
            )
        ])

    ts, sig = create_signature(telegram_id)
    url = (
    f"{BACKEND_URL}/google/login"
    f"?telegram_id={telegram_id}"
    f"&ts={ts}"
    f"&sig={sig}"
)
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Add Google Account",
            url=url
        )
    ])

    markup = InlineKeyboardMarkup(keyboard)
    return markup


def manage_account_buttons(is_expired,telegram_id,email):

    keyboard = []


    if is_expired:
        keyboard.append([
            InlineKeyboardButton(
                text="Verify Now",
                callback_data=f"verify:{email}"
            )
        ])
    else:

        keyboard.append([
            InlineKeyboardButton(
                text="Change Destination Folder",
                callback_data=f"folder:{email}"
            )
        ])
    keyboard.append([
            InlineKeyboardButton(
                text="Unlink Account",
                callback_data=f"unlink:{email}"
            )
        ])
    markup = InlineKeyboardMarkup(keyboard)
    return markup


