#!/usr/bin/env python3
"""Verify that the signup.html template error is fixed"""

import sys
from app import app

print("=" * 60)
print("VERIFICATION TEST - i18n FILTER ERROR FIX")
print("=" * 60)

# Test 1: App imports
print("\nTest 1: Flask app imports...")
try:
    print("  OK - app.py imports successfully")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 2: Templates render
print("\nTest 2: Testing template rendering...")
templates = ['signup.html', 'login.html', 'teacher_dashboard.html']
with app.test_request_context():
    from flask import render_template
    for template in templates:
        try:
            html = render_template(template)
            print(f"  OK - {template} renders")
        except Exception as e:
            print(f"  FAIL - {template}: {e}")
            sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS! All tests passed.")
print("The i18n filter error is FIXED.")
print("=" * 60)
print("\nYou can now:")
print("  1. Start the server: python -m flask run --debug")
print("  2. Visit: http://127.0.0.1:5000/login")
print("  3. Click 'Create Account' to test signup")
