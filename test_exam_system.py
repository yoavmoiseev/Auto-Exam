#!/usr/bin/env python3
"""
Test Exam System - Complete exam flow test
"""

import json
import re

def test_exam_parsing():
    """Test exam file parsing"""
    print("📝 Testing Exam Parsing...")
    
    # Read example exam
    with open('example_exam.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test regex patterns used in parsing
    lines = content.strip().split('\n')
    questions_found = 0
    options_found = 0
    
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and ('. ' in line or line[1] == '.'):
            questions_found += 1
        elif line and len(line) > 2 and line[0] in 'ABCDEFGH' and line[1] == ')':
            options_found += 1
    
    print(f"  ✓ Questions found: {questions_found}")
    print(f"  ✓ Options found: {options_found}")
    return questions_found > 0 and options_found > 0

def test_app_routes():
    """Test that required app routes exist"""
    print("\n🔌 Testing App Routes...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    routes = [
        '/api/exam/',
        '/api/submit-exam',
        'parse_exam_questions',
    ]
    
    all_found = True
    for route in routes:
        if route in content:
            print(f"  ✓ Route '{route}' found")
        else:
            print(f"  ✗ Route '{route}' NOT found")
            all_found = False
    
    return all_found

def test_exam_html():
    """Test exam.html structure"""
    print("\n🎨 Testing Exam HTML...")
    
    with open('templates/exam.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    elements = {
        'pre-exam': 'id="pre-exam"',
        'exam-form': 'id="exam-form"',
        'questions-container': 'id="questions-container"',
        'timer': 'id="timer"',
        'start-btn': 'id="start-btn"',
        'submit-btn': 'id="submit-btn"',
        'prev-btn': 'id="prev-btn"',
        'next-btn': 'id="next-btn"',
        'exam-results': 'id="exam-results"',
        'first-name': 'id="first-name"',
        'last-name': 'id="last-name"',
    }
    
    all_found = True
    for name, selector in elements.items():
        if selector in content:
            print(f"  ✓ Element '{name}' found")
        else:
            print(f"  ✗ Element '{name}' NOT found")
            all_found = False
    
    return all_found

def test_exam_script():
    """Test exam_script.js functionality"""
    print("\n📜 Testing Exam Script...")
    
    with open('static/js/exam_script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions = [
        'loadExamQuestions',
        'displayCurrentQuestion',
        'recordAnswer',
        'submitExam',
        'startTimer',
        'nextQuestion',
        'previousQuestion',
        'showResults',
    ]
    
    all_found = True
    for func in functions:
        if func in content:
            print(f"  ✓ Function '{func}' found")
        else:
            print(f"  ✗ Function '{func}' NOT found")
            all_found = False
    
    return all_found

def test_translations():
    """Test translation keys"""
    print("\n🌐 Testing Translations...")
    
    required_keys = [
        'question',
        'answer',
        'correct_answer',
        'submit_exam',
        'start_exam',
        'exam_submitted',
        'exam_failed',
        'previous',
        'next',
        'exam_results',
        'confirm_submit',
        'required',
        'correct',
    ]
    
    langs = ['en', 'ru', 'he']
    all_ok = True
    
    for lang in langs:
        with open(f'data/translations/{lang}.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        missing = [k for k in required_keys if k not in translations]
        if missing:
            print(f"  ✗ {lang.upper()}: Missing keys: {missing}")
            all_ok = False
        else:
            print(f"  ✓ {lang.upper()}: All required keys present")
    
    return all_ok

def test_json_validity():
    """Test that all JSON files are valid"""
    print("\n✓ Testing JSON Validity...")
    
    json_files = [
        'data/translations/en.json',
        'data/translations/ru.json',
        'data/translations/he.json',
    ]
    
    all_valid = True
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"  ✓ {filepath} is valid JSON")
        except json.JSONDecodeError as e:
            print(f"  ✗ {filepath} has JSON error: {e}")
            all_valid = False
    
    return all_valid

if __name__ == '__main__':
    print("=" * 60)
    print("EXAM SYSTEM - COMPLETE FLOW TEST")
    print("=" * 60)
    
    tests = [
        ("Exam Parsing", test_exam_parsing),
        ("App Routes", test_app_routes),
        ("Exam HTML", test_exam_html),
        ("Exam Script", test_exam_script),
        ("Translations", test_translations),
        ("JSON Validity", test_json_validity),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - EXAM SYSTEM READY!")
    else:
        print("⚠️  Some tests failed - Please fix issues")
    print("=" * 60)
