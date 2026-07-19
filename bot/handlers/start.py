from utils.service import clear_pending_actions
from utils.logger import logger


async def start(update, context):
    telegram_id = update.effective_user.id

    try:
        await clear_pending_actions(update, context)

        logger.info(
            "User %s used /start",
            telegram_id,
        )

        captions = """
🤖 Welcome to the Google Drive Uploader Bot!

I can help you directly upload files to your designated Google Drive folders with ease.

🔐 How to Get Started:
Before you can start uploading, you need to connect your Google Drive account.

Send /manage to link and connect your Google Drive account.

Send /upload (or simply send/forward a file) to upload it directly to your Drive!

🛠️ Useful Commands:
/manage – Connect, switch, or manage your Google Drive accounts and target folders.

/upload – Send or upload a file directly to your connected Google Drive.

/help – View full instructions, detailed command list, and quick troubleshooting tips.

📌 Tip: Make sure your account is linked via /manage before trying to use /upload!
"""

        await update.message.reply_text(captions)

        logger.info(
            "/start completed for user %s",
            telegram_id,
        )

    except Exception:
        logger.exception(
            "Failed to process /start for user %s",
            telegram_id,
        )

        await update.message.reply_text(
            "❌ Something went wrong. Please try again."
        )