# FindThem System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌──────────────────────┐       │
│  │   Main Website       │         │   Admin Dashboard    │       │
│  │   (index.html)       │         │   (admin.html)       │       │
│  │                      │         │                      │       │
│  │ • Report Cases       │         │ • Manage Cases       │       │
│  │ • Search Faces       │         │ • View Statistics    │       │
│  │ • View Results       │         │ • Settings           │       │
│  │ • Live Statistics    │         │ • User Management    │       │
│  └──────────────────────┘         └──────────────────────┘       │
│           │                                │                      │
│           └────────────────┬─────────────────┘                    │
│                            │                                      │
│           ┌────────────────▼──────────────────┐                   │
│           │    Frontend JavaScript Layer      │                   │
│           │   (script.js, admin-script.js)    │                   │
│           │                                   │                   │
│           │  • API Communication              │                   │
│           │  • Event Handling                 │                   │
│           │  • DOM Manipulation               │                   │
│           │  • Form Processing                │                   │
│           └────────────────┬──────────────────┘                   │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                    HTTP/HTTPS Requests
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                    API GATEWAY LAYER (FastAPI)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           FastAPI Application (main.py)                │   │
│  │                                                          │   │
│  │  8 REST Endpoints:                                      │   │
│  │  • GET /                       (Health check)          │   │
│  │  • GET /health                 (Status)                │   │
│  │  • POST /api/upload-case       (Case upload)           │   │
│  │  • POST /api/search-face       (Face search)           │   │
│  │  • GET /api/cases              (Get all cases)         │   │
│  │  • GET /api/cases/{id}         (Get case details)      │   │
│  │  • DELETE /api/cases/{id}      (Delete case)           │   │
│  │  • GET /api/stats              (Get statistics)        │   │
│  │                                                          │   │
│  │  Middleware:                                            │   │
│  │  • CORS Support                                         │   │
│  │  • Error Handling                                       │   │
│  │  • Request Validation                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   DATABASE    │  │  FILE STORAGE   │  │  FACE RECOGNITION
│    LAYER      │  │     LAYER       │  │   ENGINE LAYER
└───────┬───────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        │                    │                    │
```

## Component Breakdown

### 1. Frontend Layer

```
frontend/
├── index.html (700 lines)
│   ├── Navigation Bar
│   ├── Hero Section
│   ├── Report Case Form
│   ├── Search Interface
│   ├── Cases Gallery
│   ├── About Section
│   └── Modals & Alerts
│
├── admin.html (400 lines)
│   ├── Sidebar Navigation
│   ├── Top Bar
│   ├── Dashboard Page
│   ├── Cases Management
│   ├── Search History
│   ├── Admin Users
│   ├── Settings Page
│   └── Modal Dialogs
│
├── styles.css (1000+ lines)
│   ├── Root Variables
│   ├── Navbar Styling
│   ├── Hero Section
│   ├── Buttons & Forms
│   ├── Cards & Grids
│   ├── Animations
│   └── Responsive Design
│
└── script.js (400 lines)
    ├── API Configuration
    ├── Event Listeners
    ├── Form Handling
    ├── File Upload Logic
    ├── Search Functionality
    ├── Case Management
    ├── Statistics Loading
    └── Modal Management
