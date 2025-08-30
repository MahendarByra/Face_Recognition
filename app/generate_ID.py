import os
import sqlite3
import re
from glob import glob

DB_PATH = "data/chefs.db"
TEMP_DIR = "data/images/temporary-images"

def generate_new_chef_id():
    """Generate a new Chef ID based on the max ID in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists (optional safeguard)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chefs (
            chef_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            image_path TEXT
        )
    """)

    cursor.execute("SELECT chef_id FROM registered_chefs")
    chef_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not chef_ids:
        return "C001"

    # Extract numbers and find max
    max_num = max([int(re.search(r"C(\d+)", cid).group(1)) for cid in chef_ids])
    new_id_num = max_num + 1
    return f"C{new_id_num:04d}"


def rename_temp_image():
    """Rename temp image to CHEFID_FirstName-LastName.jpg and return path."""
    temp_images = glob(os.path.join(TEMP_DIR, "*.jpg"))

    if not temp_images:
        raise FileNotFoundError("❌ No image found in temp folder.")

    # Get the first (and should be only) image
    temp_image_path = temp_images[0]
    filename = os.path.basename(temp_image_path)
    name_part = os.path.splitext(filename)[0]  # Mahendar_Byra

    # Extract FirstName and LastName
    try:
        first_name, last_name = name_part.split("_")
    except ValueError:
        raise ValueError("❌ Image name must be in FirstName_LastName format.")

    # Generate new chef ID
    new_chef_id = generate_new_chef_id()

    # Create new file name
    new_filename = f"{new_chef_id}_{first_name}-{last_name}.jpg"
    new_path = os.path.join(TEMP_DIR, new_filename)

    # Rename the file
    os.rename(temp_image_path, new_path)

    return new_path, new_chef_id, first_name, last_name


if __name__ == "__main__":
    try:
        #image_path, chef_id, first_name, last_name = rename_temp_image()
        chef_id = generate_new_chef_id()
        print(f"✅ New Chef ID: {chef_id}")

        # Now you can call your pipelines
        # if face_detection_pipeline(image_path):
        #     face_registration_pipeline(chef_id, first_name, last_name, image_path)
        # else:
        #     print("❌ No face detected.")

    except Exception as e:
        print(str(e))
