# FindThem API Documentation

Complete API reference for the FindThem Lost and Found Person Search system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses admin password for protected endpoints. Upgrade to token-based auth for production.

## Endpoints

### 1. Root Endpoint

**GET** `/`

Get basic API information.

**Response:**
```json
{
  "message": "FindThem - Lost and Found Person Search API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 2. Health Check

**GET** `/health`

Check API and database status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### 3. Upload Case

**POST** `/api/upload-case`

Upload a new missing or found person case with photo.

**Parameters (Form Data):**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Full name of the person |
| status | string | Yes | "missing" or "found" |
| description | string | Yes | Details about the person |
| contact | string | Yes | Email or phone number |
| image | file | Yes | Photo (JPG, PNG, GIF, BMP, max 10MB) |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/upload-case \
  -F "name=John Doe" \
  -F "status=missing" \
  -F "description=Missing since yesterday, last seen in downtown area" \
  -F "contact=john.family@email.com" \
  -F "image=@photo.jpg"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Case uploaded successfully",
  "case_id": 1,
  "faces_detected": 1,
  "image_path": "20240122_101530_photo.jpg"
}
```

**Error Responses:**
- 400: Invalid file format or no face detected
- 413: File size exceeds maximum limit
- 500: Server error

---

### 4. Search for Similar Faces

**POST** `/api/search-face`

Search for similar faces in the database.

**Parameters (Form Data):**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| image | file | Yes | Query photo (JPG, PNG, GIF, BMP, max 10MB) |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/search-face \
  -F "image=@search_photo.jpg"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Found 3 potential match(es)",
  "matches": [
    {
      "case_id": 1,
      "name": "John Doe",
      "status": "missing",
      "contact": "john.family@email.com",
      "description": "Missing since yesterday...",
      "image_path": "20240122_101530_photo.jpg",
      "similarity_score": 0.8543,
      "similarity_percentage": 85.43
    },
    {
      "case_id": 2,
      "name": "Jane Smith",
      "status": "found",
      "contact": "jane@email.com",
      "description": "Found in shelter",
      "image_path": "20240121_143022_photo.png",
      "similarity_score": 0.7211,
      "similarity_percentage": 72.11
    }
  ],
  "total_cases_searched": 15,
  "search_time": "2024-01-22T10:30:45.123456"
}
```

**Error Responses:**
- 400: Invalid file format or no face detected
- 413: File size exceeds maximum limit
- 500: Server error

---

### 5. Get All Cases

**GET** `/api/cases`

Retrieve all cases, optionally filtered by status.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Optional: "missing" or "found" |
| limit | integer | Optional: max results (default: 50) |

**Example Requests:**
```bash
# Get all cases
curl http://localhost:8000/api/cases

# Get only missing cases
curl http://localhost:8000/api/cases?status=missing

