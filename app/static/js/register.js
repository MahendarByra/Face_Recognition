const form = document.getElementById("register-form");
const fileInput = document.getElementById("image");
const uploadPreview = document.getElementById("upload-preview");

const video = document.getElementById("camera");
const startCamBtn = document.getElementById("startCam");
const captureBtn = document.getElementById("capture");
const canvas = document.getElementById("canvas");
const capturePreview = document.getElementById("capture-preview");
const hiddenImageData = document.getElementById("image_data");
const statusBox = document.getElementById("status");

let stream;

function setStatus(msg) {
  statusBox.textContent = msg || "";
}

fileInput?.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (!file) {
    uploadPreview.style.display = "none";
    return;
  }
  const url = URL.createObjectURL(file);
  uploadPreview.src = url;
  uploadPreview.style.display = "block";

  // If user selected a file, clear webcam capture
  hiddenImageData.value = "";
  capturePreview.style.display = "none";
});

startCamBtn?.addEventListener("click", async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
  } catch (err) {
    setStatus("Could not start camera: " + err);
  }
});

captureBtn?.addEventListener("click", () => {
  if (!stream) {
    setStatus("Start the camera first.");
    return;
  }
  const v = video;
  const w = v.videoWidth || 640;
  const h = v.videoHeight || 480;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(v, 0, 0, w, h);
  const dataUrl = canvas.toDataURL("image/png");
  hiddenImageData.value = dataUrl;

  capturePreview.src = dataUrl;
  capturePreview.style.display = "block";

  // If webcam captured, clear file selection
  fileInput.value = "";
  uploadPreview.style.display = "none";
});

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  setStatus("Submitting...");

  const fd = new FormData(form);
  try {
    const res = await fetch("/api/register", {
      method: "POST",
      body: fd
    });
    const data = await res.json();
    if (data.ok) {
      setStatus("✅ " + (data.message || "Registered."));
      // Optional: redirect directly to authorize to continue
      // window.location.href = "/authorize";
    } else {
      setStatus("❌ " + (data.message || "Failed."));
    }
  } catch (err) {
    setStatus("❌ Request failed: " + err);
  }
});
