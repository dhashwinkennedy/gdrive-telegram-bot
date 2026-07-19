def connected_message(name,email):
    connected_message= f"""✅ Google account Connected successfully!

👤 {name}
📧 {email}

status code: 201"""
    return connected_message
    
def verified_message(name,email):
    verified_message = f"""✅ Google account Verified successfully!

👤 {name}
📧 {email}

status code: 200

            """
    return verified_message


account_mismatch_message = """❌ Account Mismatch Detected

The Google account you selected does not match the one requesting verification. 

Please try again using the correct account.
status code: 409"""

server_error_message = """⚠️ Internal Server Error

Something went wrong on our server while processing your request. 

Please try again later or restart the process from Telegram.

status code: 500"""

connected_response = """
            <h2>✅ Google Drive Connected Successfully</h2>

            <p>You can close this page and return to Telegram.</p>

            <status_code 201:
            """
verified_response = """
        <h2>✅ Account Verified Successfully</h2>


        <p>You can close this page and return to Telegram.</p>

        <p>status code : 200<p>
        """
account_mismatch_response= """
    <h2>❌ Wrong Google account selected.</h2>

    <p>Please close this page and return to Telegram.</p>

    <p>status code : 409<p>

"""

server_error_response = """
        <h2>⚠️ Internal Server Error</h2>

        <p>Something went wrong on our end. Please close this page and try again in Telegram.</p>

        <p>status code : 500</p>
        """


account_mismatch_telegram_error_response = """
    <h2>❌ Wrong Google account selected.</h2>

    <p>Please close this page and return to Telegram. (Note: We couldn't send the error message to Telegram due to a server issue).</p>

    <p>status code : 409</p>
"""

verified_telegram_failed_response = """
        <h2>✅ Account Verified Successfully</h2>

        <p>You can close this page and return to Telegram.</p>

        <p>⚠️ <i>Note: We verified your account, but failed to send the confirmation message in Telegram due to a server issue.</i></p>

        <p>status code : 200</p>
        """



connected_telegram_failed_response = """
            <h2>✅ Google Drive Connected Successfully</h2>

            <p>You can close this page and return to Telegram.</p>

            <p>⚠️ <i>Note: Connection succeeded, but we couldn't send the confirmation message in Telegram due to a server issue.</i></p>

            <p>status code : 201</p>
            """

not_found_detail = {
                "status": "error",
                "code": 404,
                "error_type": "NOT_FOUND",
                "message": "The requested verification session or user record could not be found."
            }

not_found_message = """⚠️ Resource Not Found

We couldn't find the requested session or verification record. It may have expired or is invalid.

Please restart the process from Telegram.
status code: 404"""


server_error_detail = detail={
                "status": "error",
                "code": 500,
                "error_type": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server-side error occurred while processing your request."
            }

expired_detail={
        "status": "error",
        "code": 410,
        "error_type": "SESSION_EXPIRED",
        "message": "Your verification link or connection session has expired.",
        "action_required": "Send /connect or /verify in Telegram to generate a new link."
    }
expired_telegram_message = """⚠️ Session Expired

Your verification session has timed out for security reasons.

Please send /connect or /verify to reconnect and try again.

status code: 410"""

already_connected_response = """
    <h2>⚠️ Already Already Connected To This Telegram User</h2>

    <p>This account is already linked to an active session. Please close this page and return to Telegram.</p>

    <p>status code : 200</p>
"""

already_connected_telegram_failed_response = """
    <h2>⚠️ Already Already Connected To This Telegram User</h2>

    <p>This account is already linked to an active session. Please close this page and return to Telegram.</p>

    <p>⚠️ <i>Note: Connection succeeded, but we couldn't send the confirmation message in Telegram due to a server issue.</i></p>


    <p>status code : 200</p>
"""

already_connected_telegram_response = """⚠️ Account Already Connected

This account is already linked to an active session. 

👉 Use /manage to view and manage your current account status.
👉 Use /connect to disconnect and link a new account."""