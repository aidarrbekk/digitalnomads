#!/usr/bin/env python
"""
Direct test of send_otp_email function timing
"""
import sys
import time
sys.path.insert(0, '.')

from main.app import create_app
from main.email_otp import send_otp_email

print("="*70)
print("DIRECT TIMING TEST OF send_otp_email()")
print("="*70)

# Create app context
app = create_app()

with app.app_context():
    print("\n[TEST] Calling send_otp_email('test@example.com', '123456')")
    
    start = time.time()
    result = send_otp_email('test@example.com', '123456')
    elapsed = time.time() - start
    
    print(f"\n[TEST] Result: {result}")
    print(f"[TEST] Time taken: {elapsed:.4f} seconds")
    
    if elapsed < 0.1:
        print("[TEST] ✅ ASYNC WORKING: Returned in <100ms!")
    else:
        print(f"[TEST] ⚠️  SLOW: Took {elapsed:.2f}s (blocking detected)")
    
    print("\n[TEST] Waiting 5 seconds for background email to complete...")
    time.sleep(5)
    print("[TEST] ✓ Done")
