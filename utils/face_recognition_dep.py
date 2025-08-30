import sqlite3
import face_recognition
import numpy as np
import ast

def face_recognition_pipeline(test_image_path):
    # connect to the database
    db_path = 'data/chefs.db'  # Update if your DB is elsewhere
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception:
        return -1  # ❌ Failed to connect to DB

    try:
        # Fetch id, name, image_path, and encoding
        cursor.execute("SELECT id, name, image_path, encoding FROM registered_chefs")
        rows = cursor.fetchall()

        known_encodings = []
        known_names = []
        known_ids = []

        for row in rows:
            chef_id, name, image_path, encoding_str = row[0], row[1], row[2], row[3]

            try:
                # Convert stringified list to actual list and then to numpy array
                encoding_list = ast.literal_eval(encoding_str)
                encoding_np = np.array(encoding_list)
                
                known_encodings.append(encoding_np)
                known_names.append(name)
                known_ids.append(chef_id)
            except Exception:
                return -2  # ❌ Failed to load stored encodings

        known_encodings = np.array(known_encodings)

        # Load and encode test image
        test_image = face_recognition.load_image_file(test_image_path)
        test_encodings = face_recognition.face_encodings(test_image)

        if not test_encodings:
            return -3  # ❌ No face found in test image

        test_encoding = test_encodings[0]

        results = face_recognition.compare_faces(known_encodings, test_encoding, tolerance=0.4)
        distances = face_recognition.face_distance(known_encodings, test_encoding)

        if True in results:
            best_match_index = np.argmin(distances)
            chef_id = known_ids[best_match_index]
            name = known_names[best_match_index]
            return chef_id, name  # ✅ Match found
        else:
            return -4  # ❌ No match found

    except Exception:
        return -2  # ❌ Failed during encoding/comparison

    finally:
        conn.close()


if __name__ == "__main__":
    test_image_path = "data/images/test/test.jpg"
    result = face_recognition_pipeline(test_image_path)

    if result == -1:
        print("❌ Failed to connect to database.")
    elif result == -2:
        print("❌ Failed to load encodings.")
    elif result == -3:
        print("❌ No face found in test image.")
    elif result == -4:
        print("❌ No match found.")
    else:
        chef_id, name = result
        print(f"✅ Match found: Chef ID {chef_id}, Name {name}")
