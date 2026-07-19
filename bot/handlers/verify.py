from utils.service import clear_pending_actions
import requests
from keyboards.verify import accounts_buttons,verify_button
from utils.security import create_signature
from config import BACKEND_URL
async def verify(update,context):
    await clear_pending_actions(update,context)

    telegram_id = update.effective_user.id
    try:
        ts ,sig = create_signature(telegram_id)
        response = requests.get(
            f"{BACKEND_URL}/manage/{telegram_id}",
            params={
                "ts":ts,
                "sig":sig
            },
            timeout=10,
        )

        response.raise_for_status()

        accounts = response.json()["accounts"]

    except requests.RequestException:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data["active_message_id"],
            text="❌ Unable to connect to the server.",
        )
        return

    await update.message.reply_text(
        "Select the account to verify.",
        reply_markup=accounts_buttons(accounts)
    )


async def verify_callback(update, context):
    query = update.callback_query
    await query.answer()

    email = query.data.split(":", 1)[1]


    telegram_id = update.effective_user.id
    

    await query.edit_message_text(
        "Click below to verify.",
        reply_markup = verify_button(telegram_id,email)
    )

   