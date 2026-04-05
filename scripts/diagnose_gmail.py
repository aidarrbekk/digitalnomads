#!/usr/bin/env python
"""
Diagnose Gmail SMTP authentication issues
"""
import os
import sys
import smtplib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("GMAIL SMTP AUTHENTICATION DIAGNOSTIC")
print("=" * 70)

# Get credentials
username = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
server_name = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
port = int(os.environ.get('MAIL_PORT', 587))

print("\n1. CREDENTIALS CHECK")
print(f"   Username: {username}")
print(f"   Password Length: {len(password) if password else 0} characters")
print(f"   Server: {server_name}:{port}")
print(f"   Password Value: {password}")

# Test 1: Connection
print("\n2. CONNECTION TEST")
try:
    server = smtplib.SMTP(server_name, port, timeout=10)
    print("   ✓ Connected to SMTP server")
    
    # Test 2: TLS
    print("\n3. TLS TEST")
    try:
        server.starttls()
        print("   ✓ TLS started successfully")
    except Exception as e:
        print(f"   ✗ TLS failed: {e}")
        server.quit()
        sys.exit(1)
    
    # Test 3: Authentication
    print("\n4. AUTHENTICATION TEST")
    try:
        server.login(username, password)
        print("   ✓ Authentication successful!")
        print("\n   ✅ GMAIL SMTP IS WORKING CORRECTLY")
        server.quit()
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ✗ Authentication FAILED: {e}")
        print("\n   POSSIBLE SOLUTIONS:")
        print("   " + "=" * 66)
        print("\n   Option 1: ENABLE 'LESS SECURE APP ACCESS' (if 2FA is OFF)")
        print("   ─" * 33)
        print("   1. Go to: https://myaccount.google.com/lesssecureapps")
        print("   2. Turn ON 'Allow less secure apps'")
        print("   3. Try again")
        
        print("\n   Option 2: USE APP PASSWORD (if 2FA is ON) - RECOMMENDED")
        print("   ─" * 33)
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Select 'Mail' → 'Windows Computer'")
        print("   3. Google generates 16-char password (without spaces)")
        print("   4. Copy EXACT password (remove any spaces)")
        print("   5. Update: setx MAIL_PASSWORD \"<16-char-password>\"")
        print("   6. Restart PowerShell")
        print("   7. Try again")
        
        print("\n   Option 3: CHECK IF EMAIL IS CORRECT")
        print("   ─" * 33)
        print(f"   Current: {username}")
        print("   Make sure it's a valid Gmail address (ends with @gmail.com)")
        
        print("\n   Option 4: DISABLE 2-STEP VERIFICATION (Not Recommended)")
        print("   ─" * 33)
        print("   1. Go to: https://myaccount.google.com/security")
        print("   2. Disable '2-Step Verification'")
        print("   3. Then enable 'Less secure app access'")
        
        server.quit()
        sys.exit(1)
        
except smtplib.SMTPException as e:
    print(f"   ✗ SMTP Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Connection Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
