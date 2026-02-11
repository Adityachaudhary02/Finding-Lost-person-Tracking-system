from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
import logging
from datetime import datetime
import json
from pathlib import Path
from contextlib import asynccontextmanager

# Add backend directory to path to avoid naming conflicts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
import database as db_module
from face_recognition_engine import face_engine
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, SIMILARITY_THRESHOLD, ADMIN_PASSWORD

db = db_module.db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============ LIFESPAN MANAGEMENT ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting FindThem API...")
    if db.connect():
        logger.info("Database connected successfully")
        
        # Auto-backup on startup
        try:
            from backup import backup_database
            backup_database()
            logger.info("Auto-backup completed on startup")
        except Exception as e:
            logger.warning(f"Auto-backup failed: {e}")
    else:
        logger.error("Failed to connect to database")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FindThem API...")
    db.disconnect()


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="FindThem - Lost and Found Person Search",
    description="AI-powered face recognition system for finding lost persons",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# Mount frontend static files
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
if os.path.exists(FRONTEND_FOLDER):
    app.mount("/static", StaticFiles(directory=FRONTEND_FOLDER), name="static")


# ============ UTILITY FUNCTIONS ============

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_content, filename):
    """Save uploaded file to disk"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)
        return filepath
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


# ============ FRONTEND ROUTES ============

@app.get("/admin")
async def serve_admin():
    """Serve admin panel"""
    admin_file = os.path.join(FRONTEND_FOLDER, 'admin.html')
    if os.path.exists(admin_file):
        return FileResponse(admin_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Admin panel not found")


@app.get("/index")
async def serve_index():
    """Serve main website"""
    index_file = os.path.join(FRONTEND_FOLDER, 'index.html')
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Index not found")


# ============ API ENDPOINTS ============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FindThem - Lost and Found Person Search API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db.connection else "disconnected"
    }


@app.post("/api/admin/login")
async def admin_login(password: str = Form(...)):
    """Authenticate admin user"""
    try:
        from config import ADMIN_PASSWORD as CORRECT_PASSWORD
        
        logger.info("Admin login attempt")
        
        if not password or password != CORRECT_PASSWORD:
            logger.warning("Failed admin login attempt - invalid password")
            return {
                "success": False,
                "message": "Invalid admin password",
                "authenticated": False
            }
        
        logger.info("Successful admin login")
        return {
            "success": True,
            "message": "Admin authenticated successfully",
            "authenticated": True
        }
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return {
            "success": False,
            "message": "Login error",
            "authenticated": False
        }


@app.post("/api/upload-case")
async def upload_case(
    name: str = Form(...),
    status: str = Form(...),  # "missing" or "found"
    description: str = Form(...),
    contact: str = Form(...),
    image: UploadFile = File(...)
):
    """Upload a new case with image"""
    try:
        # Validate status field
        if not status or status not in ['missing', 'found']:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'missing' or 'found'")
        # Validate image file
        if not allowed_file(image.filename):
            raise HTTPException(status_code=400, detail="Invalid file format. Allowed: jpg, jpeg, png, gif, bmp")
        
        # Read file content
        file_content = await image.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds maximum limit")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + image.filename
        
        # Save file
        filepath = save_uploaded_file(file_content, filename)
        if not filepath:
            raise HTTPException(status_code=500, detail="Failed to save image")
        
        # Validate face in image
        has_face, face_count = face_engine.validate_image(filepath)
        if not has_face:
            os.remove(filepath)
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        # Get face embedding
        embedding = face_engine.get_face_embedding(filepath)
        if embedding is None:
            os.remove(filepath)
            raise HTTPException(status_code=500, detail="Failed to process face")
        
        logger.info(f"Got embedding, type: {type(embedding)}, length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
        
        # Insert into database
        query = """
        INSERT INTO cases (name, status, description, contact, image_path, embedding, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            embedding_json = json.dumps(embedding)
            logger.info(f"Embedding JSON created, length: {len(embedding_json)}")
        except Exception as e:
            logger.error(f"Failed to serialize embedding: {e}")
            os.remove(filepath)
            raise HTTPException(status_code=500, detail="Failed to serialize face data")
        
        try:
            case_id = db.execute_insert(
                query,
                (name, status, description, contact, filename, embedding_json, datetime.now())
            )
            logger.info(f"Insert result: case_id={case_id}")
        except Exception as e:
            logger.error(f"Database insert failed: {e}")
            os.remove(filepath)
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        if case_id is None:
            os.remove(filepath)
            raise HTTPException(status_code=500, detail="Failed to create case in database - no ID returned")
        
        logger.info(f"Case created: {case_id}, detected {face_count} face(s)")
        
        return {
            "success": True,
            "message": "Case uploaded successfully",
            "case_id": case_id,
            "faces_detected": face_count,
            "image_path": filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload case error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search-face")
async def search_face(image: UploadFile = File(...), min_similarity: float = Form(default=None)):
    """Search for similar faces in the database"""
    temp_filepath = None
    try:
        # Validate image file
        if not allowed_file(image.filename):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        # Read file content
        file_content = await image.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds maximum limit")
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Save temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        temp_filename = "temp_" + timestamp + image.filename
        temp_filepath = save_uploaded_file(file_content, temp_filename)
        
        if not temp_filepath:
            raise HTTPException(status_code=500, detail="Failed to save image")
        
        logger.info(f"Processing search image: {temp_filename}")
        
        try:
            # Validate face in image
            has_face, face_count = face_engine.validate_image(temp_filepath)
            if not has_face:
                logger.warning(f"No face detected in uploaded image: {temp_filename}")
                raise HTTPException(status_code=400, detail="No face detected in the image")
            
            logger.info(f"Face detected in image (count: {face_count})")
            
            # Get face embedding
            query_embedding = face_engine.get_face_embedding(temp_filepath)
            if query_embedding is None or len(query_embedding) == 0:
                logger.error(f"Failed to generate embedding for image: {temp_filename}")
                raise HTTPException(status_code=500, detail="Failed to process face")
            
            logger.info(f"Generated embedding of length {len(query_embedding)}")
            
            # Get all cases from database
            query = "SELECT id, name, status, description, contact, image_path, embedding, created_at FROM cases"
            cases = db.execute_query(query)
            
            logger.info(f"Retrieved {len(cases) if cases else 0} cases from database")
            
            if not cases or len(cases) == 0:
                logger.warning("No cases found in database")
                return {
                    "success": True,
                    "message": "No cases in database",
                    "match": None,
                    "search_time": datetime.now().isoformat()
                }
            
            # Prepare database embeddings
            database_embeddings = []
            for case in cases:
                try:
                    embedding = json.loads(case['embedding'])
                    database_embeddings.append({
                        'person_id': case['id'],
                        'case_id': case['id'],
                        'name': case['name'],
                        'status': case['status'],
                        'description': case['description'],
                        'contact': case['contact'],
                        'image_path': case['image_path'],
                        'embedding': embedding,
                        'created_at': case['created_at'].isoformat() if case['created_at'] else None
                    })
                except Exception as e:
                    logger.warning(f"Error processing case {case['id']}: {e}")
                    continue
            
            logger.info(f"Prepared {len(database_embeddings)} case embeddings")
            
            # Determine threshold to use (allow override via form field)
            if min_similarity is None:
                threshold_used = SIMILARITY_THRESHOLD
            else:
                # Accept either 0-1 fractional value or 0-100 percentage (e.g., 99)
                try:
                    threshold_used = float(min_similarity)
                except Exception:
                    threshold_used = SIMILARITY_THRESHOLD

                # If the caller passed a percentage (e.g., 99), normalize to 0-1
                if threshold_used > 1.0:
                    threshold_used = threshold_used / 100.0

            # Clamp to valid range
            threshold_used = max(0.0, min(1.0, threshold_used))
            logger.info(f"Starting face matching with threshold {threshold_used}")
            matches = face_engine.find_similar_faces(
                query_embedding,
                database_embeddings,
                threshold=threshold_used
            )
            logger.info(f"Face matching completed. Found {len(matches)} matches above threshold {threshold_used}")

            # Prepare matches output (include both score and percentage)
            matches_out = []
            for m in matches:
                score = float(m.get('similarity_score', 0.0))
                matches_out.append({
                    'case_id': m.get('case_id'),
                    'name': m.get('name'),
                    'status': m.get('status'),
                    'contact': m.get('contact'),
                    'description': m.get('description', ''),
                    'image_path': m.get('image_path'),
                    'similarity_score': round(score, 4),
                    'similarity_percentage': round(score * 100, 2)
                })

            if matches_out:
                # Best match is first after sorting in engine
                best_match = matches_out[0]
                logger.info(f"Returning best match: {best_match['name']} with {best_match['similarity_percentage']}% confidence")
                return {
                    "success": True,
                    "message": "Matching faces found",
                    "match": best_match,
                    "matches": matches_out,
                    "total_cases_searched": len(cases),
                    "threshold_used": threshold_used,
                    "search_time": datetime.now().isoformat()
                }
            else:
                logger.info("No matching face found above threshold")
                return {
                    "success": True,
                    "message": "No matching face found",
                    "match": None,
                    "matches": [],
                    "total_cases_searched": len(cases),
                    "threshold_used": threshold_used,
                    "search_time": datetime.now().isoformat()
                }
        
        finally:
            # Clean up temporary file
            if temp_filepath and os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                logger.info(f"Cleaned up temporary file: {temp_filepath}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search face error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cases")
async def get_all_cases(status: str = None, limit: int = 50):
    """Get all cases, optionally filtered by status"""
    try:
        if status:
            query = "SELECT id, name, status, description, contact, image_path, created_at FROM cases WHERE status = %s ORDER BY created_at DESC LIMIT %s"
            cases = db.execute_query(query, (status, limit))
        else:
            query = "SELECT id, name, status, description, contact, image_path, created_at FROM cases ORDER BY created_at DESC LIMIT %s"
            cases = db.execute_query(query, (limit,))
        
        if not cases:
            cases = []
        
        return {
            "success": True,
            "count": len(cases),
            "cases": [
                {
                    'case_id': case['id'],
                    'name': case['name'],
                    'status': case['status'],
                    'description': case['description'],
                    'contact': case['contact'],
                    'image_path': case['image_path'],
                    'created_at': case['created_at'].isoformat() if case['created_at'] else None
                }
                for case in cases
            ]
        }
    except Exception as e:
        logger.error(f"Get cases error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cases/{case_id}")
async def get_case_detail(case_id: int):
    """Get detailed information about a specific case"""
    try:
        query = "SELECT id, name, status, description, contact, image_path, created_at FROM cases WHERE id = %s"
        result = db.execute_query(query, (case_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = result[0]
        return {
            "success": True,
            "case": {
                'case_id': case['id'],
                'name': case['name'],
                'status': case['status'],
                'description': case['description'],
                'contact': case['contact'],
                'image_path': case['image_path'],
                'created_at': case['created_at'].isoformat() if case['created_at'] else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get case detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cases/{case_id}/delete")
async def delete_case(case_id: int, admin_password: str = Form(default='')):
    """Delete a case (requires admin password)"""
    try:
        from config import ADMIN_PASSWORD
        
        logger.info(f"Delete request for case {case_id}, password provided: {bool(admin_password)}")
        
        if not admin_password or admin_password != ADMIN_PASSWORD:
            logger.warning(f"Unauthorized delete attempt for case {case_id} - invalid password")
            raise HTTPException(status_code=401, detail="Unauthorized - invalid admin password")
        
        # Get image path first
        query = "SELECT image_path FROM cases WHERE id = %s"
        result = db.execute_query(query, (case_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Case not found")
        
        image_path = result[0]['image_path']
        logger.info(f"Deleting case {case_id} with image: {image_path}")
        
        # Delete from database
        delete_query = "DELETE FROM cases WHERE id = %s"
        db.execute_query(delete_query, (case_id,), commit=True)
        logger.info(f"Case {case_id} deleted from database")
        
        # Delete image file
        filepath = os.path.join(UPLOAD_FOLDER, image_path)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Could not delete image file: {e}")
        
        return {
            "success": True,
            "message": "Case deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete case error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """Get database statistics"""
    try:
        # Total cases
        total_query = "SELECT COUNT(*) as count FROM cases"
        total = db.execute_query(total_query)
        
        # Missing cases
        missing_query = "SELECT COUNT(*) as count FROM cases WHERE status = 'missing'"
        missing = db.execute_query(missing_query)
        
        # Found cases
        found_query = "SELECT COUNT(*) as count FROM cases WHERE status = 'found'"
        found = db.execute_query(found_query)
        
        return {
            "success": True,
            "statistics": {
                'total_cases': total[0]['count'] if total else 0,
                'missing_persons': missing[0]['count'] if missing else 0,
                'found_persons': found[0]['count'] if found else 0
            }
        }
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ BACKUP AND RESTORE ENDPOINTS ============

@app.post("/api/backup")
async def create_backup(admin_password: str = Form(default='')):
    """Create database backup (admin only)"""
    try:
        # Verify admin password
        if admin_password != ADMIN_PASSWORD:
            logger.warning("Unauthorized backup attempt - invalid password")
            raise HTTPException(status_code=401, detail="Invalid admin password")
        
        from backup import backup_database
        backup_file = backup_database()
        
        return {
            "success": True,
            "message": "Backup created successfully",
            "backup_file": backup_file
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/backups")
async def list_backups(admin_password: str = ""):
    """List all available backups (admin only)"""
    try:
        # Verify admin password
        if admin_password != ADMIN_PASSWORD:
            logger.warning("Unauthorized backup list request - invalid password")
            raise HTTPException(status_code=401, detail="Invalid admin password")
        
        from backup import list_backups
        backups = list_backups()
        
        return {
            "success": True,
            "backups": [
                {
                    "filename": b['filename'],
                    "size": b['size'],
                    "timestamp": b['filename'].replace('backup_', '').replace('.json', '')
                }
                for b in backups
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List backups error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/restore")
async def restore_from_backup(backup_filename: str = Form(...), admin_password: str = Form(default='')):
    """Restore database from backup (admin only)"""
    try:
        # Verify admin password
        if admin_password != ADMIN_PASSWORD:
            logger.warning("Unauthorized restore attempt - invalid password")
            raise HTTPException(status_code=401, detail="Invalid admin password")
        
        from backup import list_backups, restore_database
        
        # Find the backup file
        backups = list_backups()
        backup_path = None
        
        for backup in backups:
            if backup['filename'] == backup_filename:
                backup_path = backup['path']
                break
        
        if not backup_path:
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        restore_database(backup_path)
        
        return {
            "success": True,
            "message": f"Database restored from {backup_filename}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restore error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
