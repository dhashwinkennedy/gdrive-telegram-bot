from config import BOT_TOKEN
from utils.logger import logger
import requests


def send_telegram_message(
    message: str,
    chat_id: int,
):
    if chat_id is None:
        logger.warning(
            "Attempted to send Telegram message with no chat_id"
        )
        return False

    try:
        logger.info(
            "Sending Telegram message to user %s",
            chat_id,
        )

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
            },
            timeout=20,
        )

        response.raise_for_status()

        logger.info(
            "Telegram message sent successfully to user %s",
            chat_id,
        )

        return True

    except requests.RequestException:
        logger.exception(
            "Failed to send Telegram message to user %s",
            chat_id,
        )
        return False