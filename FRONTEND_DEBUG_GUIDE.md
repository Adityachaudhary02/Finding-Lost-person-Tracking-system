# Frontend Debugging Guide

## How to Debug API-Frontend Connection Issues

### Step 1: Enable Browser Console Logging

1. **Open your browser** (Chrome, Firefox, Edge, etc.)
2. **Press F12** to open Developer Tools
3. **Click on "Console" tab**
4. **Open** `http://localhost:8000/index`

You should see detailed logs like:
```
✅ Page loaded, initializing...
API_BASE_URL: http://localhost:8000/api
SEARCH_ENDPOINT: http://localhost:8000/api/search-face
🔗 Initialization complete
```

---

### Step 2: Upload a Photo and Start Search

1. Click on "Search for Similar Faces" section
2. Upload a photo (e.g., `adi photo.jpg`)
3. Click the **Search** button
4. **Watch the Console** - You'll see real-time logs

---

### Step 3: Look for These Console Logs

#### ✅ SUCCESS Path (Expected Logs)

```
🔍 Sending search request to: http://localhost:8000/api/search-face
📁 File: adi photo.jpg

📊 Response status: 200
📊 Response headers: {
  'content-type': 'application/json',
  'status': 'OK'
}

✅ Response data received: {
  "success": true,
  "message": "Found 1 potential match(es)",
  "matches": [
    {
      "case_id": 6,
      "name": "aditya",
      "status": "found",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "description": "patna",
      "image_path": "20260122_190547_adi photo.jpg",
      "similarity_score": 1,
      "similarity_percentage": 100
    }
  ],
  ...
}

🎉 Search successful! Found 1 matches

===== DISPLAY SEARCH RESULTS =====
📥 Input data: {...}

🔗 DOM Elements check:
  - searchStatus: ✅
  - searchResults: ✅
  - noResults: ✅
  - resultsList: ✅
  - matchBanner: ✅

🔍 Filtering Results: 1 total → 1 filtered (90%+)
  - aditya: 100% ✅ PASS

✅ Found 1 matches! Building result cards...

📋 Building card 1:
  - Name: aditya
  - Similarity: 100%
  - Status: FOUND
  - Image URL: http://localhost:8000/uploads/20260122_190547_adi photo.jpg
  - Description: patna
  - Contact: adityakumaR1632003@GMAIL.COM

🖼️ Setting results HTML...
✅ HTML set to resultsList

📊 Result count text updated: Found <strong>1 potential match</strong> with 90%+ similarity

🎉 DISPLAYING RESULTS ON PAGE
  - matchBanner.style.display = "block"
  - searchResults.style.display = "block"
  - noResults.style.display = "none"

✅ Visibility updated

📍 Auto-scrolling to match banner...

===== DISPLAY COMPLETE =====
```

#### ❌ Common Error Patterns

**Problem: No Response**
```
❌ Search error: TypeError: Failed to fetch
Error stack: ...
```
**Solution**: 
- Make sure backend is running: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
- Check if port 8000 is accessible
- Verify no firewall blocking

---

**Problem: CORS Error**
```
❌ Access to XMLHttpRequest at 'http://localhost:8000/api/search-face' from origin 
'http://localhost:8000' has been blocked by CORS policy
```
**Solution**: 
- Backend has CORS enabled, should not see this error
- If you see it, backend may not be running properly
- Restart backend

---

**Problem: File Upload Issue**
```
❌ Search error: Invalid file format
❌ Search error: No face detected in the image
```
**Solution**:
- Use JPG, PNG, GIF, or BMP images only
- Make sure image contains a clear face
- Try uploading a different photo

---

**Problem: Similarity Too Low (No 90%+ Matches)**
```
🔍 Filtering Results: 4 total → 0 filtered (90%+)
  - aditya: 85.32% ❌ FAIL (below 90%)
  - aditya: 72.15% ❌ FAIL (below 90%)
  - hanuman: 41.2% ❌ FAIL (below 90%)
  - case3: 62.3% ❌ FAIL (below 90%)

❌ No matches after filtering - displaying no results message
```
**Solution**:
- Upload exact same photo as database (should get 100%)
- Or upload a very similar photo from the same person
- The 90% threshold is quite high

---

### Step 4: Check Network Tab

1. **Click on "Network" tab** in Developer Tools
2. **Perform a search**
3. **Look for the search-face request**
4. **Click on it** to see:
   - **Request Headers** - Should show `Content-Type: multipart/form-data`
   - **Response Headers** - Should show `Content-Type: application/json`
   - **Response Body** - The JSON data from backend

---

### Step 5: Verify Backend Response Format

The backend should return this exact JSON structure:

```json
{
  "success": true,
  "message": "Found X potential match(es)",
  "matches": [
    {
      "case_id": 6,
      "name": "aditya",
      "status": "found",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "description": "patna",
      "image_path": "20260122_190547_adi photo.jpg",
      "similarity_score": 1,
      "similarity_percentage": 100
    }
  ],
  "total_cases_searched": 4,
  "threshold_used": 0.9,
  "search_time": "2026-01-23T01:12:41.296630"
}
```