```

### 2. Backend Layer

```
backend/
├── main.py (550 lines)
│   ├── FastAPI Setup
│   ├── CORS Configuration
│   ├── Database Connection
│   │
│   ├── Endpoints:
│   │  ├── POST /api/upload-case
│   │  │  └─► Validate → Process → Store
│   │  │
│   │  ├── POST /api/search-face
│   │  │  └─► Extract → Compare → Return Results
│   │  │
│   │  ├── GET /api/cases
│   │  │  └─► Query DB → Return List
│   │  │
│   │  ├── GET /api/cases/{id}
│   │  │  └─► Query DB → Return Details
│   │  │
│   │  ├── DELETE /api/cases/{id}
│   │  │  └─► Authenticate → Delete → Clean Files
│   │  │
│   │  └── GET /api/stats
│   │     └─► Count Cases → Return Stats
│   │
│   ├── Startup/Shutdown Events
│   └── Error Handling
│
├── config.py (50 lines)
│   ├── Database Config
│   ├── Upload Settings
│   ├── Face Recognition Config
│   ├── Security Config
│   └── API Configuration
│
├── database.py (120 lines)
│   ├── Database Class
│   ├── Connection Management
│   ├── Query Execution
│   ├── Insert Operations
│   └── Error Handling
│
└── face_recognition_engine.py (200 lines)
    ├── Face Detection
    │  └─► MTCNN Model
    │
    ├── Embedding Generation
    │  └─► FaceNet Model
    │
    ├── Face Comparison
    │  └─► Euclidean Distance
    │
    ├── Similar Face Finding
    │  └─► Threshold Matching
    │
    └── Image Validation
       └─► Face Presence Check
```

### 3. Database Layer

```
MySQL Database (findthem_db)
│
├── cases Table
│   ├── id (Primary Key)
│   ├── name (varchar)
│   ├── status (enum: missing/found)
│   ├── description (text)
│   ├── contact (varchar)
│   ├── image_path (varchar)
│   ├── embedding (longtext - JSON array)
│   ├── is_resolved (boolean)
│   ├── resolved_at (timestamp)
│   ├── notes (text)
│   ├── created_at (timestamp)
│   ├── updated_at (timestamp)
│   └── Indexes:
│       ├── idx_status
│       ├── idx_created_at
│       └── idx_is_resolved
│
├── search_history Table
│   ├── id (Primary Key)
│   ├── query_image_path (varchar)
│   ├── matched_case_id (FK)
│   ├── similarity_score (float)
│   ├── search_timestamp (timestamp)
│   └── Index: idx_search_timestamp
│
├── admin_users Table
│   ├── id (Primary Key)
│   ├── username (varchar)
│   ├── password_hash (varchar)
│   ├── email (varchar)
│   ├── last_login (timestamp)
│   ├── created_at (timestamp)
│   └── is_active (boolean)
│
└── activity_log Table
    ├── id (Primary Key)
    ├── action (varchar)
    ├── case_id (FK)
    ├── details (text)
    ├── created_at (timestamp)
    └── Index: idx_action, idx_created_at
```

### 4. Face Recognition Pipeline

```
User Upload Photo
        │
        ▼
File Validation
├─ Check file extension
├─ Check file size
└─ Check image format
        │
        ▼
Save to Disk
(uploads/ folder)
        │
        ▼
Face Detection (MTCNN)
├─ Load image
├─ Detect faces
└─ Validate presence
        │
        ▼
Extract Face Region
(Crop detected face)
        │
        ▼
Generate Embedding (FaceNet)
├─ Run through model
├─ Get 128-dim vector
└─ Normalize values
        │
        ▼
Store in Database
├─ Save embedding as JSON
├─ Link to case
└─ Index for search
        │
        ▼
User → Search with Photo
        │
        ▼
Repeat: Detect → Extract → Embed
        │
        ▼
Compare with Database
├─ Calculate distance (Euclidean)
├─ Convert to similarity (0-1)
└─ Apply threshold
        │
        ▼
Return Matches
├─ Sort by similarity
├─ Limit to top 10
└─ Return with scores
```

## Data Flow Diagrams

### Upload Case Flow

```
User Interface
    │
    ├─ Form: Name, Status, Description, Contact, Photo
    │
    ▼
submit_form() [script.js]
    │
    ├─ Validate inputs
    ├─ Read file
    └─ Create FormData
    │
    ▼
POST /api/upload-case
    │
    ▼
upload_case() [main.py]
    │
    ├─ Validate file
    ├─ Save to disk
    ├─ Detect faces
    ├─ Generate embedding
    └─ Insert into DB
    │
    ▼
return { success: true, case_id: 1, faces_detected: 1 }
    │
    ▼
Show Success Message
Load Updated Statistics
```

### Search Face Flow

```
User Interface
    │
    ├─ Select photo to search
    │
    ▼
