#!/usr/bin/env python
"""
Test sending real email with correct credentials
"""
import os
import sys

# Set environment variables
os.environ['MAIL_USERNAME'] = 'ssshipaiii@gmail.com'
os.environ['MAIL_PASSWORD'] = 'retkqmngionadbhg'
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'

sys.path.insert(0, '.')

print("="*70)
print("TESTING REAL EMAIL SEND")
print("="*70)

from main.app import create_app
from main.email_otp import generate_otp, send_otp_email

app = create_app()

with app.app_context():
    from flask import current_app
    
    print("\n[CONFIG] Flask Email Configuration:")
    print(f"  From: {current_app.config['MAIL_USERNAME']}")
    print(f"  Server: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
    
    # Generate OTP
    otp = generate_otp()
    print(f"\n[OTP] Generated: {otp}")
    
    # Get email address
    to_email = input("\n[INPUT] Enter your email address to receive test code: ").strip()
    
    if not to_email:
        print("[ERROR] Email required")
        sys.exit(1)
    
    print(f"\n[SEND] Sending OTP to {to_email}...")
    print(f"[SEND] Code: {otp}")
    print("[SEND] Sending in background (async)...\n")
    
    result = send_otp_email(to_email, otp)
    
    print(f"\n[SUCCESS] Result: {result}")
    print("[SUCCESS] Check your inbox for the verification code!")
    print(f"[SUCCESS] Code to enter: {otp}")
