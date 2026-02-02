#!/usr/bin/env python3
"""Quick test to verify templates render without errors"""

from app import app

with app.test_request_context():
    from flask import render_template
    
    templates_to_test = [
        'signup.html',
        'login.html',
        'teacher_dashboard.html',
        'base.html'
    ]
    
    for template_name in templates_to_test:
        try:
            html = render_template(template_name)
            print(f"✅ {template_name} renders successfully")
        except Exception as e:
            print(f"❌ {template_name}: {e}")
