import time
import hmac
import hashlib
import os


BOT_SECRET = os.getenv("BOT_HMAC_SECRET")


def create_signature(tg_id: int):
    timestamp = str(int(time.time()))

    payload = f"{tg_id}:{timestamp}"

    signature = hmac.new(
        BOT_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return timestamp, signature