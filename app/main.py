import os
import io
import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.face_detection_dep import face_detection_pipeline
from utils.face_registration_dep import face_registration_pipeline
from utils.face_recognition_dep import face_recognition_pipeline
from utils.face_anti_spoofing_dep import anti_spoofing_video_pipeline
from app.helpers import decode_base64_image, read_file_storage, extract_middle_frame_from_video_bytes
from app.generate_ID import generate_new_chef_id


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")  # needed for flash/session


TEMP_IMAGE_DIR = os.path.join("data\images", "temporary-images")


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/authorize", methods=["GET"])
def authorize_page():
    return render_template("authorize.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Expect 'chef_name' stored in session after recognition
    chef_name = session.get("chef_name", "Chef")
    return render_template("chef_dashboard.html", chef_name=chef_name)

# -------------------------
# API Endpoints
# -------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    chef_name = (first_name + "-" + last_name).strip()
    chef_id = generate_new_chef_id()

    image_file = request.files.get("image")
    image_data_url = request.form.get("image_data")

    if not first_name or not last_name:
        return redirect(url_for('register_page', message="First name and Last name are required."))

    img_bytes = None
    if image_file and image_file.filename:
        img_bytes = read_file_storage(image_file)
    elif image_data_url:
        img_bytes = decode_base64_image(image_data_url)

    if not img_bytes:
        return redirect(url_for('register_page', message="Please upload or capture an image."))

    # Save image to disk temporarily
    filename = f"{chef_id}_{chef_name}.jpg"
    image_path = os.path.join(TEMP_IMAGE_DIR, filename)
    try:
        with open(image_path, "wb") as f:
            f.write(img_bytes)
        
        # Call deployment-ready pipeline
        result = face_registration_pipeline(image_path=image_path)
        if result == 1:
            # Copy image to known_faces and delete temporary image
            known_faces_dir = os.path.join("data", "images", "known_faces")
            os.makedirs(known_faces_dir, exist_ok=True)
            known_face_path = os.path.join(known_faces_dir, filename)
            os.rename(image_path, known_face_path)
            # Success → redirect to dashboard
            session["chef_name"] = chef_name
            return redirect(url_for('dashboard'))
        elif result == -3:
            os.remove(image_path)
            return redirect(url_for('register_page', message="Registration failed (DB or unknown error)"))
        elif result == -1:
            os.remove(image_path)
            return redirect(url_for('register_page', message="No face found in image"))
        elif result == -2:
            os.remove(image_path)
            return redirect(url_for('register_page', message="Encodings extraction failed"))
        elif result == -4:
            os.remove(image_path)
            return redirect(url_for('register_page', message="Chef already exists.. Please authorize"))
        elif result == -5:
            os.remove(image_path)
            return redirect(url_for('register_page', message="Failed to Add the chef. Internal Database error"))

    except Exception as e:
        return redirect(url_for('register_page', message=f"Registration failed: {e}"))

@app.route("/api/authorize", methods=["POST"])
def api_authorize():
    video_file = request.files.get("video")
    if not video_file or not video_file.filename:
        return jsonify({"ok": False, "message": "No video uploaded."}), 400

    video_bytes = read_file_storage(video_file)

    # 1) Anti-spoofing
    try:
        status, best_frame_path, metrics, debug = anti_spoofing_video_pipeline(io.BytesIO(video_bytes))

        if status is False:  # spoof
            return jsonify({"ok": False, "message": "Spoof detected.", "debug": debug}), 403
        if status == -1:  # not enough frames or error
            return jsonify({"ok": False, "message": "Not enough frames for liveness.", "debug": debug}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": f"Anti-spoofing failed: {e}"}), 500

    # 3) Face recognition
    try:
        recog = face_recognition_pipeline(best_frame_path)
        if recog == -1:
            return jsonify({"ok": False, "message": "Failed to connect to database."}), 500
        elif recog == -2:
            return jsonify({"ok": False, "message": "Failed to load encodings."}), 500
        elif recog == -3:
            return jsonify({"ok": False, "message": "No face found in test image."}), 400
        elif recog == -4:
            return jsonify({"ok": False, "message": "No face matched."}), 401
        else:
            # Expected tuple: (chef_id, name)
            chef_id, chef_name = recog
            session["chef_name"] = chef_name
            return jsonify({
                "ok": True,
                "message": f"Welcome {chef_name}!",
                "chef_id": chef_id,
                "chef_name": chef_name,
                "redirect": url_for('dashboard')
            })

    except Exception as e:
        return jsonify({"ok": False, "message": f"Recognition failed: {e}"}), 500
    finally:
        os.remove(best_frame_path)


if __name__ == "__main__":
    # Run as a module from project root:
    #   python -m app.main
    # Or directly:
    #   python app/main.py
    app.run(debug=True, host="0.0.0.0", port=5000)