**Required fields**:
- ✅ `success` (boolean)
- ✅ `message` (string)
- ✅ `matches` (array)
  - ✅ `case_id` (number)
  - ✅ `name` (string)
  - ✅ `status` (string: "missing" or "found")
  - ✅ `contact` (string)
  - ✅ `description` (string)
  - ✅ `image_path` (string - filename only)
  - ✅ `similarity_score` (number 0-1)
  - ✅ `similarity_percentage` (number 0-100)

---

### Step 6: Check Image Loading

In the Console, you'll see:

**✅ If image loads successfully**:
```
📋 Building card 1:
  - Image URL: http://localhost:8000/uploads/20260122_190547_adi photo.jpg
```

**❌ If image fails to load**:
```
❌ Image failed to load: http://localhost:8000/uploads/20260122_190547_adi photo.jpg
```

**Solution**:
- Check if the file exists in `backend/uploads/` folder
- Make sure the `image_path` in database matches actual filename
- Verify file permissions

---

### Step 7: DOM Elements Check

Frontend verifies all HTML elements exist. You should see:

```
🔗 DOM Elements check:
  - searchStatus: ✅
  - searchResults: ✅
  - noResults: ✅
  - resultsList: ✅
  - matchBanner: ✅
```

**If any show ❌**:
- Element is missing from index.html
- Check HTML structure
- Refresh page

---

### Step 8: Quick Test Checklist

- [ ] **Backend Running**: Can you access `http://localhost:8000/health`?
- [ ] **Database Connected**: Does `/health` return `{"status":"healthy","database":"connected"}`?
- [ ] **Cases in Database**: Are there test cases? Check with curl or in MySQL
- [ ] **Console Shows Logs**: Do you see initialization logs in F12 console?
- [ ] **Search Request Sent**: Do you see "🔍 Sending search request..." in console?
- [ ] **Backend Responds**: Do you see "📊 Response status: 200" in console?
- [ ] **JSON Received**: Do you see "✅ Response data received:" in console?
- [ ] **Results Display**: Do you see "🎉 DISPLAYING RESULTS ON PAGE" in console?
- [ ] **Green Banner Visible**: Can you see the "✓ MATCH FOUND!" banner on page?
- [ ] **Result Cards Visible**: Can you see match cards with photos and details?

---

### Step 9: Manual API Testing with cURL

Open a terminal and test the API directly:

```powershell
# Test 1: Health Check
curl -X GET http://localhost:8000/health

# Test 2: Search with a test image
curl -X POST "http://localhost:8000/api/search-face" `
  -H "Content-Type: multipart/form-data" `
  -F "image=@C:\path\to\your\image.jpg"

# Test 3: Get all cases
curl -X GET http://localhost:8000/api/cases
```

---

### Step 10: Backend Logs

Check your backend terminal for matching logs:

```
2026-01-23 12:50:30,123 - main - INFO - Starting search...
2026-01-23 12:50:30,234 - main - INFO - Image file saved: temp_20260123_125030_aditya.jpg
2026-01-23 12:50:30,456 - face_recognition_engine - INFO - Detected 1 face(s)
2026-01-23 12:50:30,678 - face_recognition_engine - INFO - Created embedding of length 128
2026-01-23 12:50:30,789 - main - INFO - Loaded 4 cases from database
2026-01-23 12:50:30,890 - face_recognition_engine - INFO - Searching 4 cases with threshold 0.9
2026-01-23 12:50:30,901 - face_recognition_engine - INFO - Case 6 similarity: 1.0
2026-01-23 12:50:30,905 - face_recognition_engine - INFO - Found 1 potential matches
2026-01-23 12:50:30,906 - main - INFO - Search completed. Found 1 matches out of 4 cases. Threshold: 0.9
2026-01-23 12:50:30,907 - main - INFO -   - aditya: 100% match
```

---

## Troubleshooting Flowchart

```
Start: User clicks Search
  ↓
[F12 Console] See logs?
  ├─ NO → Backend not running or page not loaded properly
  │        → Restart backend, refresh page
  │
  └─ YES → See "🔍 Sending search request..."?
             ├─ NO → JavaScript error in handleSearch()
             │        → Check for exceptions in console
             │
             └─ YES → See "📊 Response status: 200"?
                       ├─ NO → Backend error or connection issue
                       │        → Check backend logs
                       │
                       └─ YES → See "✅ Response data received:"?
                                 ├─ NO → JSON parse error
                                 │        → Check response format
                                 │
                                 └─ YES → See "🎉 Search successful!"?
                                           ├─ NO → data.success = false
                                           │        → Check error message
                                           │
                                           └─ YES → See "🎉 DISPLAYING RESULTS ON PAGE"?
                                                     ├─ NO → displaySearchResults() failed
                                                     │        → Check console for errors
                                                     │
                                                     └─ YES → Results visible on page?
                                                               ├─ NO → CSS hiding elements
                                                               │        → Check element display property
                                                               │
                                                               └─ YES ✅ SUCCESS!
```

---

## Quick Test Command

To test everything end-to-end:

**Windows PowerShell**:
```powershell
# 1. Start backend (Terminal 1)
cd C:\Users\ASUS\OneDrive\Desktop\Findthem2\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Test API (Terminal 2)
# Use PowerShell to send request with image file
# Or open browser to http://localhost:8000

# 3. Open browser console (F12) and watch logs
```

---

**Last Updated**: January 23, 2026
