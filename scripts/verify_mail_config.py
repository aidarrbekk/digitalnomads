#!/usr/bin/env python
"""
Verify mail configuration is correct
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main.config import Config

print("=" * 60)
print("MAIL CONFIGURATION VERIFICATION")
print("=" * 60)

# Environment variables
print("\n1. ENVIRONMENT VARIABLES:")
print(f"   MAIL_USERNAME (env): {os.environ.get('MAIL_USERNAME', 'NOT SET')}")
print(f"   MAIL_PASSWORD (env): {os.environ.get('MAIL_PASSWORD', 'NOT SET')}")
print(f"   MAIL_SERVER (env):   {os.environ.get('MAIL_SERVER', 'NOT SET')}")

# Flask Config
print("\n2. FLASK CONFIG LOADED:")
print(f"   MAIL_USERNAME: {Config.MAIL_USERNAME}")
print(f"   MAIL_PASSWORD: {Config.MAIL_PASSWORD}")
print(f"   MAIL_SERVER:   {Config.MAIL_SERVER}")
print(f"   MAIL_PORT:     {Config.MAIL_PORT}")
print(f"   MAIL_USE_TLS:  {Config.MAIL_USE_TLS}")
print(f"   MAIL_DEFAULT_SENDER: {Config.MAIL_DEFAULT_SENDER}")

# Verification
print("\n3. VERIFICATION:")
expected_username = "ssshipaiii@gmail.com"
expected_password = "retkqmngionadbhg"
expected_server = "smtp.gmail.com"

username_ok = Config.MAIL_USERNAME == expected_username
password_ok = Config.MAIL_PASSWORD == expected_password
server_ok = Config.MAIL_SERVER == expected_server

print(f"   Username Correct: {username_ok} ✓" if username_ok else f"   Username Correct: {username_ok} ✗")
print(f"   Password Correct: {password_ok} ✓" if password_ok else f"   Password Correct: {password_ok} ✗")
print(f"   Server Correct:   {server_ok} ✓" if server_ok else f"   Server Correct:   {server_ok} ✗")

if username_ok and password_ok and server_ok:
    print("\n✓ ALL MAIL SETTINGS ARE CORRECT!")
else:
    print("\n✗ SOME SETTINGS ARE INCORRECT")

print("=" * 60)
