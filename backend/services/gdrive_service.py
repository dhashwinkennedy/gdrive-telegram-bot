from urllib.parse import urlencode
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fastapi import Cookie,HTTPException,status
import requests
from utils.logger import logger

from datetime import datetime,timezone
from database.collections import users_collections

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    USER_INFO_URL,
    TOKEN_URL,
    GOOGLE_AUTH_URL,
    ACCESS_TOKEN_URL
)


def get_google_auth_url(state:str):
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "state":state,
        "scope": "openid email profile https://www.googleapis.com/auth/drive.file",

        # Needed to receive a refresh token
        "access_type": "offline",

        # Always show the consent screen while developing
        "prompt": "consent",
    }
    logger.debug("Generated Google OAuth URL")
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def get_drive_service(access_token: str):
    logger.debug("Creating Google Drive service")
    credentials = Credentials(token=access_token)

    service = build("drive", "v3", credentials=credentials)

    return service


def upload_to_drive(access_token:str, file,upload_name:str,target_folder_id):
    logger.info(
    "Uploading '%s' to Google Drive",
    upload_name,
)
    service = get_drive_service(access_token)
    media = MediaIoBaseUpload(
        file.file,
        mimetype=file.content_type or "application/octet-stream",
        resumable=True,
    )
    metadata = {
        "name" : upload_name,
        "parents": [target_folder_id],
    }
    try:
        uploaded = (
            service.files().create(
                body = metadata,
                media_body = media,
                fields = "id,name"
            ).execute()
        )

        logger.info(
        "Successfully uploaded '%s' (Drive ID: %s)",
        upload_name,
        uploaded["id"],
    )
        uploaded["driveLink"] = f"https://drive.google.com/file/d/{uploaded['id']}/view"
        return uploaded
    except Exception:
        logger.exception(
            "Failed to upload '%s' to Google Drive",
            upload_name,
        )
        raise





def exchange_code_for_tokens(code: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    logger.info(
    "Exchanging authorization code for Google tokens"
)
    try:
        response = requests.post(TOKEN_URL,data=data)
        response.raise_for_status()
        logger.info("Successfully exchanged authorization code")

        return response.json()
    except Exception:
        logger.exception("Failed to exchange authorization code")
        raise


def get_google_tokens(
    access_token: str | None = Cookie(default=None),
    refresh_token: str | None = Cookie(default=None),
):
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Please connect your Google account first."
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }




def get_google_user_info(token ):
    try:
        response = requests.get(
            USER_INFO_URL,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        response.raise_for_status()

        userinfo = response.json()

        logger.info(
            "Fetched Google profile for %s",
            userinfo.get("email"),
        )

        return userinfo
    

    except Exception:
        logger.exception("Failed to fetch Google user profile")
        raise


def refresh_access_token(refresh_token: str):
    data = {
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    "refresh_token": refresh_token,
    "grant_type": "refresh_token"
}
    logger.info(
    "Refreshing Google access token"
)
    try:
        response = requests.post(ACCESS_TOKEN_URL,data=data)
        response.raise_for_status()  # Raises an exception if Google returns an error
        logger.info(
        "Google access token refreshed successfully"
)
    except:
        logger.exception(
    "Failed to refresh Google access token"
)   
        raise

    return response.json()


async def update_access_token(
    telegram_id: int,
    email: str,
    access_token: str
):
    logger.info(
    "Updating access token for user %s (%s)",
    telegram_id,
    email,
)
    await users_collections.update_one(
        {
            "telegram_id":int(telegram_id),
            "accounts.google.email":email
        },
        {"$set" :{
            "accounts.$.google.access_token":access_token,
            "updated_at": datetime.now(timezone.utc),
        }}
    )
    logger.info(
    "Stored refreshed access token for %s",
    email,
)


async def get_valid_access_token(
    telegram_id: int,
    email: str
):
    
    logger.info(
    "Retrieving valid access token for user %s (%s)",
    telegram_id,
    email,
)
    user = await users_collections.find_one(
    {"telegram_id": int(telegram_id)}
)

    if user is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    account = next(
        (
            acc
            for acc in user["accounts"]
            if acc["google"]["email"] == email
        ),
        None
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found."
        )

    refresh_token = account["google"]["refresh_token"]

    access_response = refresh_access_token(refresh_token)
    access_token = access_response["access_token"]
    await update_access_token(telegram_id,email,access_token)
    logger.info(
    "Access token updated for %s",
    email,
)
    return access_token



def get_target_folder_id(
    access_token: str,
    folder_path: str,
    telegram_id:int
) -> str:
    logger.info(
    "Resolving Drive folder path '%s'",
    folder_path,
)
    # ---------- Validate ----------
    if not folder_path.startswith("./"):
        logger.warning(
        "Invalid folder path received from user %s: %s",
        telegram_id,
        folder_path,
    )
        raise HTTPException(
            status_code=400,
            detail="Folder path must start with './'"
        )

    if ".." in folder_path:
        logger.warning(
        "Invalid folder path received from user %s: %s",
        telegram_id,
        folder_path,
    )
        raise HTTPException(
            status_code=400,
            detail="Invalid folder path."
        )

    if "\\" in folder_path:
        logger.warning(
        "Invalid folder path received from user %s: %s",
        telegram_id,
        folder_path,
    )
        raise HTTPException(
            status_code=400,
            detail="Use '/' instead of '\\'."
        )

    # remove "./" and trailing "/"
    folders = [
        f for f in folder_path[2:].strip("/").split("/")
        if f
    ]

    credentials = Credentials(access_token)
    service = build("drive", "v3", credentials=credentials)

    parent_id = "root"

    for folder in folders:

        query = (
            f"'{parent_id}' in parents and "
            f"name='{folder}' and "
            "mimeType='application/vnd.google-apps.folder' and "
            "trashed=false"
        )

        result = service.files().list(
            q=query,
            fields="files(id,name)"
        ).execute()

        files = result.get("files", [])

        if files:
            logger.info(
    "Found existing folder '%s'",
    folder,
)
            parent_id = files[0]["id"]

        else:
            metadata = {
                "name": folder,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            logger.info(
    "Creating Google Drive folder '%s'",
    folder,
)
            created = service.files().create(
                body=metadata,
                fields="id"
            ).execute()

            parent_id = created["id"]
            logger.info(
    "Created folder '%s' (ID: %s)",
    folder,
    parent_id,
)

    logger.info(
    "Resolved folder '%s' -> %s",
    folder_path,
    parent_id,
)
    return parent_id


