from database.collections import users_collections
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse
from services.telegram_service import send_telegram_message
from constants import (
    server_error_message,
    server_error_response,
    server_error_detail,
)
from utils.logger import logger


async def get_user(telegram_id: int):
    logger.info(
        "Loading user %s from database",
        telegram_id,
    )

    user = await users_collections.find_one(
        {"telegram_id": int(telegram_id)}
    )

    if user:
        logger.info(
            "User %s found",
            telegram_id,
        )
    else:
        logger.info(
            "User %s not found",
            telegram_id,
        )

    return user


async def get_accounts(
    telegram_id: int,
):
    logger.info(
        "Loading accounts for user %s",
        telegram_id,
    )

    user = await get_user(telegram_id)

    if user is None:
        logger.info(
            "User %s has no accounts",
            telegram_id,
        )
        return []

    accounts = [
        {
            "email": account["google"]["email"]
        }
        for account in user["accounts"]
    ]

    logger.info(
        "Loaded %s account(s) for user %s",
        len(accounts),
        telegram_id,
    )

    return accounts


async def get_account(
    telegram_id: int,
    email: str,
):
    logger.info(
        "Loading account %s for user %s",
        email,
        telegram_id,
    )

    user = await get_user(telegram_id)

    if user is None:
        logger.warning(
            "User %s not found while requesting account %s",
            telegram_id,
            email,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    account = next(
        (
            account
            for account in user["accounts"]
            if account["google"]["email"] == email
        ),
        None,
    )

    if account is None:
        logger.warning(
            "Account %s not found for user %s",
            email,
            telegram_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google account not found.",
        )

    logger.info(
        "Loaded account %s for user %s",
        email,
        telegram_id,
    )

    google = account["google"]

    return {
        "name": google["name"],
        "email": google["email"],
        "target_folder": google["target_folder"],
        "app_expires_at": google["app_expires_at"],
    }


def server_error_response(chat_id: int | None = None):
    logger.error(
        "Internal server error (chat_id=%s)",
        chat_id,
    )

    if chat_id is not None:
        sent = send_telegram_message(
            server_error_message,
            chat_id,
        )

        if sent:
            logger.info(
                "Server error message sent to Telegram user %s",
                chat_id,
            )
        else:
            logger.error(
                "Failed to send server error message to Telegram user %s",
                chat_id,
            )

    return HTMLResponse(
        server_error_response,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def server_error_exception(chat_id: int | None = None):
    logger.error(
        "Internal server exception (chat_id=%s)",
        chat_id,
    )

    if chat_id is not None:
        sent = send_telegram_message(
            server_error_message,
            chat_id,
        )

        if sent:
            logger.info(
                "Server error message sent to Telegram user %s",
                chat_id,
            )
        else:
            logger.error(
                "Failed to send server error message to Telegram user %s",
                chat_id,
            )

    return HTTPException(
        detail=server_error_detail,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def finish_with_message(
    telegram_id: int,
    telegram_message: str,
    success_html: str,
    telegram_failed_html: str,
    status_code: int,
):
    logger.info(
        "Sending Telegram completion message to user %s",
        telegram_id,
    )

    if send_telegram_message(
        telegram_message,
        telegram_id,
    ):
        logger.info(
            "Telegram message delivered to user %s",
            telegram_id,
        )

        return HTMLResponse(
            success_html,
            status_code=status_code,
        )

    logger.error(
        "Failed to deliver Telegram message to user %s",
        telegram_id,
    )

    return HTMLResponse(
        telegram_failed_html,
        status_code=status_code,
    )