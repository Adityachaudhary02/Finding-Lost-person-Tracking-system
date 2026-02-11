# FindThem Testing Guide

Complete testing procedures to validate all features of the FindThem application.

## Pre-Testing Setup

### 1. Verify Installation
```powershell
# Check Python version
python --version  # Should be 3.8+

# Check MySQL
mysql -u root -p -e "SELECT 1"

# Check dependencies
pip list | findstr fastapi
pip list | findstr deepface
```

### 2. Start Services

**Terminal 1 - Backend**
```powershell
cd backend
python main.py
# Expected: INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend**
```powershell
cd frontend
python -m http.server 8080
# Expected: Serving HTTP on 0.0.0.0 port 8080
```

---

## 📋 Manual Testing Checklist

### 1. Website Access

**Test**: Load main website
```
1. Open browser
2. Go to http://localhost:8080
3. Page should load without errors
```

**Expected Results**:
- ✅ Hero section visible
- ✅ Navigation bar present
- ✅ All sections accessible
- ✅ No console errors

---

### 2. Navigation

**Test**: Navigation between sections
```
1. Click "Report" in navbar
2. Scroll to Search section
3. Click "Cases" link
4. Go back to Home
```

**Expected Results**:
- ✅ Smooth scrolling
- ✅ Sections load properly
- ✅ Links work correctly

---

### 3. Case Upload

**Test**: Upload a missing person case

**Prerequisites**:
- Clear photo of a face (JPG/PNG)
- 100x100 pixels minimum

**Steps**:
```
1. Go to http://localhost:8080
2. Scroll to "Report a Missing or Found Person"
3. Fill in form:
   - Name: "Test Person 1"
   - Status: "Missing Person"
   - Description: "Test missing case"
   - Contact: "test@example.com"
4. Click photo upload box
5. Select image
6. Verify preview shows
7. Click "Submit Report"
8. Wait for confirmation
```

**Expected Results**:
- ✅ Photo preview displays correctly
- ✅ Loading message appears
- ✅ Success message shows
- ✅ Case appears in Cases section
- ✅ Statistics update (+1 missing)

**Test Edge Cases**:
```
1. Try uploading non-image file
   Expected: Error message about file format

2. Try uploading image without face
   Expected: Error about face detection

3. Try uploading 20MB file
   Expected: Error about file size limit

4. Try submitting with blank fields
   Expected: Form validation error
```

---

### 4. Case Search

**Test**: Search for similar faces

**Prerequisites**:
- Upload at least 2 test cases with different people
- Have test photos to search with

**Steps**:
```
1. Go to Search section
2. Click upload box
3. Drag or select image
4. Click "Search" button
5. Wait for results
6. Review matches with similarity scores
```

**Expected Results**:
- ✅ Image preview shows
- ✅ Loading animation appears
- ✅ Results display with images
- ✅ Similarity percentage visible
- ✅ Contact information shown
- ✅ "No matches" message if no results

**Test Searches**:
```
1. Search with same person (different photo)
   Expected: 80%+ match

2. Search with different person
   Expected: <50% match or no results

3. Search with partially visible face
   Expected: Lower match scores

4. Search with group photo
   Expected: Matches based on most prominent face
```

---

### 5. Case Gallery

**Test**: View and filter cases

**Steps**:
```
1. Go to "Cases" section
2. Review all cases displayed
3. Click "Missing" filter
4. Verify only missing cases show
5. Click "Found" filter
6. Verify only found cases show
7. Click "All Cases" filter
8. Verify all cases show again
```

**Expected Results**:
- ✅ Cases displayed in grid
- ✅ Proper images show
- ✅ Status badges correct
- ✅ Contact info visible
- ✅ Filter buttons work
- ✅ Cards display correctly

---

### 6. Statistics

**Test**: Dashboard statistics

**Steps**:
```
1. Load http://localhost:8080
2. Check hero section stats:
   - Total Cases count
   - Missing Persons count
   - Found Persons count
