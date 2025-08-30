import sqlite3
import os
import json
from datetime import datetime

# Path to the database file
DB_PATH = "data/chefs.db"

def init_db():
    # Make sure the data folder exists
    os.makedirs("data", exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registered_chefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chef_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            image_path TEXT NOT NULL,
            encoding TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()
    print("✅ Database and table initialized!")


def insert_chef(chef_id, name, image_path, encoding):
    """
    Inserts a new chef record into the database.
    encoding: should be a NumPy array or list (128-d), will be stored as JSON.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        encoding_json = json.dumps(encoding)  # Convert list to JSON string
        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO registered_chefs (chef_id, name, image_path, encoding, timestamp)
            VALUES (?, ?, ?, ?, ?);
        """, (chef_id, name, image_path, encoding_json, timestamp))

        conn.commit()
        conn.close()
        print(f"✅ Chef '{name}' inserted successfully!")
        return True
    except sqlite3.IntegrityError:
        print("❌ Error: Duplicate chef_id.")
        return False

def print_chefs():
    """
    Inserts a new chef record into the database.
    encoding: should be a NumPy array or list (128-d), will be stored as JSON.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, image_path, encoding FROM registered_chefs")
        rows = cursor.fetchall()

        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Image Path: {row[2]}")
    
    except sqlite3.IntegrityError:
        print("❌ Error: Duplicate chef_id.")


if __name__ == "__main__":
    print_chefs()