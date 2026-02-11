import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Adi@808389'),
    'database': os.getenv('DB_NAME', 'findthem_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Face Recognition Configuration
SIMILARITY_THRESHOLD = 0.85 # Threshold for face matching (0-1), 60% for moderate-quality matches
MODEL_NAME = 'VGGFace2'  # Changed from facenet to VGGFace2 for better compatibility

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
RELOAD = os.getenv('RELOAD', True)

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change in production
