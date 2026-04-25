"""
Email OTP verification module
Sends OTP codes via Resend HTTP API asynchronously
"""
import random
import requests
from flask import current_app
import logging
import threading

logger = logging.getLogger(__name__)

_app = None

def set_app(app):
    """Set the Flask app for use in background threads"""
    global _app
    _app = app


def generate_otp(length=6):
    """Generate a random OTP code"""
    otp = ""
    for i in range(length):
        otp += str(random.randint(0, 9))
    return otp


def _send_otp_email_sync(to_email, otp):
    """
    Internal function to actually send email via Resend HTTP API (blocking)
    Runs in background thread with proper Flask app context
    """
    try:
        if not _app:
            print("[EMAIL BG ERROR] Flask app context not available!")
            return False

        with _app.app_context():
            api_key = current_app.config.get('RESEND_API_KEY')
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <onboarding@ship-ai.app>')

            if not api_key:
                print("[EMAIL BG ERROR] RESEND_API_KEY not configured")
                return False

            html_body = f'''
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0d6efd;">Email Verification - ShipAI</h2>
            <p>Thank you for signing up! Use the following code to verify your email:</p>
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="color: #0d6efd; letter-spacing: 2px; margin: 0; font-size: 36px;">{otp}</h1>
            </div>
            <p>This code will expire in <strong>10 minutes</strong>.</p>
            <p style="color: #666; font-size: 14px;">If you didn't create this account, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">Best regards,<br>The ShipAI Team</p>
        </div>
    </body>
</html>
'''

            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': sender,
                    'to': [to_email],
                    'subject': 'Your ShipAI Email Verification Code',
                    'html': html_body,
                    'text': f'Your ShipAI verification code is: {otp}\n\nThis code will expire in 10 minutes.',
                },
                timeout=10
            )

            if response.status_code in (200, 201):
                print(f"[EMAIL BG SUCCESS] Email sent to {to_email}")
                logger.info(f'OTP email sent successfully to {to_email}')
                return True
            else:
                print(f"[EMAIL BG ERROR] Resend API error: {response.status_code} {response.text}")
                logger.error(f'Resend API error: {response.status_code} {response.text}')
                return False

    except Exception as e:
        print(f"[EMAIL BG ERROR] {e}")
        logger.error(f'Error sending OTP email: {e}')
        return False


def send_otp_email(to_email, otp):
    """
    Send OTP verification email ASYNCHRONOUSLY in background thread
    Returns immediately, email sends in background.
    """
    try:
        print(f"[ASYNC SEND] Scheduling OTP email to {to_email}")
        thread = threading.Thread(
            target=_send_otp_email_sync,
            args=(to_email, otp),
            daemon=True,
            name=f"EmailThread-{to_email}"
        )
        thread.start()
        print(f"[ASYNC SEND] Email thread started")
        return True
    except Exception as e:
        print(f"[ASYNC ERROR] {e}")
        logger.error(f'Error starting email thread: {e}')
        return False