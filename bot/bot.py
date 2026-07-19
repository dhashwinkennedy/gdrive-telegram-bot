from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram import BotCommand
from utils.service import unknown_folder_command
from config import BOT_TOKEN
from telegram.request import HTTPXRequest
from handlers.verify import verify,verify_callback
from handlers.start import start
from handlers.connect import connect
from utils.logger import logger
from handlers.upload import (
    upload,
    upload_account_callback,
    receive_upload_file,
    rename_callback,
    keep_name_callback,
    receive_filename,
)
from handlers.manage import (
    manage,
    manage_account_callback,
    change_folder_callback,
    receive_folder,
)
from handlers.unlink import (
    unlink_callback,
    unlink_confirm_callback,
    unlink_cancel_callback,
)
from handlers.help import help
from utils.service import cancel
request = HTTPXRequest(
    connect_timeout=30,
    read_timeout=30,
    write_timeout=30,
)

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("connect", "Connect your Google Drive"),
        BotCommand("upload", "Upload a file"),
        BotCommand("manage", "Manage your Drive"),
        BotCommand("help", "Help"),
    ])


app = (
    Application.builder()
    .token(BOT_TOKEN)
    .request(request)
    .post_init(post_init)
    .build()
)


# ---------------- Commands ---------------- #

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("connect", connect))
app.add_handler(CommandHandler("upload", upload))
app.add_handler(CommandHandler("manage", manage))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(MessageHandler(filters.COMMAND, unknown_folder_command))
app.add_handler(CommandHandler("verify", verify))



# ---------------- Callback Queries ---------------- #

app.add_handler(
    CallbackQueryHandler(
        manage_account_callback,
        pattern=r"^manage:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        change_folder_callback,
        pattern=r"^folder:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        unlink_callback,
        pattern=r"^unlink:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        unlink_confirm_callback,
        pattern=r"^unlink_confirm:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        unlink_cancel_callback,
        pattern=r"^unlink_cancel:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        upload_account_callback,
        pattern=r"^upload:"
    )
)


app.add_handler(
    CallbackQueryHandler(
        verify_callback,
        pattern=r"^verify:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        rename_callback,
        pattern=r"^rename$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        keep_name_callback,
        pattern=r"^keep_name$"
    )
)



# ---------------- Documents ---------------- #

app.add_handler(
    MessageHandler(
        filters.ATTACHMENT,
        receive_upload_file
    )
)


# ---------------- Text Router ---------------- #

async def text_router(update, context):

    upload = context.user_data.get("upload")

    if upload and upload.get("waiting_filename"):
        return await receive_filename(update, context)

    if context.user_data.get("waiting_folder"):
        return await receive_folder(update, context)

    return


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_router,
    )
)


logger.info(
    "Bot started successfully. Waiting for updates..."
)

app.run_polling()
