from database.collections import users_collections
from datetime import datetime,timezone,timedelta
from services.gdrive_service import get_valid_access_token,get_target_folder_id
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from utils.logger import logger

async def create_user(
    telegram_id:int,
    email:str,
    name:str,
    token:dict

):
    
    logger.info(
    "Creating new user %s with Google account %s",
    telegram_id,
    email,
)
    target_id = get_target_folder_id(token["access_token"],"./gdrive_bot",telegram_id)
    try:

        await users_collections.insert_one(
            {
                "telegram_id": int(telegram_id),
                "created_at":datetime.now(timezone.utc),
                "updated_at" : datetime.now(timezone.utc),
                "accounts":[
                    {
                    "google": {
                        "name":name,
                        "email": email,
                        "access_token":token["access_token"],
                        "refresh_token":token["refresh_token"],
                        "target_folder":"./gdrive_bot",
                        "target_folder_id":target_id,
                        "app_expires_at" : datetime.now(timezone.utc) + timedelta(days=15),
                        "scope":token["scope"],
                        "token_type":token["token_type"],
                    },
                    
                },
                ]
            },
            
        )
    except Exception:
        logger.exception(
            "Failed to create user %s",
            telegram_id,
        )
        raise
    logger.info(
    "Successfully created user %s",
    telegram_id,
)


async def add_account(
    telegram_id:int,
    email:str,
    name:str,
    token:dict

):
    
    logger.info(
    "Adding Google account %s to user %s",
    email,
    telegram_id,
)
    target_id = get_target_folder_id(token["access_token"],"./gdrive_bot",telegram_id)
    
    
    account = {
            
                "google": {
        
                    "name":name,
                    "email": email,
                    "access_token":token["access_token"],
                    "refresh_token":token["refresh_token"],
                    "target_folder":"./gdrive_bot",
                    "target_folder_id":target_id,
                    "app_expires_at": datetime.now(timezone.utc) + timedelta(days=15),
                    "scope":token["scope"],
                    "token_type":token["token_type"],
                },
                
            }
    try:
        result = await users_collections.update_one(
            {"telegram_id": int(telegram_id)},
            {
            "$push": {
                "accounts": account
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        )
    except Exception:
        logger.exception(
            "Failed to add account %s for user %s",
            email,
            telegram_id,
        )
        raise

    if result.modified_count == 0:
        logger.warning(
            "add account affected 0 documents for user %s (%s)",
            telegram_id,
            email,
        )
    else:
        logger.info(
    "Successfully added Google account %s to user %s",
    email,
    telegram_id,
)



async def change_target_folder(telegram_id:int,email:str,path:str):

    logger.info(
    "Changing target folder for user %s (%s) -> %s",
    telegram_id,
    email,
    path,
)
    token = await get_valid_access_token(int(telegram_id),email)
    target_id = get_target_folder_id(token,path,telegram_id)
    try:
        result = await users_collections.update_one(
            {
                "telegram_id":int(telegram_id),
                "accounts.google.email":email
            },
            {"$set" :{
                "accounts.$.google.target_folder_id":target_id,
                "accounts.$.google.target_folder":path,
                "updated_at": datetime.now(timezone.utc),
            }})
    except Exception:
        logger.exception(
            "Failed to Update Target folder %s for email %s for user %s",
            path,
            email,
            telegram_id,
        )
        raise
    
    if result.modified_count == 0:
        logger.warning(
            "Target folder update affected 0 documents for user %s (%s)",
            telegram_id,
            email,
        )
    else:
    
        logger.info(
        "Target folder updated successfully for user %s (%s)",
        telegram_id,
        email,
    )

async def recreate_target_folder(telegram_id:int,email:str,path:str,token):
    logger.info(
    "Recreating target folder '%s' for user %s (%s)",
    path,
    telegram_id,
    email,
)
    target_id = get_target_folder_id(token,path,telegram_id)
    try:
        result = await users_collections.update_one(
            {
                "telegram_id":int(telegram_id),
                "accounts.google.email":email
            },
            {"$set" :{
                "accounts.$.google.target_folder_id":target_id,
                "accounts.$.google.target_folder":path,
                "updated_at": datetime.now(timezone.utc),
            }})
    except Exception:
        logger.exception(
            "Failed to recreate target folder '%s' for %s (%s)",
            path,
            telegram_id,
            email,
        )
        raise


    if result.modified_count == 0:
        logger.warning(
            "Target folder update affected 0 documents for user %s (%s)",
            telegram_id,
            email,
        )
        raise HTTPException(
        status_code=500,
        detail="Failed to update target folder."
    )
    else:
        logger.info(
        "Created new target folder ID %s for user %s (%s)",
        target_id,
        telegram_id,
        email,
    )
        return target_id


async def remove_account(
    telegram_id: int,
    email: str
):
    
    logger.info(
    "Removing Google account %s from user %s",
    email,
    telegram_id,
)
    try:
        result = await users_collections.update_one(
            {
                "telegram_id": telegram_id
            },
            {
                "$pull": {
                    "accounts": {
                        "google.email": email
                    }
                },
                "$set": {
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
    except Exception:
        logger.exception(
            "Failed to remove account %s for user %s",
            email,
            telegram_id,
        )
        raise

    if result.modified_count == 0:

        logger.warning(
    "Attempted to remove non-existent account %s from user %s",
    email,
    telegram_id,
)
        raise HTTPException(
            status_code=404,
            detail="Google account not found."
        )
    
    logger.info(
    "Successfully removed Google account %s from user %s",
    email,
    telegram_id,
)
    


async def update_verify_token(
    telegram_id: int,
    email: str,
    token: dict,
):
    
    logger.info(
    "Updating verification tokens for user %s (%s)",
    telegram_id,
    email,
)
    update = {
        "accounts.$.google.access_token": token["access_token"],
        "accounts.$.google.scope": token["scope"],
        "accounts.$.google.token_type": token["token_type"],
        "accounts.$.google.app_expires_at":
            datetime.now(timezone.utc) + timedelta(days=10),

        "updated_at": datetime.now(timezone.utc),
    }

    # Google doesn't always return a refresh token
    if token.get("refresh_token"):
        update["accounts.$.google.refresh_token"] = token["refresh_token"]
    try:
        result = await users_collections.update_one(
            {
                "telegram_id": int(telegram_id),
                "accounts.google.email": email,
            },
            {
                "$set": update
            }
        )
    except Exception:
        logger.exception(
            "Failed to update verify token for account %s for user %s",
            email,
            telegram_id,
        )
        raise
    if result.modified_count == 0:
        logger.warning(
            "Verify token update affected 0 documents for user %s (%s)",
            telegram_id,
            email,
        )
    else:

        logger.info(
        "Verification token updated successfully for user %s (%s)",
        telegram_id,
        email,
    )