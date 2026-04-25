"""
Email templates and email sending utilities via Resend HTTP API
"""
import requests
from email.message import EmailMessage
from flask import current_app


def create_email_message(subject: str, to_email: str, html_body: str, plain_text: str) -> EmailMessage:
    """Create an email message object (kept for compatibility)"""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <onboarding@ship-ai.app>')
    msg['To'] = to_email
    msg.set_content(plain_text, subtype='plain')
    msg.add_alternative(html_body, subtype='html')
    return msg


def send_email(msg: EmailMessage) -> bool:
    """Send email via Resend HTTP API (replaces old SMTP send_email)"""
    try:
        api_key = current_app.config.get('RESEND_API_KEY')
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'ShipAI <onboarding@ship-ai.app>')

        if not api_key:
            raise RuntimeError('RESEND_API_KEY not configured')

        to_email = msg['To']
        subject = msg['Subject']

        # Extract HTML and plain text from EmailMessage
        html_body = ''
        plain_text = ''
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_subtype() == 'html':
                    html_body = part.get_content()
                elif part.get_content_subtype() == 'plain':
                    plain_text = part.get_content()
        else:
            plain_text = msg.get_content()

        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': sender,
                'to': [to_email],
                'subject': subject,
                'html': html_body,
                'text': plain_text,
            },
            timeout=10
        )

        if response.status_code in (200, 201):
            return True

        current_app.logger.error(f'Resend API error: {response.status_code} {response.text}')
        raise RuntimeError(f'Resend API error: {response.status_code}')

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