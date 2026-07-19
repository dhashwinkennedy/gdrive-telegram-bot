from config import BACKEND_URL
from keyboards.unlink import unlink
import requests
from utils.security import create_signature
from utils.logger import logger


async def unlink_callback(update, context):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    email = query.data.split(":", 1)[1]

    logger.info(
        "User %s initiated unlink for %s",
        telegram_id,
        email,
    )

    await query.edit_message_text(
        f"""⚠️ Unlink Google Account?

📧 {email}

This action cannot be undone.""",
        reply_markup=unlink(email),
    )

    context.user_data["active_message_id"] = query.message.message_id


async def unlink_confirm_callback(update, context):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    email = query.data.split(":", 1)[1]

    logger.info(
        "User %s confirmed unlink for %s",
        telegram_id,
        email,
    )

    ts, sig = create_signature(telegram_id)

    try:
        response = requests.delete(
            f"{BACKEND_URL}/manage/account",
            json={
                "telegram_id": telegram_id,
                "email": email,
                "ts": ts,
                "sig": sig,
            },
            timeout=10,
        )

        if response.status_code == 200:

            logger.info(
                "Successfully unlinked account %s for user %s",
                email,
                telegram_id,
            )

            await query.edit_message_text(
                "✅ Google account unlinked successfully."
            )

        else:
            try:
                detail = response.json().get(
                    "detail",
                    "Failed to unlink account."
                )
            except Exception:
                detail = "Failed to unlink account."

            logger.warning(
                "Unlink rejected (%s) for user %s (%s): %s",
                response.status_code,
                telegram_id,
                email,
                detail,
            )

            await query.edit_message_text(
                f"❌ {detail}"
            )

    except requests.RequestException:

        logger.exception(
            "Failed to unlink account %s for user %s",
            email,
            telegram_id,
        )

        await query.edit_message_text(
            "❌ Unable to connect to the server."
        )

    finally:
        context.user_data.pop("active_message_id", None)


async def unlink_cancel_callback(update, context):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id

    logger.info(
        "User %s cancelled unlink",
        telegram_id,
    )

    await query.edit_message_text(
        "❌ Unlink cancelled."
    )

    context.user_data.pop("active_message_id", None)