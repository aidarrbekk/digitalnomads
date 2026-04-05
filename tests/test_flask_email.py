#!/usr/bin/env python
"""
Direct email test from Flask app context
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main.app import create_app
from main.email_otp import send_otp_email

app = create_app('development')

print("=" * 70)
print("DIRECT FLASK APP EMAIL TEST")
print("=" * 70)

with app.app_context():
    print("\nStep 1: Check Configuration in App Context")
    print(f"  MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"  MAIL_PASSWORD: {'*' * 16}")
    print(f"  MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"  MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"  MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    
    print("\nStep 2: Send Test Email (OTP)")
    try:
        test_email = 'yernur.aidarbek@gmail.com'
        test_otp = '123456'
        
        result = send_otp_email(test_email, test_otp)
        
        if result:
            print(f"  ✅ SUCCESS: Email sent to {test_email}")
            print(f"  OTP Code: {test_otp}")
            print("\n✓ Flask App Email Test: PASSED")
        else:
            print(f"  ❌ FAILED: Could not send email")
            print("\n✗ Flask App Email Test: FAILED")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n✗ Flask App Email Test: FAILED")

print("=" * 70)
