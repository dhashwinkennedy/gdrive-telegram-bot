from keyboards.manage import (
    accounts_buttons
    ,manage_account_buttons
)
import requests
from config import BACKEND_URL
from datetime import datetime, UTC
from utils.service import clear_pending_actions
from utils.security import create_signature
from utils.logger import logger


async def manage(update, context):
    await clear_pending_actions(update, context)

    telegram_id = update.effective_user.id

    logger.info(
        "User %s used /manage",
        telegram_id,
    )

    ts, sig = create_signature(telegram_id)

    try:
        response = requests.get(
            f"{BACKEND_URL}/manage/{telegram_id}",
            params={
                "ts": ts,
                "sig": sig,
            },
            timeout=10,
        )

        if response.status_code == 404:
            logger.info(
                "User %s has no connected accounts",
                telegram_id,
            )

            await update.message.reply_text(
                "❌ No Google accounts connected.\n\n"
                "Use /connect to connect your Google Drive.\n"
                "Use /help for more information."
            )
            return

        response.raise_for_status()

        accounts = response.json()["accounts"]

    except requests.RequestException:
        logger.error(
    "Failed to load accounts for user %s",
    telegram_id,
    exc_info=True,
)

        await update.message.reply_text(
            "❌ Unable to connect to the server."
        )
        return

    logger.info(
        "Loaded %s account(s) for user %s",
        len(accounts),
        telegram_id,
    )

    msg = await update.message.reply_text(
        "Manage your Google Drive Account(s).",
        reply_markup=accounts_buttons(accounts, telegram_id),
    )

    context.user_data["active_message_id"] = msg.message_id


async def manage_account_callback(update, context):

    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    email = query.data.split(":", 1)[1]
    logger.info(
    "User %s opened account %s",
    telegram_id,
    email,
)
    try:
        ts, sig = create_signature(telegram_id)
        response = requests.get(
            f"{BACKEND_URL}/manage/{telegram_id}/{email}",
            params={
                "ts":ts,
                "sig":sig
            },
            timeout=10,
        )

        response.raise_for_status()

        account = response.json()["account"]

    except Exception as e:
        logger.exception(
    "Failed to load account %s for user %s",
    email,
    telegram_id,
)
        await query.edit_message_text(
            "❌ Unable to load account."
        )
        return

    caption = f"""
👤 Name: {account["name"]}

📧 Email: {account["email"]}

📂 Target Folder:
{account["target_folder"]}
"""

    target_time = datetime.fromisoformat(account["app_expires_at"])

    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=UTC)

    is_expired = datetime.now(UTC) > target_time

    if is_expired:
        caption += f"""

🚫 Expired On
{target_time.strftime("%d %b %Y")}

⚠️ Verify using /verify.
"""
    else:
        caption += f"""

⏳ Verified Until
{target_time.strftime("%d %b %Y")}

"""
    logger.info(
    "Displayed account details for %s (user %s)",
    email,
    telegram_id,
)
    await query.edit_message_text(
        caption,
        reply_markup=manage_account_buttons(
            is_expired,
            telegram_id,
            account["email"],
        ),
    )

    context.user_data["active_message_id"] = query.message.message_id


async def change_folder_callback(update, context):
    query = update.callback_query
    await query.answer()

    email = query.data.split(":", 1)[1]

    context.user_data["waiting_folder"] = True
    context.user_data["folder_email"] = email
    logger.info(
    "User %s started folder change for %s",
    update.effective_user.id,
    email,
)

    await query.edit_message_text(
        """📂 Change Destination Folder

Send the new destination folder.

Examples:
./Photos
./College/Notes
./Projects/Python

Send /cancel to cancel."""
    )

    context.user_data["active_message_id"] = query.message.message_id


async def receive_folder(update, context):

    if not context.user_data.get("waiting_folder"):
        return

    telegram_id = update.effective_user.id
    email = context.user_data["folder_email"]
    folder = update.message.text.strip()

    logger.info(
        "User %s submitted folder '%s' for %s",
        telegram_id,
        folder,
        email,
    )

    try:
        await update.message.delete()
    except Exception:
        pass

    ts, sig = create_signature(telegram_id)

    try:
        response = requests.patch(
            f"{BACKEND_URL}/manage/folder",
            json={
                "telegram_id": telegram_id,
                "email": email,
                "target_folder": folder,
                "ts": ts,
                "sig": sig,
            },
            timeout=10,
        )

    except Exception:
        logger.exception(
            "Failed to contact backend while updating folder for user %s (%s)",
            telegram_id,
            email,
        )

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data["active_message_id"],
            text=(
                "❌ Unable to connect to the server.\n\n"
                "Please try again or send /cancel."
            ),
        )
        return

    # ---------------- Success ----------------

    if response.status_code == 200:

        logger.info(
            "Folder updated for user %s (%s) -> %s",
            telegram_id,
            email,
            folder,
        )

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data["active_message_id"],
            text="✅ Destination folder updated successfully.",
        )

        context.user_data.pop("waiting_folder", None)
        context.user_data.pop("folder_email", None)
        context.user_data.pop("active_message_id", None)

        return

    # ---------------- Validation / Other Error ----------------

    detail = response.json().get(
        "detail",
        "Failed to update folder."
    )

    logger.warning(
        "Folder update rejected (%s) for user %s (%s): %s",
        response.status_code,
        telegram_id,
        email,
        detail,
    )

    # Keep waiting_folder=True so the user can retry.
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["active_message_id"],
        text=(
            f"❌ {detail}\n\n"
            "Please send a valid destination folder.\n\n"
            "Examples:\n"
            "./Photos\n"
            "./College/Notes\n"
            "./Projects/Python\n\n"
            "Send /cancel to cancel."
        ),
    )