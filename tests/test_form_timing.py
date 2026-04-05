#!/usr/bin/env python
"""
Test form validation timing
"""
import sys
import time
sys.path.insert(0, '.')

from main.app import create_app
from main.forms import SignUpForm
from flask import session

print("="*70)
print("TESTING FORM VALIDATION TIMING")
print("="*70)

# Create app context
app = create_app()

with app.test_request_context():
    # Test form creation
    print("\n[TEST] Creating form...")
    t0 = time.time()
    form = SignUpForm()
    t1 = time.time()
    print(f"[TEST] Form creation: {(t1-t0)*1000:.1f}ms")
    
    # Test form submission with valid data
    print("\n[TEST] Validating form with data...")
    from werkzeug.datastructures import MultiDict
    
    form_data = MultiDict([
        ('username', 'testuser123'),
        ('email', 'test.example@gmail.com'),
        ('password', 'TestPass123!'),
        ('password_confirm', 'TestPass123!'),
        ('csrf_token', form.csrf_token.data)
    ])
    
    form2 = SignUpForm(form_data)
    t2 = time.time()
    
    print(f"[TEST] Starting validation at {t2:.2f}...")
    is_valid = form2.validate()
    t3 = time.time()
    
    print(f"[TEST] Form validation: {(t3-t2)*1000:.1f}ms")
    print(f"[TEST] Is valid: {is_valid}")
    
    if not is_valid:
        for field, errors in form2.errors.items():
            print(f"[TEST]   {field}: {errors}")
    else:
        print(f"[TEST] ✅ Form is valid and ready to submit")
        print(f"[TEST] Total form overhead: {(t3-t0)*1000:.1f}ms")
