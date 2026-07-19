from utils.service import clear_pending_actions
import requests
from config import BACKEND_URL,UPLOAD_LENGTH,UPLOAD_TIME
from keyboards.upload import (
    accounts_buttons,
    rename_button,
    web_view_button)
import os
import mimetypes
from utils.security import create_signature
import tempfile
import uuid
from utils.logger import logger

async def upload(update, context):
    await clear_pending_actions(update, context)
    telegram_id = update.effective_user.id
    logger.info(
    "User %s started upload flow",
    telegram_id,
)
    context.user_data["upload"] = {}

    msg = await update.message.reply_text(
        """📎 Send the file you want to upload.

Supported:
• Documents
• Images
• Videos

Send /cancel to cancel."""
    )

    context.user_data["active_message_id"] = msg.message_id

async def upload_account_callback(update, context):
    query = update.callback_query
    await query.answer()

    upload = context.user_data.get("upload")

    if not upload:
        await query.answer(
            "This upload request has already been completed.",
            show_alert=False,
        )
        return

    if upload.get("uploading"):
        await query.answer(
            "Upload already in progress.",
            show_alert=False,
        )
        return

    upload["uploading"] = True

    email = query.data.split(":", 1)[1]
    filename = upload.get("filename", upload["original_name"])

    logger.info(
    "User %s started uploading '%s' to %s",
    update.effective_user.id,
    filename,
    email,
)
    await query.edit_message_text(
        "⏳ Uploading... Please wait."
    )

    try:
        link = await upload_from_tg(
            update,
            context,
            filename,
            email,
        )
        logger.info(
    "Upload completed for user %s (%s)",
    update.effective_user.id,
    filename,
)

        await query.edit_message_text(
            "✅ Uploaded successfully!",
            reply_markup=web_view_button(link),
        )

    except Exception as e:

        logger.exception(
    "Upload failed for user %s (%s)",
    update.effective_user.id,
    filename,
)
        await query.edit_message_text(
            f"❌ {e}"
        )


async def receive_upload_file(update, context):
    if update.message.document:
        file = update.message.document
        filename = file.file_name

    elif update.message.photo:
        file = update.message.photo[-1]
        filename = f"photo_{file.file_unique_id}.jpg"

    elif update.message.video:
        file = update.message.video
        filename = file.file_name or f"video_{file.file_unique_id}.mp4"

    elif update.message.audio:
        file = update.message.audio
        filename = file.file_name or f"audio_{file.file_unique_id}.mp3"

    else:
        return
    
    telegram_id = update.effective_user.id
    file_size = file.file_size or 0

    logger.info(
    "User %s sent file '%s' (%s bytes)",
    telegram_id,
    filename,
    file_size,
)
    

    if file_size > (int(UPLOAD_LENGTH)*1024 * 1024):
        logger.warning(
    "User %s attempted oversized upload '%s' (%s bytes)",
    telegram_id,
    filename,
    file_size,
)
        await update.message.reply_text(
            f"""❌ File is too large.

    Maximum allowed size: {UPLOAD_LENGTH} MB
    Your file: {file_size / (1024 * 1024):.2f} MB"""
        )
        return

    upload = context.user_data.setdefault("upload", {})
    upload["telegram_file"] = file
    upload["original_name"] = filename
    old = context.user_data.get("active_message_id")

    if old:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=old,
            )
        except:
            pass

    msg = await update.message.reply_text(
        "Choose a filename option.",
        reply_markup=rename_button(),
    )

    context.user_data["active_message_id"] = msg.message_id


