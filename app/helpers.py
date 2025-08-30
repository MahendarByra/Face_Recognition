import base64
import os
import cv2
import tempfile

def decode_base64_image(data_url: str) -> bytes:
    """
    Accepts 'data:image/png;base64,...' and returns raw bytes.
    """
    if not data_url:
        return None
    header, b64data = data_url.split(",", 1) if "," in data_url else ("", data_url)
    return base64.b64decode(b64data)

def read_file_storage(file_storage) -> bytes:
    """
    Read werkzeug FileStorage into bytes, without saving to disk.
    """
    return file_storage.read()

def extract_middle_frame_from_video_bytes(video_bytes: bytes) -> bytes:
    """
    Save video bytes to a temp file, grab a middle frame with OpenCV, return the frame as PNG bytes.
    """
    if not video_bytes:
        return None

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            return None
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        mid_index = max(frame_count // 2, 0)
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid_index)
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return None
        # Convert BGR -> RGB if your pipeline expects RGB; if it expects BGR, keep as is.
        # Here we'll encode as PNG directly from BGR.
        ok, buf = cv2.imencode(".png", frame)
        if not ok:
            return None
        return buf.tobytes()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass