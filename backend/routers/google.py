from fastapi import APIRouter,Request,HTTPException,File,UploadFile,status,Response
from fastapi.responses import RedirectResponse
from googleapiclient.errors import HttpError

from datetime import datetime,timezone
from utils.logger import logger
from services.gdrive_service import (
    exchange_code_for_tokens,
    get_google_user_info,
    get_google_auth_url,
    get_valid_access_token,
    upload_to_drive)
from services.user_service import (add_account,
                                   create_user,
                                   update_verify_token,
                                   recreate_target_folder)
from services.server_service import (get_user,server_error_response,
                                     server_error_exception,
                                     finish_with_message)
from services.telegram_service import send_telegram_message
from utils.security import verify_signature
from constants import (
    verified_message,
    connected_message,
    account_mismatch_message,
    not_found_message,
    verified_telegram_failed_response,
    connected_response,
    connected_telegram_failed_response,
    verified_response,
    account_mismatch_telegram_error_response,
    account_mismatch_response,
    not_found_detail,
    expired_detail,
    expired_telegram_message,
    already_connected_response,
    already_connected_telegram_failed_response,
    already_connected_telegram_response
    )


router = APIRouter(
    prefix="/google",
    tags=["google"]
)


@router.get("/login")
async def google_login(telegram_id: int,ts:str,sig:str):
    logger.info(
    "[GET /login] Google login requested by user %s",
    telegram_id,
)
    if not verify_signature(
    telegram_id,
    ts,
    sig,
):
        logger.warning(
    "[GET /login] Invalid login signature for user %s",
    telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )
    try:
        url = get_google_auth_url(f"connect|{telegram_id}")
        return RedirectResponse(url)

    except Exception:

        logger.exception(
            "[GET /login] Failed to start Google login for user %s",
            telegram_id,
        )
        return server_error_response(telegram_id)



