import ast
import os
import sqlite3
import face_recognition
import numpy as np
from datetime import datetime
from utils.face_detection_dep import  face_detection_pipeline

def extract_info_from_filename(filename):
    base = os.path.splitext(filename)[0]
    if '_' in base:
        chef_id, name = base.split('_', 1)
    else:
        chef_id, name = "Unknown", base
    return chef_id, name.replace('_', ' ')

def check_matching(cursor, name, test_encoding):
    
    # Check if chef name already exists to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM registered_chefs WHERE name = ?", (name,))
    if cursor.fetchone()[0] > 0:
        return -4  # Code for duplicate entry

    # check with encodings
    # Fetch id, name, image_path, and encoding
    cursor.execute("SELECT id, name, image_path, encoding FROM registered_chefs")
    rows = cursor.fetchall()
    known_encodings = []
    known_names = []

    for row in rows:
        chef_id, name, image_path, encoding_str = row[0], row[1], row[2], row[3]
            
        try:
            # Convert stringified list to actual list and then to numpy array
            encoding_list = ast.literal_eval(encoding_str)
            encoding_np = np.array(encoding_list)
                
            known_encodings.append(encoding_np)
            known_names.append(name)
        except Exception as e:
            print(f"Failed to load encoding for {name}: {e}")

    known_encodings = np.array(known_encodings)
    results = face_recognition.compare_faces(known_encodings, test_encoding, tolerance=0.4)
    distances = face_recognition.face_distance(known_encodings, test_encoding)

    print("Results:", results)
    print("Distances:", distances)

    if True in results:
        best_match_index = np.argmin(distances)
        name = known_names[best_match_index]
        return -4 # duplicate entry
    else:
        return 1  # No duplicate found




def face_registration_pipeline(image_path):
    # Connect to the database
    db_path = 'data/chefs.db'  # Changed from ../data for consistency
    if not os.path.exists(db_path):
        return -3

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        print(f"[DB Error] {e}")
        return -3

    # Perform face detection and encoding
    encoding = face_detection_pipeline(image_path)
    if isinstance(encoding, int):  # -1: No face, -2: Encoding failure
        return encoding

    # Extract metadata from filename
    try:
        chef_id, name = extract_info_from_filename(os.path.basename(image_path))
        match = check_matching(cursor,name, encoding)

        if match == -4:
            return -4
        
        # Insert into DB
        cursor.execute("""
            INSERT INTO registered_chefs (chef_ID, name, image_path, encoding, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            chef_id,
            name,
            image_path,
            str(list(encoding)),  # storing encoding as stringified list
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        return 1  # Success
    except Exception as e:
        print(f"[Insert Error] {e}")
        return -5
    finally:
        conn.close()

if __name__ == "__main__":
    image_path = "data/images/temp/C0013_Mahendar-Byra.jpg"
    result = face_registration_pipeline(image_path)

    if result == 1:
        print("✅ Registration successful")
    elif result == -3:
        print("❌ Registration failed (DB or unknown error)")
    elif result == -1:
        print("❌ No face found in image")
    elif result == -2:
        print("encodings extraction failed")
    elif result == -4:
        print("⚠️ Chef ID already exists")
    elif result == -5:
        print("Failed to Add the chef. Internal Database error")