handleSearch() [script.js]
    │
    ├─ Validate file
    ├─ Create FormData
    └─ Show loading message
    │
    ▼
POST /api/search-face
    │
    ▼
search_face() [main.py]
    │
    ├─ Validate file
    ├─ Save temp file
    ├─ Detect face
    ├─ Generate embedding
    │
    ├─ Fetch all cases from DB
    │
    ├─ For each case:
    │   ├─ Load embedding
    │   ├─ Calculate similarity
    │   ├─ Compare to threshold
    │   └─ Keep if > threshold
    │
    ├─ Sort by similarity
    ├─ Limit to top 10
    └─ Clean temp files
    │
    ▼
return { success: true, matches: [...], total_searched: 42 }
    │
    ▼
displaySearchResults() [script.js]
    │
    ├─ Build result cards
    ├─ Show similarity bars
    └─ Display contact info
    │
    ▼
User sees matching cases with confidence scores
```

## Technology Interactions

```
┌─ JavaScript ─┐
│              │
│ Browser ────────► FastAPI
│ (Frontend)        │
│                   ├─────────────────────────────┐
│ ◄──────────────────                             │
│ JSON Response     │                             │
│                   │                             │
└──────────────┘    │                             │
                    │                             │
             ┌──────▼─────────┐                   │
             │   FastAPI      │                   │
             │   (Python)     │                   │
             └────────┬───────┘                   │
                      │                           │
        ┌─────────────┼────────────────────┐      │
        │             │                    │      │
        ▼             ▼                    ▼      │
    ┌────────┐  ┌─────────┐  ┌──────────────────┐│
    │ MySQL  │  │  Files  │  │ Face Recognition ││
    │ DB     │  │ Storage │  │ Engines          ││
    │        │  │         │  │ • MTCNN          ││
    │ Cases  │  │uploads/ │  │ • FaceNet        ││
    │ Logs   │  │ Folder  │  │ • Comparison     ││
    │ Users  │  │         │  └──────────────────┘│
    └────────┘  └─────────┘                      │
                                                 │
    └─────────────────────────────────────────────┘
             All from Backend Container
```

## Deployment Architecture

```
For Production:

┌────────────────────────────────────────────────────┐
│              Frontend - Web Server                  │
│  (Nginx / Apache / Cloud Storage)                   │
│  • Serves index.html                               │
│  • Serves admin.html                               │
│  • Proxies /api requests to backend                │
│  • Handles SSL/TLS                                 │
└────────────────────────────────────────────────────┘
                      │
            ┌─────────▼─────────┐
            │   Load Balancer   │
            └─────────┬─────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Backend │  │Backend │  │Backend │
    │ API #1 │  │ API #2 │  │ API #3 │
    └────────┘  └────────┘  └────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │  Managed MySQL Database   │
        │  (RDS / Cloud SQL)        │
        │                           │
        │ • findthem_db            │
        │ • Replicated             │
        │ • Backed up daily        │
        │ • Read replicas          │
        └───────────────────────────┘

        ┌──────────────────────────┐
        │  File Storage            │
        │  (S3 / Cloud Storage)    │
        │                          │
        │ • Uploaded images       │
        │ • CDN distribution      │
        │ • Encrypted             │
        └──────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│         HTTPS/TLS Encryption            │
│         (Port 443)                      │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      Web Application Firewall           │
│      • DDoS Protection                  │
│      • Rate Limiting                    │
│      • Request Filtering                │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      FastAPI Application                │
│      • CORS Validation                  │
│      • Input Sanitization               │
│      • Admin Authentication             │
└────────────────────┬────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │ MySQL  │  │ Files  │  │ Models   │
    │ Secure │  │Isolated│  │ Storage  │
    │Creds   │  │Perms   │  │ Secure   │
    └────────┘  └────────┘  └──────────┘
```

---

This architecture provides:
- ✅ Scalability (horizontal scaling via load balancer)
- ✅ Reliability (redundant components)
- ✅ Security (layered defense)
- ✅ Performance (optimized database, caching)
- ✅ Maintainability (modular design)
