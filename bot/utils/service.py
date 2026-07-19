from utils.logger import logger


async def clear_pending_actions(update, context):
    telegram_id = update.effective_user.id

    if (
        "upload" in context.user_data
        or "waiting_folder" in context.user_data
        or "active_message_id" in context.user_data
    ):
        logger.info(
            "Clearing pending actions for user %s",
            telegram_id,
        )

    # Upload
    context.user_data.pop("upload", None)

    # Manage
    context.user_data.pop("waiting_folder", None)
    context.user_data.pop("folder_email", None)

    # Delete active bot message
    message_id = context.user_data.pop("active_message_id", None)

    if message_id:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=message_id,
            )
        except Exception:
            logger.debug(
                "Unable to delete active message %s for user %s",
                message_id,
                telegram_id,
            )


async def cancel(update, context):
    telegram_id = update.effective_user.id

    upload = context.user_data.get("upload")

    # Upload flow
    if upload:

        if upload.get("uploading"):
            logger.info(
                "User %s attempted to cancel an upload already in progress",
                telegram_id,
            )

            await update.message.reply_text(
                "⏳ Upload is already in progress and cannot be cancelled."
            )
            return

        logger.info(
            "User %s cancelled upload flow",
            telegram_id,
        )

        await clear_pending_actions(update, context)

        await update.message.reply_text(
            "❌ Upload cancelled."
        )
        return

    # Change folder flow
    if context.user_data.get("waiting_folder"):

        logger.info(
            "User %s cancelled folder change",
            telegram_id,
        )

        await clear_pending_actions(update, context)

        await update.message.reply_text(
            "❌ Folder change cancelled."
        )
        return

    logger.info(
        "User %s used /cancel with no active operation",
        telegram_id,
    )

    await update.message.reply_text(
        "Nothing to cancel."
    )

async def unknown_folder_command(update, context):
    if context.user_data.get("waiting_folder"):
        logger.warning(
        "User %s attempted command '%s' while entering destination folder",
        update.effective_user.id,
        update.message.text,
    )
        
        logger.warning(
        "User %s attempted Unknown command '%s' while entering destination folder",
        update.effective_user.id,
        update.message.text,
    )
        await update.message.reply_text(
        """You are currently changing the destination folder.
Please enter a valid folder path.
        
Examples:
./Photos
./College/Notes
./Projects/Python

Send /cancel to cancel.
"""
   
    )
        

        return
    

    logger.warning(
        "User %s attempted Unknown command '%s'",
        update.effective_user.id,
        update.message.text,
    )

    await update.message.reply_text(
        """🤖 Unknown Command

I didn't recognize that command. 

👉 Use /help to see the list of available commands."""
   
    )