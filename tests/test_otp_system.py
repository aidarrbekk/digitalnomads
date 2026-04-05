#!/usr/bin/env python
"""
Test the OTP email verification system
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Flask app context
os.environ['FLASK_ENV'] = 'development'

from main.app import create_app
from main.email_otp import generate_otp, send_otp_email

# Create app
app = create_app('development')

# Test in app context
with app.app_context():
    print("=" * 60)
    print("OTP EMAIL VERIFICATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Generate OTP
    print("\n1. Testing OTP Generation...")
    otp = generate_otp()
    print(f"   Generated OTP: {otp}")
    print(f"   OTP Length: {len(otp)} (expected: 6)")
    assert len(otp) == 6, "OTP should be 6 digits"
    assert otp.isdigit(), "OTP should contain only digits"
    print("   ✓ OTP Generation: PASS")
    
    # Test 2: Mail Configuration
    print("\n2. Checking Mail Configuration...")
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    server = app.config.get('MAIL_SERVER')
    port = app.config.get('MAIL_PORT')
    
    print(f"   MAIL_USERNAME: {username}")
    print(f"   MAIL_PASSWORD: {'*' * len(password) if password else 'NOT SET'}")
    print(f"   MAIL_SERVER: {server}")
    print(f"   MAIL_PORT: {port}")
    
    assert username == 'ssshipaiii@gmail.com', f"Expected ssshipaiii@gmail.com, got {username}"
    assert password == 'retkqmngionadbhg', "Password mismatch"
    assert server == 'smtp.gmail.com', "Server mismatch"
    assert port == 587, "Port mismatch"
    print("   ✓ Mail Configuration: PASS")
    
    # Test 3: Send OTP Email
    print("\n3. Testing OTP Email Send...")
    test_email = 'yernur.aidarbek@gmail.com'  # Use your test email
    result = send_otp_email(test_email, otp)
    
    if result:
        print(f"   ✓ Email sent successfully to {test_email}")
        print(f"   Verification code sent: {otp}")
        print("   ✓ OTP Email Send: PASS")
    else:
        print(f"   ✗ Failed to send email to {test_email}")
        print("   ✗ OTP Email Send: FAIL")
    
    # Test 4: Forms Import
    print("\n4. Testing Form Imports...")
    try:
        from main.forms import SignUpForm, VerifyOTPForm, LoginForm
        print("   ✓ SignUpForm imported")
        print("   ✓ VerifyOTPForm imported")
        print("   ✓ LoginForm imported")
        print("   ✓ Forms Import: PASS")
    except ImportError as e:
        print(f"   ✗ Form import failed: {e}")
    
    # Test 5: Routes Check
    print("\n5. Checking Routes...")
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    required_routes = ['/signup', '/verify-otp', '/login', '/logout', '/dashboard']
    
    for route in required_routes:
        if route in routes:
            print(f"   ✓ Route {route} found")
        else:
            print(f"   ✗ Route {route} NOT found")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS COMPLETED!")
    print("=" * 60)