@router.get("/callback")
async def google_callback(request: Request, response: Response):

    code = request.query_params.get("code")
    state = request.query_params.get("state")
    logger.info(
    "[GET /callback] Received Google OAuth callback ",
)
    try:
        tokens = exchange_code_for_tokens(code)
        googleuserinfo = get_google_user_info(
            tokens["access_token"]
        )
    except Exception:

        logger.exception(
            "[GET /callback] Failed to exchange Google OAuth callback"
        )

        return server_error_response(None)

    name = googleuserinfo["name"]
    email = googleuserinfo["email"]

    parts = state.split("|")
    flow = parts[0]

    # =====================================================
    # VERIFY FLOW
    # =====================================================

    if flow == "verify":


        telegram_id = int(parts[1])
        expected_email = parts[2]
        logger.info(
            "[GET /callback] Verification callback for user %s (%s)",
            telegram_id,
            expected_email,
        )

        if email != expected_email:
            logger.warning(
            "[GET /callback] Verification email mismatch. Expected %s, got %s",
            expected_email,
            email,
        )

            return finish_with_message(
                telegram_id=telegram_id,
                telegram_message=account_mismatch_message,
                success_html=account_mismatch_response,
                telegram_failed_html=account_mismatch_telegram_error_response,
                status_code=status.HTTP_409_CONFLICT,
            )

        try:
            logger.info(
                "[GET /callback] Updating verification for %s",
                expected_email,
            )
            await update_verify_token(
                telegram_id,
                expected_email,
                tokens,
            )
        except Exception:
            logger.exception(
                "[GET /callback] Verification update failed for %s",
                expected_email,
            )
            return server_error_response(telegram_id)
        

        logger.info(
    "[GET /callback] Verification completed for %s",
    expected_email,
)

        return finish_with_message(
            telegram_id=telegram_id,
            telegram_message=verified_message(name, email),
            success_html=verified_response,
            telegram_failed_html=verified_telegram_failed_response,
            status_code=status.HTTP_200_OK,
        )

    # =====================================================
    # CONNECT FLOW
    # =====================================================

    telegram_id = int(parts[1])
    logger.info(
    "[GET /callback] Connection callback for user %s",
    telegram_id,
)

    try:
        user = await get_user(telegram_id)
    except Exception:
        return server_error_response(telegram_id)

    # ---------------- First Account ---------------- #

    if user is None:    
        logger.info(
    "[GET /callback] Creating first Google account for user %s",
    telegram_id,
)

        try:
            await create_user(
                telegram_id,
                email,
                name,
                token=tokens,
            )
        except Exception:
            logger.exception(
        "[GET /callback] Failed to create first account for user %s",
        telegram_id,
    )
            return server_error_response(telegram_id)
        

        logger.info(
            "[GET /callback] Google account connected successfully for user %s (%s)",
            telegram_id,
            email,
        )

        return finish_with_message(
            telegram_id=telegram_id,
            telegram_message=connected_message(name, email),
            success_html=connected_response,
            telegram_failed_html=connected_telegram_failed_response,
            status_code=status.HTTP_201_CREATED,
        )

    # ---------------- Existing Account ---------------- #

    exists = any(
        account["google"]["email"] == email
        for account in user["accounts"]
    )

    if exists:

        logger.info(
            "[GET /callback] User %s attempted to reconnect existing account %s",
            telegram_id,
            email,
        )

        return finish_with_message(
        telegram_id=telegram_id,
        telegram_message=already_connected_telegram_response,
        success_html=already_connected_response,
        telegram_failed_html=already_connected_telegram_failed_response,
        status_code=status.HTTP_200_OK,
    )

    # ---------------- Add New Account ---------------- #

    try:
        logger.info(
    "[GET /callback] Adding additional Google account %s for user %s",
    email,
    telegram_id,
)
        await add_account(
            telegram_id,
            email,
            name,
            token=tokens,
        )
    except Exception:

        logger.exception(
        "[GET /callback] Failed to create first account for user %s",
        telegram_id,
    )
        return server_error_response(telegram_id)
    
    logger.info(
    "[GET /callback] Google account connected successfully for user %s (%s)",
    telegram_id,
    email,
)

    return finish_with_message(
        telegram_id=telegram_id,
        telegram_message=connected_message(name, email),
        success_html=connected_response,
        telegram_failed_html=connected_telegram_failed_response,
        status_code=status.HTTP_201_CREATED,
    )

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def upload_file(
    telegram_id:int,
    email:str,
    ts:str,
    sig:str,
    file: UploadFile = File(...),
    filename: str | None = None,
    
):
    
    logger.info(
    "[POST /upload] Upload request from user %s (%s)",
    telegram_id,
    email,
)
    if not verify_signature(
    telegram_id,
    ts,
    sig,
):
        logger.warning(
    "[POST /upload]Invalid upload signature from user %s",
    telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )
    try:
        user = await get_user(telegram_id)
    except Exception:
        return server_error_response(telegram_id)
    if user is None:
        logger.warning(
    "[POST /upload] Upload requested by unknown user %s",
    telegram_id,
)
        send_telegram_message(not_found_message,telegram_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=not_found_detail)
    
    
 
    
    account = next(
    (
        acc
        for acc in user["accounts"]
        if acc["google"]["email"] == email
    ),
    None
)   
    if account is None:
        logger.warning(
    "[POST /upload]Upload requested for missing account %s by user %s",
    email,
    telegram_id,
)
        send_telegram_message(not_found_message,telegram_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=not_found_detail)
    target_id = account["google"]["target_folder_id"]

    
    if account["google"]["app_expires_at"] < datetime.now(timezone.utc).replace(tzinfo=None):
        logger.warning(
    "[POST /upload]Upload rejected because account %s expired",
    email,
)
        send_telegram_message(expired_telegram_message,telegram_id)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=expired_detail
        )
    try:
        access_token = await get_valid_access_token(telegram_id,email)
        upload_name = filename or file.filename

        try:
            logger.info(
        "[POST /upload] Uploading '%s' for user %s",
        filename or file.filename,
        telegram_id,
    )
            uploaded = upload_to_drive(access_token,file,upload_name,target_id)

            return uploaded
        except HttpError as e:
            if e.resp.status != 404:
                raise

            logger.warning(
                "[POST /upload] Drive folder missing. Recreating folder for %s",
                email,
            )
            new_folder_id = await recreate_target_folder(telegram_id,
            email,account["google"]["target_folder"],access_token
        )


            uploaded = upload_to_drive(
                access_token,
                file,
                upload_name,
                new_folder_id,
            )

        logger.info(
            "[POST /upload] Upload Request completed for user %s",
            telegram_id,
        )

        return uploaded

    except Exception:
        logger.exception(
            "[POST /upload] Upload failed for user %s (%s)",
            telegram_id,
            email,
        )
        raise server_error_exception(telegram_id)
    

