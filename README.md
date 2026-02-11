# FindThem - Lost and Found Person Search Website

An AI-powered platform that uses advanced face recognition technology to help locate missing persons and reunite families.

## Features

### Core Features
- **AI Face Recognition**: Uses DeepFace and FaceNet models for accurate face detection and matching
- **Real-time Search**: Search for similar faces against a database of cases
- **Case Management**: Upload and manage missing/found person cases
- **Similarity Matching**: Get similarity scores and confidence percentages for matched faces
- **Responsive Design**: Modern, mobile-friendly interface with smooth animations
- **Admin Panel**: Comprehensive dashboard for system management and case administration

### Frontend Features
- Beautiful, modern UI with gradient backgrounds and smooth animations
- Drag-and-drop image upload
- Real-time image preview
- Mobile-responsive design
- Instant search results with similarity scores
- Case filtering by status (missing/found)
- Live statistics dashboard

### Backend Features
- FastAPI-based REST API
- Secure image upload handling
- Face detection and embedding generation
- Efficient face comparison algorithms
- Case management endpoints
- Statistics and reporting

### Admin Features
- Dashboard with system statistics
- Case management and deletion
- Search history tracking
- Admin user management
- Settings and configuration
- Database backup and optimization

## Project Structure

```
Findthem2/
├── backend/
│   ├── config.py                    # Configuration settings
│   ├── database.py                  # Database connection and operations
│   ├── face_recognition_engine.py   # Face detection and matching logic
│   ├── main.py                      # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── uploads/                     # Uploaded image storage
│   └── face_models/                 # Model files storage
├── frontend/
│   ├── index.html                   # Main website
│   ├── admin.html                   # Admin panel
│   ├── styles.css                   # Main website styles
│   ├── admin-styles.css             # Admin panel styles
│   ├── script.js                    # Main website JavaScript
│   └── admin-script.js              # Admin panel JavaScript
├── database/
│   ├── schema.sql                   # Database schema
│   └── init_db.py                   # Database initialization script
└── .env.example                     # Environment variables template
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Node.js (optional, for local development server)
- pip (Python package manager)

### Step 1: Clone/Setup Project

```bash
cd c:\Users\ASUS\OneDrive\Desktop\Findthem2
```

### Step 2: Setup Database

1. Ensure MySQL is running on your system
2. Run the initialization script:

```bash
cd database
python init_db.py
```

This will create the `findthem_db` database and all required tables.

### Step 3: Setup Backend

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Note: First-time installation may take several minutes as it downloads face recognition models (~200MB).

4. Create `.env` file from template:

```bash
copy .env.example .env
```

5. Edit `.env` with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=findthem_db
```

### Step 4: Run the Backend

From the `backend` directory:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Step 5: Serve the Frontend

Option 1: Using Python's built-in server (in frontend directory):

```bash
cd frontend
python -m http.server 8080
```

Option 2: Using Node.js:

```bash
cd frontend
npx http-server -p 8080
```

Option 3: Open `frontend/index.html` directly in your browser

Visit: `http://localhost:8080`

## API Endpoints

### Case Management
- **POST** `/api/upload-case` - Upload a new case with image
  - Parameters: name, status, description, contact, image
  
- **GET** `/api/cases` - Get all cases (optional filter by status)
  - Query: `?status=missing` or `?status=found`
  
- **GET** `/api/cases/{case_id}` - Get specific case details

- **DELETE** `/api/cases/{case_id}` - Delete a case
  - Query: `?admin_password=your_password`

### Search
- **POST** `/api/search-face` - Search for similar faces
  - Body: image file

### Statistics
- **GET** `/api/stats` - Get system statistics

### Health
- **GET** `/health` - Check API health
- **GET** `/` - Root endpoint

## Configuration

### Similarity Threshold
The default similarity threshold is 0.6 (60%). Adjust in `backend/config.py`:

```python
SIMILARITY_THRESHOLD = 0.6  # Range: 0-1
```

Higher values = stricter matching (fewer false positives)
Lower values = more lenient matching (more potential matches)

### Admin Password
Change the admin password in `.env`:

```env
ADMIN_PASSWORD=your_secure_password
```

### Upload Folder
Maximum file size: 10MB (configured in `config.py`)
Allowed formats: JPG, PNG, GIF, BMP

## Database Schema

### Cases Table
- Stores information about missing/found persons
- Contains face embeddings for comparison
- Tracks case status and resolution

### Search History Table
- Logs all search queries
- Records matched cases and similarity scores

### Admin Users Table
- Stores admin user credentials
- Tracks last login time

### Activity Log Table
- Records all system actions
- Useful for audit trails

## Face Recognition Models

The system uses:
- **MTCNN**: For accurate face detection
- **FaceNet**: For generating face embeddings
- **Euclidean Distance**: For similarity calculation

Models are automatically downloaded on first run (~200MB).

## Performance Considerations

1. **Face Detection**: ~0.5-1s per image
2. **Embedding Generation**: ~0.3-0.7s per face
3. **Search through 1000 cases**: ~1-2 seconds
4. **Database Indexing**: Optimized for quick status-based queries

## Troubleshooting

### Backend Won't Start
- Ensure MySQL is running: `mysql -u root`
- Check if port 8000 is available: `netstat -ano | findstr :8000`
- Verify Python version: `python --version` (requires 3.8+)

### Face Detection Fails
- Ensure image has a clear, frontal face
- Check image format (JPG, PNG recommended)
- Try a higher resolution image

### Database Connection Error
- Verify MySQL credentials in `.env`
- Check database exists: `mysql -u root -e "SHOW DATABASES;"`
- Ensure MySQL service is running

### Slow Search
- Check database indexes are created
- Reduce similarity threshold in admin settings
- Add more system RAM for faster processing

### CORS Errors
- Ensure frontend is running on different port than backend
- Check CORS configuration in `main.py` (currently allows all origins)

## Security Recommendations

For production deployment:

1. Change all default passwords
2. Use HTTPS/SSL certificates
3. Implement rate limiting
4. Add authentication to admin endpoints
5. Use environment variables for sensitive data
6. Implement input validation and sanitization
7. Use secure database credentials
8. Enable database backups
9. Implement access control
10. Regular security audits

## Future Enhancements

- Email notifications for matches
- Multiple face detection per image
- Advanced filtering options
- Integration with law enforcement databases
- Real-time notifications
- Mobile app version
- Machine learning model fine-tuning
- Advanced analytics dashboard
- Case resolved workflow
- Photo comparison verification

## License

This project is open source and available for research and educational purposes.

## Support

For issues, questions, or suggestions, please refer to the documentation or contact the development team.

## Credits

Built with:
- FastAPI
- DeepFace
- Face Recognition
- MySQL
- Modern CSS/JavaScript

## Contact

For more information about FindThem, visit the website or contact the development team.

---

**Note**: This application is designed to assist in finding lost persons. Always involve proper authorities when reporting missing persons.
