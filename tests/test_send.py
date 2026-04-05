import os, smtplib
from email.message import EmailMessage

mail_server = os.environ.get('MAIL_SERVER')
mail_port = int(os.environ.get('MAIL_PORT') or 0)
mail_user = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')
mail_use_tls_raw = os.environ.get('MAIL_USE_TLS')
mail_use_tls = str(mail_use_tls_raw).lower() in ('true','1','yes') if mail_use_tls_raw is not None else True

msg = EmailMessage()
msg['Subject'] = 'ShipAI test email'
msg['From'] = os.environ.get('MAIL_DEFAULT_SENDER') or mail_user or 'noreply@shipai.com'
msg['To'] = mail_user or msg['From']
msg.set_content('This is a test from ShipAI.')

print('SMTP configuration (from environment):')
print(' MAIL_SERVER =', repr(mail_server))
print(' MAIL_PORT   =', repr(mail_port))
print(' MAIL_USE_TLS=', repr(mail_use_tls))
print(' MAIL_USERNAME=', repr(mail_user))
print(' MAIL_DEFAULT_SENDER=', repr(msg['From']))

if not mail_server or not mail_port:
    print('\nMail server or port not configured. Aborting send test.')
else:
    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=10) as s:
            if mail_use_tls:
                print('Starting TLS...')
                s.starttls()
            if mail_user and mail_password:
                print('Logging in as', mail_user)
                s.login(mail_user, mail_password)
            s.send_message(msg)
        print('Email sent successfully.')
    except Exception as e:
        print('Send failed:', repr(e))
