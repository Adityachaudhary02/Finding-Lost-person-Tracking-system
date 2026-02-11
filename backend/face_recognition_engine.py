import cv2
import numpy as np
from pathlib import Path
import logging
import os
from config import SIMILARITY_THRESHOLD, MODEL_NAME
from scipy import ndimage
from scipy.spatial import distance
import imghdr

logger = logging.getLogger(__name__)

class FaceRecognitionEngine:
    def __init__(self):
        self.model_name = MODEL_NAME
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, image_path):
        """Detect faces in an image using Haar Cascade"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return []
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            detected_faces = [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} 
                            for x, y, w, h in faces]
            
            logger.info(f"Detected {len(detected_faces)} face(s) in {image_path}")
            return detected_faces
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    def get_face_embedding(self, image_path):
        """Generate robust face embedding using multi-scale HOG-like features and color histograms"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return [0.0] * 256
            
            # Get faces in image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            
            if len(faces) == 0:
                logger.warning(f"No faces detected in {image_path}, using full image features")
                face_region = gray
                color_region = img
            else:
                # Use the largest detected face
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                # Add padding to capture more context
                pad = int(w * 0.1)
                x, y, w, h = max(0, x-pad), max(0, y-pad), w+2*pad, h+2*pad
                face_region = gray[y:min(y+h, gray.shape[0]), x:min(x+w, gray.shape[1])]
                color_region = img[y:min(y+h, img.shape[0]), x:min(x+w, img.shape[1])]
            
            embedding = []
            
            # 1. Multi-scale Histogram of Oriented Gradients (HOG-like) - 96 dims
            embedding.extend(self._get_hog_features(face_region, bins=8))
            
            # 2. Grayscale histogram features - 32 dims
            gray_hist = cv2.calcHist([face_region], [0], None, [32], [0, 256])
            gray_hist = cv2.normalize(gray_hist, gray_hist).flatten()
            embedding.extend(gray_hist.tolist())
            
            # 3. Color histogram features (BGR) - 96 dims
            for i in range(3):
                color_hist = cv2.calcHist([color_region], [i], None, [32], [0, 256])
                color_hist = cv2.normalize(color_hist, color_hist).flatten()
                embedding.extend(color_hist.tolist())
            
            # 4. Texture features using Laplacian variance - 8 dims
            laplacian = cv2.Laplacian(face_region, cv2.CV_64F)
            embedding.append(float(np.var(laplacian)))
            embedding.append(float(np.mean(laplacian)))
            embedding.append(float(np.std(laplacian)))
            embedding.append(float(np.max(laplacian)))
            embedding.append(float(np.min(laplacian)))
            
            # Sobel edge features
            sobelx = cv2.Sobel(face_region, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(face_region, cv2.CV_64F, 0, 1, ksize=5)
            embedding.append(float(np.var(sobelx)))
            embedding.append(float(np.var(sobely)))
            embedding.append(float(np.mean(np.sqrt(sobelx**2 + sobely**2))))
            
            # 5. Contour/shape features - 16 dims
            edges = cv2.Canny(face_region, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            contour_features = [
                len(contours),  # Number of contours
                float(np.mean([cv2.contourArea(c) for c in contours])) if contours else 0,
                float(np.sum([cv2.contourArea(c) for c in contours])),
                float(np.mean([cv2.arcLength(c, True) for c in contours])) if contours else 0,
            ]
            embedding.extend(contour_features)
            
            # Add resized pixel values for spatial information - 8 dims
            resized = cv2.resize(face_region, (8, 8))
            embedding.extend((resized.flatten() / 255.0).tolist())
            
            # Ensure exactly 256 dimensions
            embedding = np.array(embedding, dtype=np.float32).tolist()
            embedding = embedding[:256]
            while len(embedding) < 256:
                embedding.append(0.0)
            
            # Normalize embedding
            emb_array = np.array(embedding, dtype=np.float32)
            norm = np.linalg.norm(emb_array)
            if norm > 1e-6:
                embedding = (emb_array / norm).tolist()
            
            logger.info(f"Created robust embedding of length {len(embedding)} for {image_path}")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return [0.0] * 256
    
    def _get_hog_features(self, image, bins=8):
        """Extract HOG-like features from image"""
        try:
            if image is None or image.size == 0:
                return [0.0] * 96
            
            # Ensure minimum size
            if image.shape[0] < 16 or image.shape[1] < 16:
                image = cv2.resize(image, (32, 32))
            
            # Compute gradients
            sobelx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
            sobely = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
            
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            angle = np.arctan2(sobely, sobelx) * 180 / np.pi
            angle[angle < 0] += 180
            
            # Create multiple scale levels
            features = []
            
            # Original scale
            hist, _ = np.histogram(angle.flatten(), bins=bins, range=(0, 180), weights=magnitude.flatten())
            hist = hist / (np.sum(hist) + 1e-6)
            features.extend(hist.tolist())
            
            # Downsampled scales
            for scale in [2, 4]:
                h, w = image.shape
                new_h, new_w = h // scale, w // scale
                
                if new_h > 0 and new_w > 0:
                    small_mag = cv2.resize(magnitude, (new_w, new_h))
                    small_angle = cv2.resize(angle, (new_w, new_h))
                    
                    hist, _ = np.histogram(small_angle.flatten(), bins=bins, range=(0, 180), 
                                         weights=small_mag.flatten())
                    hist = hist / (np.sum(hist) + 1e-6)
                    features.extend(hist.tolist())
            
            # Pad to 96 dimensions
            features = features[:96]
            while len(features) < 96:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"HOG extraction error: {e}")
            return [0.0] * 96
    
    def compare_faces(self, embedding1, embedding2):
        """Compare two face embeddings using cosine similarity and euclidean distance"""
        try:
            # Validate embeddings
            embedding1 = np.array(embedding1, dtype=np.float32)
            embedding2 = np.array(embedding2, dtype=np.float32)
            
            # Check for empty or mismatched embeddings
            if embedding1.size == 0 or embedding2.size == 0:
                logger.warning(f"Empty embedding - embedding1 size: {embedding1.size}, embedding2 size: {embedding2.size}")
                return 0.0
            
            # Ensure same length
            if embedding1.shape != embedding2.shape:
                logger.debug(f"Mismatched embedding shapes: {embedding1.shape} vs {embedding2.shape}")
                min_len = min(len(embedding1), len(embedding2))
                embedding1 = embedding1[:min_len]
                embedding2 = embedding2[:min_len]
            
            # Normalize vectors to unit length
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 < 1e-6 or norm2 < 1e-6:
                logger.debug("Near-zero norm detected, returning 0 similarity")
                return 0.0
            
            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2
            
            # Use both cosine similarity and euclidean distance for robustness
            # 1. Cosine similarity (range: -1 to 1, higher is better)
            cosine_sim = float(np.dot(embedding1_norm, embedding2_norm))
            # Map to 0-1 range: (cosine_sim + 1) / 2
            cosine_score = max(0.0, (cosine_sim + 1.0) / 2.0)
            
            # 2. Euclidean distance (range: 0 to sqrt(2) for normalized vectors)
            euclidean_dist = float(np.linalg.norm(embedding1_norm - embedding2_norm))
            # Convert to similarity score: 1 - (dist / max_possible_dist)
            # Max distance for normalized vectors is sqrt(2)
            euclidean_score = max(0.0, 1.0 - (euclidean_dist / np.sqrt(2)))
            
            # 3. Combine both metrics for more robust matching
            # Weight cosine slightly higher as it's more standard for embeddings
            combined_score = 0.6 * cosine_score + 0.4 * euclidean_score
            combined_score = max(0.0, min(1.0, combined_score))
            
            logger.debug(f"Cosine: {cosine_score:.4f}, Euclidean: {euclidean_score:.4f}, Combined: {combined_score:.4f}")
            
            return combined_score
            
        except Exception as e:
            logger.error(f"Face comparison error: {e}")
            return 0.0
    
    def find_similar_faces(self, query_embedding, database_embeddings, threshold=None):
        """Find similar faces from database embeddings"""
        if threshold is None:
            # Use a reasonable threshold for the improved matching algorithm
            # 0.65 = high confidence matches (real faces are typically 0.75+)
            threshold = max(0.85, self.similarity_threshold - 0.25)
        
        matches = []
        
        logger.info(f"Searching {len(database_embeddings)} cases with threshold {threshold}")
        
        for db_face in database_embeddings:
            # Skip if embedding is empty or invalid
            embedding = db_face.get('embedding')
            if not embedding or len(embedding) == 0:
                logger.debug(f"Skipping case {db_face.get('case_id')} - empty embedding")
                continue
            
            try:
                similarity = self.compare_faces(query_embedding, embedding)
                logger.debug(f"Case {db_face.get('case_id')} ({db_face.get('name')}) similarity: {similarity:.4f}")
                
                if similarity >= threshold:
                    matches.append({
                        'person_id': db_face.get('person_id'),
                        'case_id': db_face.get('case_id'),
                        'name': db_face.get('name'),
                        'status': db_face.get('status'),
                        'description': db_face.get('description'),
                        'contact': db_face.get('contact'),
                        'image_path': db_face.get('image_path'),
                        'similarity_score': similarity
                    })
            except Exception as e:
                logger.error(f"Error comparing faces for case {db_face.get('case_id')}: {e}")
                continue
        
        logger.info(f"Found {len(matches)} potential matches above threshold {threshold}")
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches
    
    def validate_image(self, image_path):
        """Validate if image is a valid image file"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, 0
            
            # Try to detect faces
            try:
                faces = self.detect_faces(image_path)
                face_count = len(faces) if faces else 0
                return True, max(1, face_count)
            except Exception as e:
                logger.warning(f"Face detection failed in validation: {e}")
                return True, 1
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False, 0

# Global face recognition engine
face_engine = FaceRecognitionEngine()

