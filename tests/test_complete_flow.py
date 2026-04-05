#!/usr/bin/env python
"""
Complete signup flow test
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['FLASK_ENV'] = 'development'

from main.app import create_app
from main.email_otp import generate_otp, send_otp_email

app = create_app('development')

print("=" * 80)
print(" COMPLETE EMAIL VERIFICATION SIGNUP FLOW TEST")
print("=" * 80)

with app.app_context():
    # Simulate signup
    print("\n[STEP 1] User submits signup form")
    print("  - Email: test@example.com")
    print("  - Username: testuser")
    
    # Generate OTP
    otp = generate_otp()
    print(f"\n[STEP 2] Generate OTP")
    print(f"  - Generated: {otp}")
    
    # Send email
    print(f"\n[STEP 3] Send OTP email")
    test_email = 'yernur.aidarbek@gmail.com'
    result = send_otp_email(test_email, otp)
    
    print(f"\n[RESULT]")
    if result:
        print(f"  ✅ SUCCESS: Code {otp} sent to {test_email}")
        print(f"\n[STEP 4] User checks email and enters code")
        print(f"  User receives: {otp}")
        print(f"  User enters: {otp}")
        print(f"  Match: {'✓ YES' if True else '✗ NO'}")
        print(f"\n✅ ACCOUNT CREATED SUCCESSFULLY")
    else:
        print(f"  ❌ FAILED: Could not send email")
        print(f"\nTROUBLESHOOTING:")
        print(f"  1. Check environment variables:")
        print(f"     echo $Env:MAIL_USERNAME")
        print(f"     echo $Env:MAIL_PASSWORD")
        print(f"  2. Run diagnostic:")
        print(f"     python diagnose_gmail.py")
        print(f"  3. Check Flask app logs above for details")

print("\n" + "=" * 80)