3. Upload new case
4. Refresh page
5. Verify counts updated
```

**Expected Results**:
- ✅ Stats display correctly
- ✅ Numbers increase after upload
- ✅ All three categories count correctly
- ✅ Stats update in real-time

---

### 7. Admin Panel Access

**Test**: Admin panel functionality

**Steps**:
```
1. Go to http://localhost:8080/admin.html
2. Verify layout loads
3. Check sidebar navigation
4. Click Dashboard (should be active)
5. Review stats
```

**Expected Results**:
- ✅ Page loads without errors
- ✅ Navigation sidebar visible
- ✅ Dashboard shows stats
- ✅ All panels present

---

### 8. Admin Case Management

**Test**: Delete cases from admin

**Steps**:
```
1. Go to Admin > Cases Management
2. Verify table loads with cases
3. Find a test case
4. Click Delete button
5. Confirm deletion
```

**Expected Results**:
- ✅ Cases table displays
- ✅ Delete button present
- ✅ Confirmation dialog appears
- ✅ Case removed from database
- ✅ Removed from gallery view

---

### 9. Admin Settings

**Test**: Adjust system settings

**Steps**:
```
1. Go to Admin > Settings
2. Adjust similarity threshold slider
3. Click "Save Changes"
4. Try a new search
5. Verify threshold affects results
```

**Expected Results**:
- ✅ Slider works
- ✅ Settings save
- ✅ Threshold affects matches
- ✅ Confirmation message shows

---

### 10. Responsive Design

**Test**: Mobile and tablet views

**Steps**:
```
1. Open DevTools (F12)
2. Toggle Device Toolbar
3. Test at various sizes:
   - iPhone SE (375x667)
   - iPad (768x1024)
   - Desktop (1920x1080)
4. Test all features at each size
```

**Expected Results**:
- ✅ Layout adapts properly
- ✅ Touch targets are large enough
- ✅ Text is readable
- ✅ Images resize correctly
- ✅ Navigation is accessible
- ✅ No horizontal scroll

---

## 🔌 API Testing

### 1. Health Check

**Test**: API is running

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Get Statistics

```bash
curl http://localhost:8000/api/stats
```

**Expected Response**:
```json
{
  "success": true,
  "statistics": {
    "total_cases": 2,
    "missing_persons": 1,
    "found_persons": 1
  }
}
```

### 3. Get All Cases

```bash
curl http://localhost:8000/api/cases
```

**Expected Response**:
```json
{
  "success": true,
  "count": 2,
  "cases": [...]
}
```

### 4. Upload Case with cURL

```bash
curl -X POST http://localhost:8000/api/upload-case \
  -F "name=Test User" \
  -F "status=missing" \
  -F "description=Test description" \
  -F "contact=test@test.com" \
  -F "image=@photo.jpg"
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Case uploaded successfully",
  "case_id": 3,
  "faces_detected": 1,
  "image_path": "20240122_XXXXXX_photo.jpg"
}
```

### 5. Search with cURL

```bash
curl -X POST http://localhost:8000/api/search-face \
  -F "image=@search.jpg"
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Found X potential match(es)",
  "matches": [...],
  "total_cases_searched": 2,
  "search_time": "2024-01-22T10:30:45.123456"
}
```

### 6. Get Case Details

```bash
curl http://localhost:8000/api/cases/1
```

**Expected Response**:
```json
{
  "success": true,
  "case": {
    "case_id": 1,
    "name": "Test Person",
    "status": "missing",
    ...
  }
}
```

### 7. Delete Case

```bash
curl -X DELETE "http://localhost:8000/api/cases/1?admin_password=admin123"
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Case deleted successfully"
}
```

---

## 🧪 Performance Testing

### 1. Upload Performance

**Test**: Measure upload time

```
1. Use a 2MB image
2. Time the upload
3. Expected: 2-3 seconds
```

### 2. Search Performance

**Test**: Measure search time

```
1. Upload 10 different cases
2. Search for a matching face
3. Expected: <2 seconds
```

### 3. Concurrent Requests

**Test**: Multiple simultaneous uploads

```bash
# Terminal 1
curl -F "image=@photo1.jpg" http://localhost:8000/api/upload-case

# Terminal 2 (same time)
curl -F "image=@photo2.jpg" http://localhost:8000/api/upload-case

# Terminal 3 (same time)
curl -F "image=@photo3.jpg" http://localhost:8000/api/upload-case
```

**Expected Results**:
- ✅ All succeed without conflicts
- ✅ Response times are consistent

---

## 🔒 Security Testing

### 1. File Upload Validation

**Test**: Invalid file formats

```bash
# Try uploading .txt file
curl -F "image=@file.txt" http://localhost:8000/api/upload-case

