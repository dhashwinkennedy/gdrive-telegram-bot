from utils.service import clear_pending_actions
from utils.logger import logger


async def help(update, context):
    telegram_id = update.effective_user.id

    try:
        await clear_pending_actions(update, context)

        logger.info(
            "User %s used /help",
            telegram_id,
        )

        captions = """
💡 Bot Help & Commands

Here is how to use the bot and manage your connected accounts:

🔗 /connect
• Link a new Google account to the bot.

⚙️ /manage
• View all your connected Google accounts.
• Check your current account verification status.
• Unlink any account instantly.

📤 /upload
• Upload files by using the command or by directly sending a file to the chat.
• ⚠️ File limit: Maximum 2GB per file.
• 🚫 Note: Batch files (multiple files sent at once) are not allowed. Please upload files one by one.

🔐 /verify
• Check your Google account session validity.
• ⏳ Important: Every connected Google account session expires after 10 days. You will need to re-verify your account every 10 days to keep services active.
"""

        await update.message.reply_text(captions)

        logger.info(
            "/help completed for user %s",
            telegram_id,
        )

    except Exception:
        logger.exception(
            "Failed to process /help for user %s",
            telegram_id,
        )

        await update.message.reply_text(
            "❌ Something went wrong. Please try again."
        )