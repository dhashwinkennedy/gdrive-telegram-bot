import os
import time
import hmac
import hashlib

BOT_SECRET = os.getenv("BOT_HMAC_SECRET")


def verify_signature(
    tg_id: int,
    timestamp: str,
    signature: str,
):
    # Expire after 5 minutes
    if abs(time.time() - int(timestamp)) > 300:
        return False

    payload = f"{tg_id}:{timestamp}"

    expected = hmac.new(
        BOT_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)