"""
Email templates and email sending utilities
"""
from email.message import EmailMessage
import smtplib
from flask import current_app


def create_email_message(subject: str, to_email: str, html_body: str, plain_text: str) -> EmailMessage:
    """Create an email message with HTML and plain text alternatives"""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <noreply@shipai.com>')
    msg['To'] = to_email

    msg.set_content(plain_text, subtype='plain')
    msg.add_alternative(html_body, subtype='html')
    return msg


def send_email(msg: EmailMessage) -> bool:
    """Send email message via SMTP"""
    try:
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_user = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)

        if not mail_server or not mail_port:
            raise RuntimeError('Mail server not configured (MAIL_SERVER and MAIL_PORT required)')

        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
            if mail_use_tls:
                try:
                    server.starttls()
                except Exception as e:
                    current_app.logger.warning(f'TLS failed: {e}')

            if mail_user and mail_password:
                try:
                    server.login(mail_user, mail_password)
                except smtplib.SMTPAuthenticationError as e:
                    current_app.logger.error(f'SMTP auth failed: {e}')
                    raise

            server.send_message(msg)
            return True

    except Exception as e:
        current_app.logger.error(f'Email send error: {e}')
        raise


def get_confirmation_email_template(link: str) -> tuple[str, str]:
    """Get email confirmation template (HTML and plain text)"""
    html = f'''
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">Welcome to ShipAI!</h2>

                <p>Thanks for signing up. Please confirm your email address to complete your registration.</p>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #0d6efd; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        Confirm Email Address
                    </a>
                </p>

                <p>Or copy and paste this link in your browser:</p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
                    {link}
                </p>

                <p>This link will expire in 24 hours.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

                <p style="font-size: 12px; color: #666;">
                    If you didn't sign up for ShipAI, please ignore this email.
                </p>

                <p style="font-size: 12px; color: #666;">
                    Best regards,<br>
                    The ShipAI Team
                </p>
            </div>
        </body>
    </html>
    '''

    plain = f'Please confirm your email address by clicking the link:\n\n{link}\n\nThis link will expire in 24 hours.'

    return html, plain


def get_password_reset_email_template(link: str) -> tuple[str, str]:
    """Get password reset email template (HTML and plain text)"""
    html = f'''
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">Password Reset Request</h2>

                <p>We received a request to reset your password. If you didn't make this request, you can ignore this email.</p>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #0d6efd; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        Reset Password
                    </a>
                </p>

                <p>Or copy and paste this link in your browser:</p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
                    {link}
                </p>

                <p>This link will expire in 1 hour.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

                <p style="font-size: 12px; color: #666;">
                    If you didn't request a password reset, please ignore this email or contact support.
                </p>

                <p style="font-size: 12px; color: #666;">
                    Best regards,<br>
                    The ShipAI Team
                </p>
            </div>
        </body>
    </html>
    '''

    plain = f'Click the link to reset your password:\n\n{link}\n\nThis link will expire in 1 hour.'

    return html, plain
