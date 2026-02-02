#!/usr/bin/env python3
"""
Quick test to verify i18n API is working correctly
"""
import json
import requests

# Test if Flask app is running and test the API
try:
    print("Testing i18n API endpoints...")
    
    # Test each language
    for lang in ['en', 'ru', 'he']:
        url = f'http://localhost:5000/api/translations/{lang}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {lang}: API returns {len(data)} translation keys")
            else:
                print(f"✗ {lang}: Status {response.status_code}")
        except Exception as e:
            print(f"✗ {lang}: Connection error: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Flask app is running on http://localhost:5000")
