#!/usr/bin/env python
"""
Direct Flask test client measurement
"""
import sys
import time
sys.path.insert(0, '.')

from main.app import create_app

app = create_app()

print("="*70)
print("DIRECT FLASK ENDPOINT TIMING TEST")
print("="*70)

with app.test_client() as client:
    # Get signup page first
    print("\n[TEST] Getting signup page...")
    r1 = client.get('/signup')
    if r1.status_code != 200:
        print(f"[TEST] ERROR: {r1.status_code}")
        sys.exit(1)
    
    # Extract CSRF token
    import re
    csrf = re.search(r'csrf_token[" \n]*type="hidden"[" \n]*value="([^"]+)"', r1.get_data(as_text=True))
    csrf_token = csrf.group(1) if csrf else None
    print(f"[TEST] CSRF Token: {csrf_token[:20]}..." if csrf_token else "[TEST] No CSRF found!")
    
    # Submit signup form - measure just the POST
    print("\n[TEST] Submitting signup form...")
    print("[TEST] Measuring: time.time() BEFORE POST to time.time() AFTER response...")
    
    signup_data = {
        'username': 'testuser456',
        'email': 'test456@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'csrf_token': csrf_token
    }
    
    start = time.time()
    response = client.post('/signup', data=signup_data, follow_redirects=False)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n[TEST] ENDPOINT RESPONSE TIME: {elapsed:.1f}ms")
    print(f"[TEST] Status: {response.status_code}")
    
    if elapsed < 500:
        print(f"[TEST] ✅ FAST: {elapsed:.1f}ms (<500ms)")
    elif elapsed < 1000:
        print(f"[TEST] ⚠️  SLOW: {elapsed:.1f}ms (500ms-1s)")
    else:
        print(f"[TEST] 🔴 VERY SLOW: {elapsed:.1f}ms (>1s)")
        print("[TEST] Something is still blocking!")
