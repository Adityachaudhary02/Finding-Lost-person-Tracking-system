# API Response Examples - FindThem Face Search

## Search Endpoint Response

### Successful Search with Matches

**Endpoint**: `POST /api/search-face`

**Request**:
```
Content-Type: multipart/form-data
Body: image=[binary image file]
```

**Response (200 OK) - Matches Found**:
```json
{
  "success": true,
  "message": "Found 2 potential match(es)",
  "matches": [
    {
      "case_id": 6,
      "name": "aditya",
      "status": "found",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "description": "patna",
      "image_path": "20260122_190547_adi photo.jpg",
      "similarity_score": 0.8532,
      "similarity_percentage": 85.32
    },
    {
      "case_id": 7,
      "name": "aditya",
      "status": "found",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "description": "patna",
      "image_path": "20260122_192412_aditya pic form.jpg",
      "similarity_score": 0.7215,
      "similarity_percentage": 72.15
    }
  ],
  "total_cases_searched": 4,
  "threshold_used": 0.6,
  "search_time": "2026-01-23T00:43:15.647905"
}
```

**Frontend Behavior**:
```
1. Show green "✓ MATCH FOUND!" banner
2. Display both result cards:
   - #1 Match: aditya - 85.32% (Very High confidence)
   - #2 Match: aditya - 72.15% (High confidence)
3. Auto-scroll to results
4. Show: "Found 2 potential matches with 60%+ similarity"
```

---

### Successful Search - No Matches

**Response (200 OK) - No Matches Found**:
```json
{
  "success": true,
  "message": "Found 0 potential match(es)",
  "matches": [],
  "total_cases_searched": 4,
  "threshold_used": 0.6,
  "search_time": "2026-01-23T00:44:22.123456"
}
```

**Frontend Behavior**:
```
1. Hide loading spinner
2. Show "No Match Found" message with:
   - Large search icon
   - "No Match Found" heading
   - Explanation text
   - Suggestion to try different photo
3. Auto-scroll to no-results section
```

---

### Error: No Face Detected

**Response (400 Bad Request)**:
```json
{
  "detail": "No face detected in the image"
}
```

**Frontend Behavior**:
```
1. Hide loading spinner
2. Show alert modal:
   - Title: "Search Error"
   - Message: "No face detected in the image"
   - Suggests using clearer photo
```

---

### Error: Invalid File Format

**Response (400 Bad Request)**:
```json
{
  "detail": "Invalid file format. Allowed: jpg, jpeg, png, gif, bmp"
}
```

**Frontend Behavior**:
```
1. Hide loading spinner
2. Show alert modal:
   - Title: "Search Error"
   - Message: "Invalid file format..."
   - Suggests using jpg/png format
```

---

### Error: File Size Exceeds Limit

**Response (413 Payload Too Large)**:
```json
{
  "detail": "File size exceeds maximum limit"
}
```

**Frontend Behavior**:
```
1. Hide loading spinner
2. Show alert modal:
   - Title: "Search Error"
   - Message: "File size exceeds maximum limit"
   - Suggests compressing photo (max 10MB)
```

---

### Error: Database Empty

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "No cases in database",
  "matches": [],
  "total_cases_searched": 0,
  "threshold_used": 0.6,
  "search_time": "2026-01-23T00:45:30.234567"
}
```

**Frontend Behavior**:
```
1. Hide loading spinner
2. Show "No Match Found" message
3. Note: This means database has no cases registered yet
```

---

### Error: Backend Connection Issue

**Response (Connection Error)**:
```
No response - Connection refused or timeout
```

**Frontend Behavior**:
```
1. Catch error in try-catch block
2. Show alert modal:
   - Title: "Error"
   - Message: "Connection error. Make sure the backend is running."
   - Help user start backend
```

---

## Other API Endpoints

### Statistics Endpoint

**Endpoint**: `GET /api/stats`

**Response (200 OK)**:
```json
{
  "success": true,
  "statistics": {
    "total_cases": 4,
    "missing_persons": 2,
    "found_persons": 2
  }
}
```

**Purpose**: Display case statistics on homepage

---

### Health Check Endpoint

**Endpoint**: `GET /health`

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Purpose**: Verify backend and database are running

---

### Cases List Endpoint

**Endpoint**: `GET /api/cases?status=all&limit=50`

**Response (200 OK)**:
```json
{
  "success": true,
  "count": 4,
  "cases": [
    {
      "case_id": 7,
      "name": "aditya",
      "status": "found",
      "description": "patna",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "image_path": "20260122_192412_aditya pic form.jpg",
      "created_at": "2026-01-22T19:24:13"
    },
    {
      "case_id": 6,
      "name": "aditya",
      "status": "found",
      "description": "patna",
      "contact": "adityakumaR1632003@GMAIL.COM",
      "image_path": "20260122_190547_adi photo.jpg",
      "created_at": "2026-01-22T19:05:47"
    }
  ]
}
```

**Purpose**: Get all cases (hidden from UI, used for admin)

---

## Response Structure Explanation

### Match Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | Integer | Unique ID of case in database |
| `name` | String | Name of missing/found person |
| `status` | String | "missing" or "found" |
| `contact` | String | Email or phone of reporter |
| `description` | String | Details about person |
| `image_path` | String | Filename in uploads folder |
| `similarity_score` | Float | Raw score (0.0 to 1.0) |
| `similarity_percentage` | Float | Percentage (0.0 to 100.0) |

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | true if operation succeeded |
| `message` | String | Human-readable summary |
| `matches` | Array | List of matching results |
| `total_cases_searched` | Integer | Cases compared |
| `threshold_used` | Float | Similarity threshold (0.6) |
| `search_time` | String | ISO timestamp when search completed |

---

## Frontend Processing of Responses

### Search Result Display Logic

```javascript
// Step 1: Receive response
const data = response.json();

