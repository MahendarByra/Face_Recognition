import face_recognition

def face_detection_pipeline(image_path):
    """
    Main pipeline for face detection and registration.
    
    Args:
        image_path (str): Path to the image file.
    
    Returns:
        np.ndarray or int: 128-d face encoding vector or status code.
    """
    if not detects_faces(image_path):
        return -1  # No face detected

    encoding = get_face_encoding(image_path)
    if encoding is None:
        return -2  # Encoding extraction failed

    return encoding  # ✅ Return the full 128-d encoding


def detects_faces(image_path):
    """
    Detects if at least one face exists in the image.
    
    Args:
        image_path (str): Path to the image file.
    
    Returns:
        bool: True if face(s) found, False otherwise.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        return len(face_locations) > 0
    except Exception as e:
        print(f"[Face Detection Error] {e}")
        return False


def get_face_encoding(image_path):
    """
    Returns the first face encoding from the image if available.
    
    Args:
        image_path (str): Path to the image file.
    
    Returns:
        numpy.ndarray or None: 128-d face encoding vector or None if not found.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            return None
        return encodings[0]  
    except Exception as e:
        print(f"[Encoding Error] {e}")
        return None


# Optional CLI Test
if __name__ == "__main__":
    test_image_path = "data/images/known_faces/C0012_Rohit-Sharma.jpg"

    result = face_detection_pipeline(test_image_path)
    if isinstance(result, int):
        if result == -1:
            print("❌ No face detected in the image.")
        elif result == -2:
            print("❌ Face encoding extraction failed.")
    else:
        print(f"✅ Face detected and encoded successfully.\nEncoding shape: {result.shape}")
        #print(f"Encoding: {result}")