async def upload_from_tg(
    update,
    context,
    name: str,
    email: str,
):
    upload = context.user_data["upload"]

    telegram_file = upload["telegram_file"]
    original_name = upload["original_name"]

    upload_name = name or original_name

    # Create unique temporary file
    ext = os.path.splitext(original_name)[1]
    local_path = os.path.join(
        tempfile.gettempdir(),
        f"{uuid.uuid4()}{ext}"
    )

    mime_type = (
        mimetypes.guess_type(upload_name)[0]
        or "application/octet-stream"
    )
    telegram_id = update.effective_user.id

    try:
        # Download from Telegram
        file = await telegram_file.get_file()

        logger.info(
    "Downloading Telegram file for user %s",
    telegram_id,
)
        
        await file.download_to_drive(local_path)

        logger.info(
    "Download complete for user %s",
    telegram_id,
)

        with open(local_path, "rb") as f:
            ts, sig = create_signature(telegram_id)
            logger.info(
    "Uploading '%s' to Google Drive for user %s (%s)",
    upload_name,
    telegram_id,
    email,
)

            response = requests.post(
                f"{BACKEND_URL}/google/upload",
                params={
                    "telegram_id": telegram_id,
                    "email": email,
                    "filename": upload_name,
                    "ts": ts,
                    "sig": sig,
                },
                files={
                    "file": (
                        upload_name,
                        f,
                        mime_type,
                    )
                },
                timeout=int(UPLOAD_TIME),
            )

        if response.status_code != 201:

            try:
                detail = response.json().get(
                    "detail",
                    "Upload failed."
                )
                
            except Exception:
                detail = response.text or "Upload failed."

            logger.warning(
    "Backend rejected upload for user %s (%s): %s",
    telegram_id,
    upload_name,
    detail,
)
            raise Exception(detail)

        logger.info(
    "Google Drive upload successful for user %s (%s)",
    telegram_id,
    upload_name,
)
        return response.json()["driveLink"]
    
    

    finally:
        logger.debug(
    "Cleaning upload resources for user %s",
    telegram_id,
)
        if os.path.exists(local_path):
            os.remove(local_path)

        upload.pop("uploading", None)
        context.user_data.pop("upload", None)
        context.user_data.pop("active_message_id", None)


async def keep_name_callback(update, context):

    query = update.callback_query
    await query.answer()

    upload = context.user_data.get("upload")

    if not upload:
        await query.edit_message_text("No file selected.")
        return

    upload["filename"] = upload["original_name"]

    telegram_id = update.effective_user.id

    logger.info(
    "User %s kept original filename '%s'",
    telegram_id,
    upload["original_name"],
)

    try:
        ts,sig = create_signature(telegram_id)
        response = requests.get(
            f"{BACKEND_URL}/manage/{telegram_id}",
            params={"ts":ts,
                    "sig":sig},
            timeout=10,
        )

        if response.status_code == 404:
            logger.info(
    "User %s attempted upload with no connected accounts",
    telegram_id,
)
            await query.edit_message_text(
                "❌ No Google accounts connected.\n\n"
                "Use /connect to connect your Google Drive.\n"
                "Use /help for more information."
            )
            return

        response.raise_for_status()

        accounts = response.json()["accounts"]

    except requests.RequestException:

        logger.exception(
    "Failed loading upload accounts for user %s",
    telegram_id,
)
        await query.edit_message_text(
            "❌ Unable to connect to the server."
        )
        return

    await query.edit_message_text(
        "Select the Google account.",
        reply_markup=accounts_buttons(accounts),
    )

    context.user_data["active_message_id"] = query.message.message_id

async def rename_callback(update, context):
    query = update.callback_query
    await query.answer()

    upload = context.user_data.get("upload")

    if not upload:
        await query.edit_message_text("No file selected.")
        return

    upload["waiting_filename"] = True

    logger.info(
    "User %s chose to rename upload",
    update.effective_user.id,
)

    await query.edit_message_text(
    """✏ Send the new filename.

Example:
Resume.pdf

Send /cancel to cancel."""
)

    context.user_data["active_message_id"] = query.message.message_id


async def receive_filename(update, context):

    upload = context.user_data.get("upload")

    if not upload or not upload.get("waiting_filename"):
        return

    upload["filename"] = update.message.text.strip()
    telegram_id = update.effective_user.id


    logger.info(
    "User %s renamed upload to '%s'",
    telegram_id,
    upload["filename"],
)
    upload.pop("waiting_filename", None)

    try:
        await update.message.delete()
    except Exception:
        pass


    try:
        ts,sig = create_signature(telegram_id)
        response = requests.get(
            f"{BACKEND_URL}/manage/{telegram_id}",
            params={"ts":ts,
                    "sig":sig},
            timeout=10,
        )

        if response.status_code == 404:

            logger.info(
    "User %s has no connected accounts during upload",
    telegram_id,
)
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["active_message_id"],
                text=(
                    "❌ No Google accounts connected.\n\n"
                    "Use /connect to connect your Google Drive.\n"
                    "Use /help for more information."
                ),
            )
            return

        response.raise_for_status()

        accounts = response.json()["accounts"]

    except requests.RequestException:

        logger.exception(
    "Failed loading upload accounts for user %s",
    telegram_id,
)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data["active_message_id"],
            text="❌ Unable to connect to the server.",
        )
        return

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["active_message_id"],
        text="Select the Google account.",
        reply_markup=accounts_buttons(accounts),
    )