# Face Authentication & Anti-Spoofing System

## Overview

This project implements a **real-time face authentication system** with **liveness detection** to prevent spoofing. It is designed for chefs to **register and authorize** themselves using a 10-second video captured from a browser camera. The system ensures only real, authorized faces are recognized and added to the database.

The project is structured in a modular way using **Flask**, **OpenCV**, **dlib**, and a **SQLite database**, with separate pipelines for **face registration, anti-spoofing, and recognition**.

---

## Features

1. **Face Registration**

   * Upload or capture an image via the browser.
   * Extract face encodings and store chef information in the database.
   * Prevents duplicate entries.

2. **Liveness Detection / Anti-Spoofing**

   * Capture a 10-second video from the browser.
   * Analyze frames for:

     * **Eye blinks** (EAR metric)
     * **Head motion** (nose displacement)
     * **Optical flow** (average motion magnitude)
   * Decide liveness and reject spoofed videos.
   * Save the **best frame** for recognition if video is real.

3. **Face Recognition**

   * Recognize registered chefs from the extracted frame.
   * Match against the SQLite database.
   * Return results in JSON:

     * Success: `{"ok": True, "message": "Welcome <chef_name>!", "redirect": <dashboard_url>}`
     * Failure / No match: `{"ok": False, "message": <error_message>}`

4. **Browser Interface**

   * Simple **camera capture interface** using HTML and JavaScript.
   * Record 10-second video for authorization.
   * Start and stop camera, record video, display authorization status.

---

## Project Structure

```
face_auth_crav/
│
├─ app/                        # Flask application
│  ├─ static/                  # JS, CSS
│  ├─ templates/               # HTML templates
│  ├─ main.py                  # Flask routes & API
│  ├─ helpers.py               # Utility functions for app
│  └─ generate_ID.py           # ID generation for chefs
│
├─ data/                       # Storage
│  ├─ images/
│  │  ├─ known_faces/          # Registered chef images
│  │  ├─ temporary-images/     # Temporary uploads
│  │  └─ temporary-outputs/    # Best frames from videos
│  └─ chefs.db                 # SQLite database
│
├─ utils/                      # Pipelines
│  ├─ face_detection_dep.py    # Face detection pipeline
│  ├─ face_registration_dep.py # Registration pipeline
│  ├─ face_recognition_dep.py  # Recognition pipeline
│  ├─ face_anti_spoofing_dep.py# Anti-spoofing pipeline
│  └─ db_handler.py            # Database handler
│
├─ dev/                        # Development notebooks
├─ docker/                     # Docker (optional)
├─ requirements.txt
└─ shape_predictor_68_face_landmarks.dat  # Dlib landmark model
```

---

## Data Flow

### 1. **Registration**

1. User uploads or captures an image.
2. `face_registration_pipeline` checks for face, extracts encodings, and adds to database.
3. On success, image is moved to `known_faces`.

### 2. **Authorization**

1. Browser captures a 10-second video.
2. Video sent via POST to `/api/authorize`.
3. `anti_spoofing_video_pipeline`:

   * Extracts frames.
   * Computes metrics (blinks, optical flow, head motion).
   * Determines liveness.
   * Saves **best frame** if real.
4. `face_recognition_pipeline`:

   * Takes the best frame path.
   * Matches against registered faces.
   * Returns matched chef info or failure.

---

## Anti-Spoofing Metrics

* **Eye Aspect Ratio (EAR):** Detects blinks.
* **Optical Flow:** Measures motion in frames.
* **Head Motion:** Normalized nose displacement.
* **Face Frame Count:** Minimum frames containing a face.

The final decision combines these metrics with a weighted score.

---

## JSON Responses

### Registration Pipeline (`face_registration_pipeline`)

| Result | Meaning             | Action                                              |
| ------ | ------------------- | --------------------------------------------------- |
| 1      | Success             | Image saved to `known_faces`, redirect to dashboard |
| -1     | No face found       | Redirect to registration page with error            |
| -2     | Encoding failed     | Redirect to registration page with error            |
| -3     | Unknown error       | Redirect to registration page                       |
| -4     | Chef already exists | Redirect to registration page                       |
| -5     | DB error            | Redirect to registration page                       |

### Authorization Pipeline (`/api/authorize`)

| Key      | Value      | Meaning                            |
| -------- | ---------- | ---------------------------------- |
| ok       | True/False | Overall status                     |
| message  | String     | Status or error message            |
| redirect | URL        | Dashboard redirect (if successful) |

---

## Dependencies

* Python 3.10
* Flask
* OpenCV
* dlib (19.24.1)
* NumPy
* SQLite3

Install dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** Do **not** use Windows-specific dlib wheels in Linux Docker.

---

## How to Run

1. Activate your venv:

```bash
cd face_auth_crav
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start Flask server:

```bash
cd app
flask run
```

4. Open browser: `http://localhost:5000/register` to register a chef.
   `http://localhost:5000/authorize` to authorize via 10-second video.

---

## Notes

* The project is fully modular: you can swap or improve **anti-spoofing or recognition** pipelines independently.
* The system uses **session storage** to keep track of the authenticated chef.
* Best frames from videos are saved in `data/images/temporary-outputs/` and can be cleaned periodically.

---

## Future Work

* Dockerization for Linux containers.
* Web interface improvements with **Streamlit**.
* Multi-face authorization support.
* Logging and analytics for spoof attempts.
