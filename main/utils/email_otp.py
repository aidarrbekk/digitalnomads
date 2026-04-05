"""
Email OTP verification module
Generates and sends OTP codes via email ASYNCHRONOUSLY
"""
import random
import smtplib
from email.message import EmailMessage
from flask import current_app
import logging
import threading

logger = logging.getLogger(__name__)

# Global app reference for threading
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
    Internal function to actually send email (blocking)
    Runs in background thread with proper Flask app context
    """
    try:
        print("\n" + "="*70)
        print("[OTP EMAIL BACKGROUND] ⏳ Starting email send in background thread")
        print("="*70)
        
        # Use app context from global reference
        if not _app:
            print("[EMAIL BG ERROR] Flask app context not available!")
            return False
            
        with _app.app_context():
            # Get mail config
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_port = current_app.config.get('MAIL_PORT', 587)
            mail_user = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <noreply@shipai.com>')

            print(f"[EMAIL BG] To: {to_email}, OTP: {otp}")

            if not mail_server or not mail_port or not mail_user or not mail_password:
                print("[EMAIL BG ERROR] Invalid mail config")
                return False

            # Create email message
            msg = EmailMessage()
            msg['Subject'] = 'Your ShipAI Email Verification Code'
            msg['From'] = mail_sender
            msg['To'] = to_email

            html_body = f'''
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0d6efd;">Email Verification - ShipAI</h2>
            
            <p>Thank you for signing up on ShipAI! To verify your email address, please use the following verification code:</p>
            
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="color: #0d6efd; letter-spacing: 2px; margin: 0; font-size: 36px;">
                    {otp}
                </h1>
            </div>
            
            <p>This code will expire in <strong>10 minutes</strong>.</p>
            
            <p style="color: #666; font-size: 14px;">
                If you didn't create this account, please ignore this email.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 12px; color: #666;">
                Best regards,<br>
                The ShipAI Team
            </p>
        </div>
    </body>
</html>
'''

            msg.set_content(f"Your ShipAI verification code is: {otp}\n\nThis code will expire in 10 minutes.", subtype='plain')
            msg.add_alternative(html_body, subtype='html')

            # Connect and send
            print("[EMAIL BG] Connecting to SMTP...")
            server = smtplib.SMTP(mail_server, mail_port, timeout=10)
            
            if mail_use_tls:
                try:
                    server.starttls()
                    print("[EMAIL BG] TLS started")
                except Exception as e:
                    print(f"[EMAIL BG] TLS warning: {e}")

            print("[EMAIL BG] Authenticating...")
            server.login(mail_user, mail_password)
            
            print("[EMAIL BG] Sending...")
            server.send_message(msg)
            server.quit()
            
            print(f"[EMAIL BG SUCCESS] ✅ Email sent to {to_email}")
            logger.info(f'OTP email sent successfully to {to_email}')
            print("="*70 + "\n")
            return True

    except Exception as e:
        print(f"[EMAIL BG ERROR] ❌ {e}")
        logger.error(f'Error sending OTP email: {e}')
        print("="*70 + "\n")
        return False


def send_otp_email(to_email, otp):
    """
    Send OTP verification email ASYNCHRONOUSLY in background thread
    
    🚀 KEY FEATURE: This function returns IMMEDIATELY and sends email in background.
    User experiences instant page redirect without waiting for email!
    
    Args:
        to_email: Recipient email address
        otp: One-time password code
        
    Returns:
        bool: Always returns True (email sends in background thread)
    """
    try:
        print(f"\n[ASYNC SEND] 🚀 Scheduling OTP email to {to_email}")
        print(f"[ASYNC SEND] User will see verify page INSTANTLY (no wait)")
        
        # Start email sending in background thread
        thread = threading.Thread(
            target=_send_otp_email_sync,
            args=(to_email, otp),
            daemon=True,  # Daemon thread won't block Flask shutdown
            name=f"EmailThread-{to_email}"  # Named thread for debugging
        )
        thread.start()
        
        print(f"[ASYNC SEND] ✅ Email thread started (non-blocking)")
        print(f"[ASYNC SEND] ✅ Returning to user immediately\n")
        return True
        
    except Exception as e:
        print(f"[ASYNC ERROR] ❌ {e}")
        logger.error(f'Error starting email thread: {e}')
        return False
