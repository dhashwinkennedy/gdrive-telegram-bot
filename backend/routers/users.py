from fastapi import APIRouter,HTTPException,status
from fastapi.responses import RedirectResponse
from services.user_service import change_target_folder,remove_account
from pydantic import BaseModel
from services.gdrive_service import get_google_auth_url
from services.server_service import (
    server_error_exception,
    get_accounts,
    get_account)
from utils.security import verify_signature
from utils.logger import logger

router = APIRouter(
    tags=["users"]
)

class ChangeFolderRequest(BaseModel):
    telegram_id: int
    email: str
    target_folder: str
    ts:str
    sig:str

class RemoveAccountRequest(BaseModel):
    telegram_id: int
    email: str
    ts:str
    sig:str

class VerifyRequest(BaseModel):
    telegram_id: int
    email: str
    ts:str
    sig:str






@router.get("/manage/{telegram_id}",status_code=status.HTTP_200_OK)
async def manage_accounts(
    telegram_id: int,
    ts: str,
    sig: str,
):
    
    logger.info(
    "[GET /manage] Manage accounts requested by user %s",
    telegram_id,
)

    if not verify_signature(
        telegram_id,
        ts,
        sig,
    ):
        logger.warning(
    "[GET /manage] Invalid signature while retrieving accounts for user %s",
    telegram_id,
)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid request",
        )

    try:
        accounts = await get_accounts(telegram_id)
    except Exception:
        logger.exception(
        "[GET /manage] Failed to retrieve accounts for user %s",
        telegram_id,
    )
        raise server_error_exception(telegram_id)

    if not accounts:
        logger.info(
    "[GET /manage] No connected accounts for user %s",
    telegram_id,
)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Google accounts connected.",
        )

    logger.info(
    "[GET /manage] Returned %d account(s) for user %s",
    len(accounts),
    telegram_id,
)
    return {
        "accounts": accounts
    }

@router.get("/manage/{telegram_id}/{email}",status_code=status.HTTP_200_OK)
async def manage_account(
    telegram_id: int,
    email: str,
    ts:str,
    sig:str
):
    logger.info(
    "[GET /manage] Account details requested for %s by user %s",
    email,
    telegram_id,
)
    if not verify_signature(
    telegram_id,
    ts,
    sig,
):
        logger.warning(
    "[GET /manage] Invalid signature while retrieving account %s for user %s",
    email,
    telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )
    try:
        account = await get_account(
            telegram_id,
            email,
        )

        logger.info(
    "[GET /manage] Returned account details for %s",
    email,
)
        return {
    "message": "Account details retrieved successfully.",
    "account": account
}
    except Exception:
        logger.exception(
        "[GET /manage] Failed to retrieve account %s for user %s",
        email,
        telegram_id,
    )
        raise server_error_exception(telegram_id)
    


@router.patch("/manage/folder",status_code=status.HTTP_200_OK)
async def update_target_folder(
    request: ChangeFolderRequest,

):
    logger.info(
    "[PATCH /manage/folder] Folder update requested by user %s (%s) -> %s",
    request.telegram_id,
    request.email,
    request.target_folder,
)
    if not verify_signature(
    request.telegram_id,
    request.ts,
    request.sig,
):
        logger.warning(
    "[PATCH /manage/folder] Invalid signature while updating folder for user %s",
    request.telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )
    try:
        await change_target_folder(
            request.telegram_id,request.email,request.target_folder
        )
    except HTTPException:
        # Preserve 400/404/etc.
        raise

    except Exception:

        raise server_error_exception(request.telegram_id) 
    
    logger.info(
    "[PATCH /manage/folder] Folder updated successfully for user %s (%s)",
    request.telegram_id,
    request.email,
)
    return{
        "message" : "Target folder updated successfully"
    }

@router.delete("/manage/account",status_code=status.HTTP_200_OK)
async def delete_account(
    request: RemoveAccountRequest,

):
    logger.info(
    "[DELETE /manage/account] Account removal requested for %s by user %s",
    request.email,
    request.telegram_id,
)
    if not verify_signature(
    request.telegram_id,
    request.ts,
    request.sig,
):
        logger.warning(
    "[DELETE /manage/account] Invalid signature while removing account for user %s",
    request.telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )  
    try:
        await remove_account(
            request.telegram_id,
            request.email
        )
    except Exception:
        logger.exception(
        "[DELETE /manage/account] Failed to remove account %s for user %s",
        request.email,
        request.telegram_id,
    )
        raise server_error_exception(request.telegram_id)
    
    logger.info(
    "[DELETE /manage/account] Account %s removed successfully for user %s",
    request.email,
    request.telegram_id,
)

    return {
        "message": "Google account removed successfully."
    }



@router.get("/verify",status_code=status.HTTP_200_OK)
async def verify_account(
    telegram_id:int,
    email:str,
    ts:str,
    sig:str

    ):
    logger.info(
    "[GET /verify] Verification requested by user %s for account %s",
    telegram_id,
    email,
)
    if not verify_signature(
    telegram_id,
    ts,
    sig,
):
        logger.warning(
    "[GET /verify] Invalid signature during verification request for user %s",
    telegram_id,
)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid request",
    )
    state = f"verify|{telegram_id}|{email}"

    try:
        auth_url = get_google_auth_url(state)
        logger.info(
    "[GET /verify] Generated verification URL for user %s (%s)",
    telegram_id,
    email,
)
        return RedirectResponse(auth_url)
    except Exception:
        logger.exception(
        "[GET /verify] Failed to generate verification URL for user %s (%s)",
        telegram_id,
        email,
    )
        raise server_error_exception(telegram_id)


