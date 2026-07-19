from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import BACKEND_URL
from utils.service import clear_pending_actions
from utils.security import create_signature
from utils.logger import logger


async def connect(update, context):
    telegram_id = update.effective_user.id

    try:
        await clear_pending_actions(update, context)

        logger.info(
            "User %s initiated /connect",
            telegram_id,
        )

        ts, sig = create_signature(telegram_id)

        url = (
            f"{BACKEND_URL}/google/login"
            f"?telegram_id={telegram_id}"
            f"&ts={ts}"
            f"&sig={sig}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔗 Connect Google Drive",
                    url=url,
                )
            ]
        ]

        await update.message.reply_text(
            "Click below to connect your Google Drive Account",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(
            "Connect link sent to user %s",
            telegram_id,
        )

    except Exception:
        logger.exception(
            "Failed to start /connect for user %s",
            telegram_id,
        )

        await update.message.reply_text(
            "❌ Unable to start the connection process. Please try again later."
        )