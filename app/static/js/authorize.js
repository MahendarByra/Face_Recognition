const startBtn = document.getElementById("startAuthCam");
const recordBtn = document.getElementById("record10");
const video = document.getElementById("auth-camera");
const statusBox = document.getElementById("auth-status");

let stream;
let recorder;
let chunks = [];

function setStatus(msg) {
  statusBox.textContent = msg || "";
}

startBtn?.addEventListener("click", async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = stream;
    setStatus("Camera ready.");
  } catch (err) {
    setStatus("Could not start camera: " + err);
  }
});

recordBtn?.addEventListener("click", async () => {
  if (!stream) {
    setStatus("Start the camera first.");
    return;
  }
  chunks = [];
  const options = { mimeType: "video/webm; codecs=vp9" };
  try {
    recorder = new MediaRecorder(stream, options);
  } catch (err) {
    // Fallback without options
    recorder = new MediaRecorder(stream);
  }

  recorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) {
      chunks.push(e.data);
    }
  };

  recorder.onstop = async () => {
    const blob = new Blob(chunks, { type: "video/webm" });
    const fd = new FormData();
    fd.append("video", blob, "authorize.webm");

    setStatus("Uploading & authorizing...");
    try {
      const res = await fetch("/api/authorize", {
        method: "POST",
        body: fd
      });
      const data = await res.json();
      if (data.ok) {
        setStatus("✅ " + (data.message || "Authorized."));
        const redirect = data.redirect || "/dashboard";
        window.location.href = redirect;
      } else {
        setStatus("❌ " + (data.message || "Authorization failed."));
      }
    } catch (err) {
      setStatus("❌ Request failed: " + err);
    }
  };

  setStatus("Recording 10 seconds...");
  recorder.start();

  setTimeout(() => {
    recorder.stop();
    setStatus("Processing...");
  }, 10_000);
});
