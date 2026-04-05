#!/usr/bin/env python
"""
Test email credentials
"""
import os
import sys

# Set environment variables for this session
os.environ['MAIL_USERNAME'] = 'ssshipaiii@gmail.com'
os.environ['MAIL_PASSWORD'] = 'retkqmngionadbhg'
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'

print("="*70)
print("TESTING EMAIL CREDENTIALS") 
print("="*70)

print("\n[ENV] Environment Variables:")
print(f"  MAIL_USERNAME: {os.environ.get('MAIL_USERNAME')}")
print(f"  MAIL_PASSWORD: {os.environ.get('MAIL_PASSWORD')}")
print(f"  MAIL_SERVER: {os.environ.get('MAIL_SERVER')}")

sys.path.insert(0, '.')
from main.app import create_app

print("\n[FLASK] Loading Flask app...")
app = create_app()

with app.app_context():
    from flask import current_app
    print(f"  MAIL_USERNAME: {current_app.config['MAIL_USERNAME']}")
    print(f"  MAIL_PASSWORD: {current_app.config['MAIL_PASSWORD']}")
    print(f"  MAIL_SERVER: {current_app.config['MAIL_SERVER']}")

print("\n[TEST] Testing SMTP connection...")
import smtplib

try:
    server = smtplib.SMTP(os.environ.get('MAIL_SERVER'), 587, timeout=10)
    print("  ✓ Connected to SMTP server")
    
    server.starttls()
    print("  ✓ TLS started")
    
    server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
    print("  ✓ Authentication successful!")
    
    server.quit()
    print("\n✅ ALL TESTS PASSED - Email credentials are correct!")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    print("\n❌ FAILED - Check credentials")
    sys.exit(1)
