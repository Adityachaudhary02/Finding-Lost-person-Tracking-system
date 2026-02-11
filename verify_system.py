#!/usr/bin/env python3
"""
Complete system verification for FindThem Face Recognition App
Tests all components: Backend, Database, API endpoints, Files
"""

import requests
import sys
from pathlib import Path
import json

API_BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def check_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def check_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def check_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def test_backend_connection():
    print_header("1. Testing Backend Connection")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            check_success("Backend is running")
            data = response.json()
            print(f"   Total Cases: {data['statistics']['total_cases']}")
            print(f"   Missing: {data['statistics']['missing_persons']}")
            print(f"   Found: {data['statistics']['found_persons']}")
            return True
        else:
            check_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        check_error("Cannot connect to backend at " + API_BASE_URL)
        check_warning("Make sure to run: python backend/main.py")
        return False
    except Exception as e:
        check_error(f"Error: {str(e)}")
        return False

def test_database():
    print_header("2. Testing Database")
    
    try:
        sys.path.insert(0, 'backend')
        from database import db
        
        if db.connect():
            check_success("Database connection successful")
            
            # Test query
            query = "SELECT COUNT(*) as count FROM cases"
            result = db.execute_query(query)
            if result:
                count = result[0]['count']
                check_success(f"Database has {count} cases")
                return True
        else:
            check_error("Failed to connect to database")
            return False
    except Exception as e:
        check_error(f"Database error: {str(e)}")
        return False

def test_file_structure():
    print_header("3. Checking File Structure")
    
    files_to_check = [
        'frontend/index.html',
        'frontend/script.js',
        'frontend/styles.css',
        'backend/main.py',
        'backend/database.py',
        'backend/face_recognition_engine.py',
        'backend/config.py'
    ]
    
    all_exist = True
    for filepath in files_to_check:
        if Path(filepath).exists():
            check_success(f"Found {filepath}")
        else:
            check_error(f"Missing {filepath}")
            all_exist = False
    
    return all_exist

def test_uploads_folder():
    print_header("4. Checking Uploads Folder")
    
    uploads_dir = Path('backend/uploads')
    if uploads_dir.exists():
        check_success("Uploads folder exists")
        image_files = list(uploads_dir.glob('*.jpg')) + list(uploads_dir.glob('*.png')) + list(uploads_dir.glob('*.gif'))
        if image_files:
            check_success(f"Found {len(image_files)} image files")
            return True
        else:
            check_warning("No image files in uploads folder")
            return True
    else:
        check_error("Uploads folder not found")
        return False

def test_search_api():
    print_header("5. Testing Search API")
    
    try:
        # Find a test image
        uploads_dir = Path('backend/uploads')
        image_files = list(uploads_dir.glob('*.jpg')) + list(uploads_dir.glob('*.png')) + list(uploads_dir.glob('*.gif'))
        
        if not image_files:
            check_warning("No test images found in uploads folder")
            return False
        
        test_image = image_files[0]
        check_success(f"Using test image: {test_image.name}")
        
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_BASE_URL}/search-face", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                check_success("Search API working")
                matches = data.get('matches', [])
                check_success(f"Search returned {len(matches)} matches")
                return True
            else:
                check_error(f"API error: {data.get('detail')}")
                return False
        else:
            check_error(f"API returned status {response.status_code}")
            return False
    except Exception as e:
        check_error(f"Search API error: {str(e)}")
        return False

def test_html_elements():
    print_header("6. Checking HTML Elements")
    
    try:
        with open('frontend/index.html', 'r') as f:
            html = f.read()
        
        elements = [
            'searchResults',
            'noResults',
            'searchStatus',
            'matchBanner',
            'resultsList',
            'resultsCount',
            'searchBtn',
            'searchInput'
        ]
        
        all_found = True
        for element_id in elements:
            if f'id="{element_id}"' in html:
                check_success(f"Found element #{element_id}")
            else:
                check_error(f"Missing element #{element_id}")
                all_found = False
        
        return all_found
    except Exception as e:
        check_error(f"Error checking HTML: {str(e)}")
        return False

def test_javascript():
    print_header("7. Checking JavaScript")
    
    try:
        with open('frontend/script.js', 'r') as f:
            js = f.read()
        
        functions = [
            'handleSearch',
            'displaySearchResults',
            'handlePhotoUpload',
            'handleReportSubmit'
        ]
        
        all_found = True
        for func_name in functions:
            if f'function {func_name}' in js or f'async function {func_name}' in js:
                check_success(f"Found function {func_name}()")
            else:
                check_error(f"Missing function {func_name}()")
                all_found = False
        
        return all_found
    except Exception as e:
        check_error(f"Error checking JavaScript: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'*'*60}")
    print(f"{'FindThem - System Verification':^60}")
    print(f"{'*'*60}{Colors.END}\n")
    
    results = {
        'Backend': test_backend_connection(),
        'Database': test_database(),
        'Files': test_file_structure(),
        'Uploads': test_uploads_folder(),
        'Search API': test_search_api(),
        'HTML': test_html_elements(),
        'JavaScript': test_javascript()
    }
    
    print_header("VERIFICATION SUMMARY")
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        if result:
            check_success(f"{test_name}")
            passed += 1
        else:
            check_error(f"{test_name}")
            failed += 1
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.END} | Failed: {Colors.RED}{failed}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if failed == 0:
        check_success("All systems operational! ✨")
        print("\nNext steps:")
        print("1. Open frontend/index.html in your browser")
        print("2. Test the upload and search features")
        print("3. Check browser console (F12) for detailed logs")
        return 0
    else:
        check_error(f"{failed} system(s) need attention")
        print("\nTroubleshooting:")
        print("1. Make sure backend is running: python backend/main.py")
        print("2. Check MySQL is running")
        print("3. Verify file paths are correct")
        return 1

if __name__ == "__main__":
    sys.exit(main())