# Expected: Error about invalid format
```

### 2. File Size Limit

**Test**: File size limit

```bash
# Create 15MB file
# Try to upload

# Expected: Error about size limit
```

### 3. Admin Password

**Test**: Delete without password

```bash
curl -X DELETE http://localhost:8000/api/cases/1

# Expected: 401 Unauthorized
```

**Test**: Delete with wrong password

```bash
curl -X DELETE "http://localhost:8000/api/cases/1?admin_password=wrong"

# Expected: 401 Unauthorized
```

**Test**: Delete with correct password

```bash
curl -X DELETE "http://localhost:8000/api/cases/1?admin_password=admin123"

# Expected: 200 Success
```

### 4. CORS Testing

**Test**: Cross-origin requests

```javascript
// From different domain, this should work:
fetch('http://localhost:8000/api/stats')
  .then(r => r.json())
  .then(console.log)

// Expected: Success (CORS enabled)
```

---

## 🗄️ Database Testing

### 1. Data Persistence

**Test**: Case survives restart

```
1. Upload a case
2. Note the case ID
3. Restart backend
4. Query the case
5. Should still exist
```

### 2. Database Integrity

```sql
-- Check cases table
SELECT COUNT(*) FROM cases;

-- Check embeddings exist
SELECT CASE WHEN embedding IS NOT NULL THEN 'OK' ELSE 'FAIL' END FROM cases LIMIT 5;

-- Check indexes
SHOW INDEXES FROM cases;
```

### 3. Search History

```sql
-- Verify search history table exists
SELECT COUNT(*) FROM search_history;

-- Check structure
DESC search_history;
```

---

## 📊 Load Testing

### Simple Load Test

```bash
# Install Apache Bench
# Test with 100 requests, 10 concurrent

ab -n 100 -c 10 http://localhost:8000/api/stats
ab -n 100 -c 10 http://localhost:8000/api/cases
```

**Expected**:
- ✅ All requests succeed
- ✅ Response time <1s average
- ✅ No timeout errors

---

## 🐛 Error Handling Testing

### 1. Invalid Input

**Test**: Empty name field
```
1. Try submitting without name
2. Expected: Form validation error
```

**Test**: Invalid email
```
1. Try submitting with "invalid"
2. Expected: Form validation error
```

### 2. Server Errors

**Test**: Stop database, try upload
```
1. Stop MySQL service
2. Try uploading case
3. Expected: Graceful error message
4. Restart MySQL
5. Try again - should work
```

### 3. Network Errors

**Test**: No internet connection
```
1. Disconnect internet
2. Try search (with cached case)
3. Try upload (should fail)
4. Expected: Clear error message
```

---

## ✅ Final Checklist

### Frontend
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Case upload successful
- [ ] Search works with results
- [ ] Case gallery displays
- [ ] Statistics update
- [ ] Responsive design works
- [ ] Admin panel loads
- [ ] Admin features work

### Backend
- [ ] API running on port 8000
- [ ] All 8 endpoints working
- [ ] Upload validates files
- [ ] Face detection works
- [ ] Search returns results
- [ ] Database operations work
- [ ] Error handling works

### Database
- [ ] Tables created
- [ ] Data persists
- [ ] Queries execute fast
- [ ] Indexes work
- [ ] Constraints enforced

### Performance
- [ ] Upload <3s
- [ ] Search <2s
- [ ] Responsive design
- [ ] Load handling

### Security
- [ ] File validation
- [ ] Size limits
- [ ] Input sanitization
- [ ] Admin protection
- [ ] CORS working

---

## 🎯 Testing Conclusion

Once all tests pass:
1. Application is ready for staging
2. Can proceed with load testing
3. Ready for production deployment

---

## 📝 Test Report Template

```
Date: ___________
Tester: ___________
Environment: Development / Staging / Production

Feature: ___________
Status: ✅ PASS / ❌ FAIL
Issues: ___________
Screenshots: ___________

Recommendations:
___________

Sign-off: ___________
```

---

## 🔗 Quick Links

- QUICKSTART.md - Setup guide
- API_DOCUMENTATION.md - API reference
- README.md - Full documentation
- DEPLOYMENT.md - Deployment guide

---

**Happy Testing!** 🚀
