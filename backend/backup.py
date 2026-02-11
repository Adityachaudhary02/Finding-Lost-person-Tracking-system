"""
Database backup and restore functionality
Ensures data persistence even if MySQL has issues
"""
import mysql.connector
from config import DB_CONFIG
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKUP_DIR = 'database_backups'

def ensure_backup_dir():
    """Create backup directory if it doesn't exist"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    """Backup database to JSON file"""
    try:
        ensure_backup_dir()
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Get all cases
        cursor.execute("SELECT * FROM findthem_db.cases")
        cases = cursor.fetchall()
        
        # Convert datetime objects to strings
        for case in cases:
            for key, value in case.items():
                if isinstance(value, datetime):
                    case[key] = value.isoformat()
        
        # Create backup file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
        
        with open(backup_file, 'w') as f:
            json.dump({'cases': cases, 'timestamp': timestamp}, f, indent=2)
        
        logger.info(f"Database backup created: {backup_file} ({len(cases)} cases)")
        
        cursor.close()
        conn.close()
        
        return backup_file
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        raise

def restore_database(backup_file):
    """Restore database from JSON backup"""
    try:
        if not os.path.exists(backup_file):
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        with open(backup_file, 'r') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM findthem_db.cases")
        
        # Restore cases
        for case in cases:
            query = """INSERT INTO findthem_db.cases 
                       (id, name, status, description, contact, image_path, embedding, 
                        is_resolved, resolved_at, notes, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                case.get('id'),
                case.get('name'),
                case.get('status'),
                case.get('description'),
                case.get('contact'),
                case.get('image_path'),
                case.get('embedding'),
                case.get('is_resolved'),
                case.get('resolved_at'),
                case.get('notes'),
                case.get('created_at'),
                case.get('updated_at')
            )
            
            cursor.execute(query, values)
        
        conn.commit()
        logger.info(f"Database restored from {backup_file} ({len(cases)} cases)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Restore error: {e}")
        raise

def list_backups():
    """List all available backups"""
    ensure_backup_dir()
    
    backups = []
    for file in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if file.endswith('.json'):
            filepath = os.path.join(BACKUP_DIR, file)
            size = os.path.getsize(filepath)
            backups.append({'filename': file, 'path': filepath, 'size': size})
    
    return backups

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python backup.py [backup|restore|list]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        backup_database()
    elif command == "restore":
        if len(sys.argv) < 3:
            backups = list_backups()
            if backups:
                print(f"Restoring from latest backup: {backups[0]['filename']}")
                restore_database(backups[0]['path'])
            else:
                print("No backups found!")
        else:
            restore_database(sys.argv[2])
    elif command == "list":
        backups = list_backups()
        print(f"Found {len(backups)} backups:")
        for backup in backups:
            print(f"  - {backup['filename']} ({backup['size']} bytes)")
