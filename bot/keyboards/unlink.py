from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.logger import logger


def unlink(email):
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Yes, Unlink",
                callback_data=f"unlink_confirm:{email}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="unlink_cancel"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


async def unlink_cancel_callback(update, context):
    query = update.callback_query
    await query.answer()

    logger.info(
        "User %s cancelled unlink operation",
        update.effective_user.id,
    )

    await query.edit_message_text(
        "❌ Unlink cancelled."
    )

    context.user_data.pop("active_message_id", None)