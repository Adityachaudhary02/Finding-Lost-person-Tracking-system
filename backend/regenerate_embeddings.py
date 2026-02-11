import mysql.connector
from config import DB_CONFIG
import json
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognition_engine import face_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def regenerate_embeddings():
    """Regenerate embeddings for all cases"""
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Get all cases
        cursor.execute("SELECT id, image_path FROM cases")
        cases = cursor.fetchall()
        
        logger.info(f"Found {len(cases)} cases to regenerate embeddings for")
        
        for case in cases:
            try:
                case_id = case['id']
                image_path = case['image_path']
                
                # Full path to image
                full_path = os.path.join('uploads', image_path)
                
                if not os.path.exists(full_path):
                    logger.warning(f"Image not found for case {case_id}: {full_path}")
                    continue
                
                # Generate new embedding
                embedding = face_engine.get_face_embedding(full_path)
                embedding_json = json.dumps(embedding)
                
                # Update database
                update_query = "UPDATE cases SET embedding = %s WHERE id = %s"
                cursor.execute(update_query, (embedding_json, case_id))
                conn.commit()
                
                logger.info(f"Updated embedding for case {case_id}")
            except Exception as e:
                logger.error(f"Error processing case {case['id']}: {e}")
                continue
        
        logger.info("Embedding regeneration complete!")
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    regenerate_embeddings()