// Step 2: Check if successful
if (response.ok && data.success) {
  
  // Step 3: Filter matches >= 60%
  const filtered = data.matches.filter(m => m.similarity_percentage >= 60);
  
  // Step 4: If matches found
  if (filtered.length > 0) {
    
    // Show green banner
    matchBanner.style.display = 'block';
    
    // Build result cards for each match
    filtered.forEach((match, index) => {
      // Get photo URL
      const photoUrl = `http://localhost:8000/uploads/${match.image_path}`;
      
      // Determine confidence level
      let level = 'Good';
      if (match.similarity_percentage >= 80) level = 'Very High';
      else if (match.similarity_percentage >= 70) level = 'High';
      
      // Create card HTML with:
      // - Photo
      // - Name + Status badge
      // - Confidence bar
      // - Percentage
      // - Contact
      // - Details
    });
    
    // Display results
    searchResults.style.display = 'block';
    
  } else {
    
    // No matches - show no results message
    noResults.style.display = 'block';
  }
  
} else {
  
  // Error occurred - show error alert
  showAlert('error', 'Search Error', data.detail);
}
```

---

## Database Query Behind Search

```sql
-- 1. Get all cases
SELECT id, name, status, description, contact, image_path, embedding, created_at 
FROM cases;

-- 2. For each case:
-- - Load embedding vector from JSON
-- - Compare with uploaded photo embedding using cosine similarity
-- - Filter where similarity >= 0.6 (60%)
-- - Sort by similarity DESC
-- - Return top 10
```

---

## Similarity Score Calculation

```
Cosine Similarity = (A · B) / (||A|| × ||B||)

Where:
A = Embedding vector of uploaded photo (128 dimensions)
B = Embedding vector of database case (128 dimensions)
A · B = Dot product of vectors
||A|| = Magnitude/norm of vector A
||B|| = Magnitude/norm of vector B

Result ranges from 0.0 to 1.0:
- 0.0 = Completely different faces
- 0.5 = Some similarity
- 0.8 = Very similar faces
- 1.0 = Identical embeddings
```

---

## Example Flow with Real Data

### Step 1: User Uploads aditya.jpg

```
Request: POST /api/search-face
Body: [binary image data]
```

### Step 2: Backend Processes

```
1. Save temp file: temp_20260123_125030_aditya.jpg
2. Detect face: Found 1 face
3. Extract embedding: [0.12, 0.45, ..., 0.89] (128 values)
4. Load database cases:
   - Case 3: aditya (embedding loaded)
   - Case 4: Hanuman (embedding loaded)
   - Case 6: aditya (embedding loaded)
   - Case 7: aditya (embedding loaded)
5. Compare embeddings:
   - Case 3 vs uploaded: 0.623 (62.3%)
   - Case 4 vs uploaded: 0.412 (41.2%) ← Below threshold
   - Case 6 vs uploaded: 0.8532 (85.32%) ← Match!
   - Case 7 vs uploaded: 0.7215 (72.15%) ← Match!
6. Filter results (>= 0.6):
   - Match 1: Case 6 (85.32%)
   - Match 2: Case 7 (72.15%)
   - Match 3: Case 3 (62.3%)
7. Sort by score and return
```

### Step 3: Frontend Displays

```
✓ MATCH FOUND!

#1 Match
[Photo] aditya      [FOUND]
Match Confidence: Very High
[████████░░░] 85.32% Match
📧 Contact: adityakumaR1632003@GMAIL.COM
ℹ️ Details: patna

#2 Match
[Photo] aditya      [FOUND]
Match Confidence: High
[███████░░░░] 72.15% Match
📧 Contact: adityakumaR1632003@GMAIL.COM
ℹ️ Details: patna

#3 Match
[Photo] aditya      [MISSING]
Match Confidence: Good
[██████░░░░░] 62.30% Match
...
```

---

## Logging Output Example

**Backend Console Output**:
```
2026-01-23 12:50:30,123 - main - INFO - Starting search...
2026-01-23 12:50:30,234 - main - INFO - Image file saved: temp_20260123_125030_aditya.jpg
2026-01-23 12:50:30,456 - face_recognition_engine - INFO - Detected 1 face(s)
2026-01-23 12:50:30,678 - face_recognition_engine - INFO - Created embedding of length 128
2026-01-23 12:50:30,789 - main - INFO - Loaded 4 cases from database
2026-01-23 12:50:30,890 - face_recognition_engine - INFO - Searching 4 cases with threshold 0.6
2026-01-23 12:50:30,901 - face_recognition_engine - INFO - Case 6 similarity: 0.8532
2026-01-23 12:50:30,902 - face_recognition_engine - INFO - Case 7 similarity: 0.7215
2026-01-23 12:50:30,903 - face_recognition_engine - INFO - Case 3 similarity: 0.623
2026-01-23 12:50:30,904 - face_recognition_engine - INFO - Case 4 similarity: 0.412
2026-01-23 12:50:30,905 - face_recognition_engine - INFO - Found 3 potential matches
2026-01-23 12:50:30,906 - main - INFO - Search completed. Found 3 matches out of 4 cases. Threshold: 0.6
2026-01-23 12:50:30,907 - main - INFO -   - aditya: 85.32% match
2026-01-23 12:50:30,908 - main - INFO -   - aditya: 72.15% match
2026-01-23 12:50:30,909 - main - INFO -   - aditya: 62.30% match
```

---

**Last Updated**: January 23, 2026
**API Version**: 1.0.0
