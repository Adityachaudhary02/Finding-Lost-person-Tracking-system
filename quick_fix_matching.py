#!/usr/bin/env python3
"""
Quick fix script for face matching accuracy issue
Step-by-step guide to regenerate embeddings with improved algorithm
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def print_step(num, text):
    print(f"\n📍 STEP {num}: {text}")
    print("-" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_backend_running():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/stats", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print_header("🔧 FindThem Face Matching - Quick Fix Guide")
    
    print("""
This script will fix the face matching accuracy issue by:

1. Stopping the backend (if running)
2. Regenerating embeddings with improved algorithm
3. Restarting the backend
4. Verifying the fix

The improved algorithm uses:
  • 256-dimensional embeddings (vs old 128)
  • Multi-scale HOG features
  • Combined similarity metrics
  • Better thresholds

This will take a few minutes for all cases.
    """)
    
    input("Press Enter to continue...")
    
    # Step 1: Check backend
    print_step(1, "Checking Backend Status")
    
    if check_backend_running():
        print_warning("Backend is currently running")
        response = input("Stop backend? (y/n): ")
        if response.lower() == 'y':
            print_info("Please manually stop the backend (Ctrl+C if in terminal)")
            input("Press Enter when backend is stopped...")
        else:
            print_warning("Backend should be stopped before regenerating embeddings")
            print_info("Continuing anyway...")
    else:
        print_success("Backend is not running")
    
    # Step 2: Check database
    print_step(2, "Verifying Database Connection")
    
    try:
        from database import db
        if db.connect():
            print_success("Database connection successful")
            
            # Count cases
            result = db.execute_query("SELECT COUNT(*) as count FROM cases")
            case_count = result[0]['count'] if result else 0
            print_success(f"Found {case_count} cases to process")
        else:
            print_error("Cannot connect to database")
            return 1
    except Exception as e:
        print_error(f"Database error: {e}")
        return 1
    
    # Step 3: Regenerate embeddings
    print_step(3, "Regenerating Embeddings with Improved Algorithm")
    print_info("This may take 1-5 minutes depending on number of cases...")
    
    try:
        from face_recognition_engine import face_engine
        import mysql.connector
        from config import DB_CONFIG
        import json
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, image_path, name FROM cases")
        cases = cursor.fetchall()
        
        processed = 0
        failed = 0
        
        for i, case in enumerate(cases, 1):
            try:
                case_id = case['id']
                name = case['name']
                image_path = case['image_path']
                
                full_path = os.path.join('backend', 'uploads', image_path)
                
                if not os.path.exists(full_path):
                    print_warning(f"  [{i}/{len(cases)}] Skipped: {name} - image not found")
                    failed += 1
                    continue
                
                # Generate new embedding
                embedding = face_engine.get_face_embedding(full_path)
                embedding_json = json.dumps(embedding)
                
                # Update database
                cursor.execute(
                    "UPDATE cases SET embedding = %s WHERE id = %s",
                    (embedding_json, case_id)
                )
                conn.commit()
                
                print_success(f"  [{i}/{len(cases)}] Updated: {name}")
                processed += 1
                
            except Exception as e:
                print_error(f"  [{i}/{len(cases)}] Error processing {case.get('name')}: {e}")
                failed += 1
                continue
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"Embedding Regeneration Complete!")
        print(f"  ✅ Successfully updated: {processed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📊 Total: {len(cases)}")
        print(f"{'='*70}")
        
    except Exception as e:
        print_error(f"Regeneration failed: {e}")
        return 1
    
    # Step 4: Restart backend
    print_step(4, "Backend Ready for Restart")
    
    print_info("""
Next, restart the backend with the improved algorithm:

PowerShell:
    cd backend
    python main.py

Or in a new terminal:
    python backend/main.py
    """)
    
    input("Press Enter after restarting backend...")
    
    # Step 5: Verify
    print_step(5, "Verifying Backend with New Embeddings")
    
    print_info("Testing backend connection...")
    time.sleep(2)
    
    if check_backend_running():
        print_success("Backend is running!")
        
        try:
            response = requests.get("http://localhost:8000/api/stats", timeout=5)
            if response.status_code == 200:
                print_success("Backend API responding correctly")
                data = response.json()
                print(f"\n  Cases: {data['statistics']['total_cases']}")
                print(f"  Missing: {data['statistics']['missing_persons']}")
                print(f"  Found: {data['statistics']['found_persons']}")
        except Exception as e:
            print_error(f"API error: {e}")
    else:
        print_warning("Backend not responding - may still be starting up")
    
    # Summary
    print_header("✨ Fix Complete!")
    
    print("""
Next steps to verify the fix works:

1. Open the web application in your browser
   http://localhost:8000/static/index.html
   (or file:///c:/Users/ASUS/OneDrive/Desktop/Findthem2/frontend/index.html)

2. Upload an image and click Search

3. Verify results:
   ✅ Results should match the uploaded image
   ✅ Top match should be highly similar
   ✅ Similarity scores should be more realistic
   ✅ Wrong faces should NOT appear

4. If still having issues:
   - Check browser console (F12) for errors
   - Check backend logs for warnings
   - Try with very similar faces first
   - Verify image quality is good

Issues with the fix?
  - Check FIX_FACE_MATCHING.md for detailed explanation
  - Review backend logs for error messages
  - Verify database has correct embeddings
    """)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