# Get 10 most recent cases
curl http://localhost:8000/api/cases?limit=10
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "cases": [
    {
      "case_id": 1,
      "name": "John Doe",
      "status": "missing",
      "description": "Missing since yesterday...",
      "contact": "john.family@email.com",
      "image_path": "20240122_101530_photo.jpg",
      "created_at": "2024-01-22T10:15:30"
    },
    {
      "case_id": 2,
      "name": "Jane Smith",
      "status": "found",
      "description": "Found in shelter",
      "contact": "jane@email.com",
      "image_path": "20240121_143022_photo.png",
      "created_at": "2024-01-21T14:30:22"
    }
  ]
}
```

---

### 6. Get Case Details

**GET** `/api/cases/{case_id}`

Get detailed information about a specific case.

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| case_id | integer | The ID of the case |

**Example Request:**
```bash
curl http://localhost:8000/api/cases/1
```

**Response:**
```json
{
  "success": true,
  "case": {
    "case_id": 1,
    "name": "John Doe",
    "status": "missing",
    "description": "Missing since yesterday, last seen in downtown area",
    "contact": "john.family@email.com",
    "image_path": "20240122_101530_photo.jpg",
    "created_at": "2024-01-22T10:15:30"
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Case not found"
}
```

---

### 7. Delete Case

**DELETE** `/api/cases/{case_id}`

Delete a case (requires admin password).

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| case_id | integer | The ID of the case |
| admin_password | string | Admin password (query param) |

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/cases/1?admin_password=admin123"
```

**Success Response:**
```json
{
  "success": true,
  "message": "Case deleted successfully"
}
```

**Error Responses:**
- 401: Unauthorized (wrong password)
- 404: Case not found

---

### 8. Get Statistics

**GET** `/api/stats`

Get system statistics.

**Example Request:**
```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_cases": 42,
    "missing_persons": 25,
    "found_persons": 17
  }
}
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (invalid password) |
| 404 | Not found |
| 413 | Payload too large |
| 500 | Server error |

---

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Error description"
}
```

### Common Errors

**No face detected:**
```json
{
  "detail": "No face detected in the image"
}
```

**Invalid file type:**
```json
{
  "detail": "Invalid file format. Allowed: jpg, jpeg, png, gif, bmp"
}
```

**File too large:**
```json
{
  "detail": "File size exceeds maximum limit"
}
```

---

## Request Examples

### Python

```python
import requests

# Upload case
with open('photo.jpg', 'rb') as f:
    files = {'image': f}
    data = {
        'name': 'John Doe',
        'status': 'missing',
        'description': 'Missing person',
        'contact': 'contact@email.com'
    }
    response = requests.post('http://localhost:8000/api/upload-case', 
                           files=files, data=data)
    print(response.json())

# Search face
with open('search.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:8000/api/search-face', 
                           files=files)
    print(response.json())

# Get all cases
response = requests.get('http://localhost:8000/api/cases')
print(response.json())

# Get stats
response = requests.get('http://localhost:8000/api/stats')
print(response.json())
```

### JavaScript/Fetch

```javascript
// Upload case
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('status', 'missing');
formData.append('description', 'Missing person');
formData.append('contact', 'contact@email.com');
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/api/upload-case', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => console.log(data));

// Search
const searchFormData = new FormData();
searchFormData.append('image', searchInput.files[0]);

fetch('http://localhost:8000/api/search-face', {
    method: 'POST',
    body: searchFormData
})
.then(res => res.json())
.then(data => console.log(data));

// Get cases
fetch('http://localhost:8000/api/cases')
    .then(res => res.json())
    .then(data => console.log(data));
```

### cURL

```bash
# Upload case
curl -X POST http://localhost:8000/api/upload-case \
  -F "name=John Doe" \
  -F "status=missing" \
  -F "description=Missing person" \
  -F "contact=contact@email.com" \
  -F "image=@photo.jpg"

# Search face
curl -X POST http://localhost:8000/api/search-face \
  -F "image=@search.jpg"

# Get all cases
curl http://localhost:8000/api/cases

# Get missing cases only
curl http://localhost:8000/api/cases?status=missing

# Get case details
curl http://localhost:8000/api/cases/1

# Get statistics
curl http://localhost:8000/api/stats

# Delete case
curl -X DELETE "http://localhost:8000/api/cases/1?admin_password=admin123"
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, add rate limiting to prevent abuse.

---

## CORS

CORS is enabled for all origins. Restrict in production by modifying `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Webhooks

Future feature: Automatic notifications when matches are found.

---

## Pagination

Implemented via `limit` parameter. Default: 50, Max: 1000

---

## Sorting

Cases are sorted by `created_at` DESC (newest first) by default.

---

## Filtering

Supported filters:
- `status`: "missing" or "found"
- `limit`: number of results

---

## Performance Metrics

- Average upload time: 2-3 seconds
- Average search time: 1-2 seconds per 1000 cases
- Database query time: <100ms

---

## Version

Current API Version: **1.0.0**

---

## Support

For issues or questions, refer to README.md or contact support.

---

## Changelog

### Version 1.0.0
- Initial release
- Core face recognition functionality
- Case management
- Search capabilities
- Admin panel
