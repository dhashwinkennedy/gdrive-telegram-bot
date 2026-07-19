
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def accounts_buttons(accounts):

    keyboard = []

    for account in accounts:
        email = account["email"]

        keyboard.append([
            InlineKeyboardButton(
                text=f"📧 {email}",
                callback_data=f"upload:{email}"
            )
        ])


    markup = InlineKeyboardMarkup(keyboard)
    return markup

def rename_button():
    keyboard = [
        [
            InlineKeyboardButton(
                "✏ Rename",
                callback_data="rename"
            )
        ],
        [
            InlineKeyboardButton(
                "⏩ Keep Original Name",
                callback_data="keep_name"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def web_view_button(link):
    keyboard = [
        [
            InlineKeyboardButton(
                "Click to view",
                url=link
            )
        ],
        
    ]
    return InlineKeyboardMarkup(keyboard)

