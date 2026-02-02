#!/usr/bin/env python3
"""
Test file overwrite protection feature
"""

import json

def test_translations():
    """Test that all translation keys exist"""
    # New keys for file overwrite
    required_keys = [
        'file_already_exists',
        'overwrite_question',
        'yes_overwrite',
        'no_cancel',
        'file_name'
    ]
    
    langs = ['en', 'ru', 'he']
    
    for lang in langs:
        filepath = f'data/translations/{lang}.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        missing = [k for k in required_keys if k not in translations]
        if missing:
            print(f"✗ {lang.upper()}: Missing keys: {missing}")
            return False
        else:
            print(f"✓ {lang.upper()}: All required keys present")
    
    return True

def test_endpoints():
    """Test that endpoints are defined"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('/api/upload-exam', 'Main upload endpoint'),
        ('/api/upload-exam/overwrite', 'Overwrite endpoint'),
        ('file_exists', '409 conflict response field'),
    ]
    
    for endpoint, description in checks:
        if endpoint in content:
            print(f"✓ {description}: Found '{endpoint}'")
        else:
            print(f"✗ {description}: Missing '{endpoint}'")
            return False
    
    return True

def test_frontend():
    """Test that frontend has dialog handling"""
    with open('templates/teacher_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('showOverwriteDialog', 'Confirmation dialog function'),
        ('file_exists', 'File exists check'),
        ('uploadFile', 'Upload helper function'),
        ('409', 'HTTP 409 status check'),
    ]
    
    for check, description in checks:
        if check in content:
            print(f"✓ Frontend {description}: Found '{check}'")
        else:
            print(f"✗ Frontend {description}: Missing '{check}'")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("Testing File Overwrite Protection Feature")
    print("=" * 50)
    
    all_ok = True
    
    print("\n📝 Testing Translation Keys:")
    all_ok &= test_translations()
    
    print("\n🔌 Testing Backend Endpoints:")
    all_ok &= test_endpoints()
    
    print("\n🎨 Testing Frontend Implementation:")
    all_ok &= test_frontend()
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ All tests passed! Feature is ready.")
    else:
        print("❌ Some tests failed. Please fix the issues.")
    print("=" * 50)
