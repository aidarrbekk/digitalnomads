#!/usr/bin/env python
"""
Test email validation timing specifically
"""
import sys
import time
sys.path.insert(0, '.')

print("="*70)
print("TESTING EMAIL VALIDATION TIMING")
print("="*70)

# Test email_validator directly
print("\n[TEST] Testing email_validator library...")
try:
    from email_validator import validate_email, EmailNotValidError
    
    emails = [
        'test@example.com',
        'valid.email@gmail.com',
        'user+tag@domain.co.uk',
    ]
    
    for email in emails:
        t0 = time.time()
        try:
            validation = validate_email(email, check_deliverability=True)
            t1 = time.time()
            elapsed = (t1 - t0) * 1000
            print(f"[TEST] {email:30} -> {elapsed:6.1f}ms (deliverability check ON)")
        except EmailNotValidError as e:
            print(f"[TEST] {email:30} -> INVALID: {e}")
            
except Exception as e:
    print(f"[TEST] Error: {e}")

print("\n[TEST] That's likely the 2-second delay!")
print("[TEST] The email_validator perfoms DNS and SMTP deliverability checks")
print("[TEST] Solution: Disable check_deliverability=True")
