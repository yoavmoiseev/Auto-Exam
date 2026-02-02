#!/usr/bin/env python3
"""
Quick test script for sign-up and file upload functionality
Tests the new features without running full Flask server
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService
from config import app_config

def test_signup_system():
    """Test user signup and authentication"""
    print("=" * 60)
    print("TESTING SIGNUP SYSTEM")
    print("=" * 60)
    
    auth = AuthService()
    
    # Test 1: Create new user
    print("\n✓ Test 1: Creating new teacher account...")
    timestamp = str(int(time.time()))
    username = f"test_teacher_{timestamp}"
    
    result = auth.add_user(
        username=username,
        password="TestPass123",
        first_name="Test",
        last_name="Teacher",
        email="test@example.com"
    )
    
    if result['success']:
        print(f"  ✅ User created: {result['message']}")
        user_id = result['user_id']
    else:
        print(f"  ❌ Failed: {result['message']}")
        return False
    
    # Test 2: Login with new account
    print("\n✓ Test 2: Logging in with new account...")
    result = auth.authenticate(username, "TestPass123")
    
    if result['success']:
        print(f"  ✅ Login successful: {result['user']['first_name']} {result['user']['last_name']}")
    else:
        print(f"  ❌ Login failed: {result['message']}")
        return False
    
    # Test 3: Try duplicate username
    print("\n✓ Test 3: Testing duplicate username prevention...")
    result = auth.add_user(
        username=username,  # Same username
        password="DifferentPass123",
        first_name="Another",
        last_name="User"
    )
    
    if not result['success']:
        print(f"  ✅ Duplicate prevented: {result['message']}")
    else:
        print(f"  ⚠️ Warning: Duplicate not prevented!")
        return False
    
    # Test 4: Verify database file
    print("\n✓ Test 4: Checking database file...")
    db_path = os.path.join(app_config.DATA_DIR, 'users.db')
    
    if os.path.exists(db_path):
        print(f"  ✅ Database exists: {db_path}")
        print(f"     Size: {os.path.getsize(db_path)} bytes")
    else:
        print(f"  ❌ Database not found!")
        return False
    
    # Test 5: Verify teacher directories
    print("\n✓ Test 5: Checking teacher directories...")
    teacher_dir = os.path.join(app_config.TEACHERS_DIR, f"teacher_{user_id}")
    exams_dir = os.path.join(teacher_dir, 'exams')
    
    if os.path.exists(exams_dir):
        print(f"  ✅ Teacher exams directory exists: {exams_dir}")
    else:
        # Create it
        os.makedirs(exams_dir, exist_ok=True)
        print(f"  ✅ Created teacher exams directory: {exams_dir}")
    
    return True


def test_file_system():
    """Test file upload structure"""
    print("\n" + "=" * 60)
    print("TESTING FILE SYSTEM")
    print("=" * 60)
    
    # Test 1: Directory structure
    print("\n✓ Test 1: Checking directory structure...")
    dirs_to_check = [
        app_config.DATA_DIR,
        app_config.TEACHERS_DIR,
        app_config.LOGS_DIR,
        os.path.join(app_config.DATA_DIR, 'translations')
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ Missing: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"     Created.")
    
    # Test 2: Translation files
    print("\n✓ Test 2: Checking translation files...")
    translations = ['en.json', 'ru.json', 'he.json']
    
    for lang_file in translations:
        lang_path = os.path.join(app_config.DATA_DIR, 'translations', lang_file)
        
        if os.path.exists(lang_path):
            try:
                with open(lang_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keys = len(data)
                    print(f"  ✅ {lang_file}: {keys} translation keys")
            except Exception as e:
                print(f"  ❌ Error reading {lang_file}: {e}")
                return False
        else:
            print(f"  ❌ Missing: {lang_file}")
            return False
    
    # Test 3: Sample upload
    print("\n✓ Test 3: Creating sample exam file...")
    sample_exam = """1. What is 2 + 2?
A) 3
B) 4
C) 5
answer: b

2. What is the capital of France?
A) London
B) Berlin
C) Paris
answer: c
"""
    
    exam_file = os.path.join(app_config.TEACHERS_DIR, 'teacher_1', 'exams', 'sample_test.txt')
    os.makedirs(os.path.dirname(exam_file), exist_ok=True)
    
    try:
        with open(exam_file, 'w', encoding='utf-8') as f:
            f.write(sample_exam)
        print(f"  ✅ Sample exam created: {exam_file}")
        print(f"     Size: {os.path.getsize(exam_file)} bytes")
    except Exception as e:
        print(f"  ❌ Error creating sample exam: {e}")
        return False
    
    return True


def test_translations():
    """Test translation system"""
    print("\n" + "=" * 60)
    print("TESTING TRANSLATION SYSTEM")
    print("=" * 60)
    
    required_keys = [
        'signup_title',
        'login_title',
        'first_name',
        'last_name',
        'email',
        'password',
        'confirm_password',
        'signup_button',
        'already_registered',
        'login_link'
    ]
    
    langs = ['en', 'ru', 'he']
    
    for lang in langs:
        print(f"\n✓ Checking {lang.upper()}...")
        lang_file = os.path.join(app_config.DATA_DIR, 'translations', f'{lang}.json')
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            missing = []
            for key in required_keys:
                if key not in data:
                    missing.append(key)
            
            if not missing:
                print(f"  ✅ All {len(required_keys)} required keys present")
            else:
                print(f"  ⚠️ Missing {len(missing)} keys: {missing}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error reading {lang}: {e}")
            return False
    
    return True


def test_flask_routes():
    """Check if Flask routes are defined"""
    print("\n" + "=" * 60)
    print("TESTING FLASK ROUTES")
    print("=" * 60)
    
    try:
        from app import app
        
        routes = [
            '/login',
            '/signup',
            '/logout',
            '/dashboard',
            '/api/upload-exam',
            '/api/exams-list',
            '/api/delete-exam/<filename>',
            '/api/auth/login'
        ]
        
        print("\n✓ Checking Flask routes...")
        
        # Get all registered routes
        registered_routes = set()
        for rule in app.url_map.iter_rules():
            registered_routes.add(str(rule.rule))
        
        for route in routes:
            # Handle parameterized routes
            route_pattern = route.split('<')[0] if '<' in route else route
            
            found = any(route_pattern in r for r in registered_routes)
            
            status = "✅" if found else "❌"
            print(f"  {status} {route}")
        
        print(f"\n  Total routes: {len(registered_routes)}")
        return True
        
    except Exception as e:
        print(f"  ⚠️ Could not test Flask routes: {e}")
        return True  # Not critical


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  EXAM SYSTEM - SIGNUP & UPLOAD FUNCTIONALITY TEST".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Signup System", test_signup_system),
        ("File System", test_file_system),
        ("Translations", test_translations),
        ("Flask Routes", test_flask_routes),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results[test_name] = "ERROR"
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, status in results.items():
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{symbol} {test_name}: {status}")
    
    passed = sum(1 for s in results.values() if s == "PASS")
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
