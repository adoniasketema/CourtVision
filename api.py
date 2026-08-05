import os
import uuid
import threading
import subprocess

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="CourtVision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("input_videos", exist_ok=True)
os.makedirs("output_videos", exist_ok=True)

# In-memory job store (reset on server restart)
_jobs: dict = {}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Accept a video upload, start the pipeline in a background thread, return a job_id."""
    filename = file.filename or ""
    if not filename.lower().endswith((".mp4", ".mov", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload an .mp4, .mov, or .avi file.")

    job_id = str(uuid.uuid4())
    safe_name = f"{job_id}_{filename}"
    input_path = os.path.join("input_videos", safe_name)
    output_filename = f"{job_id}_output.mp4"
    output_path = os.path.join("output_videos", output_filename)

    content = await file.read()
    with open(input_path, "wb") as f:
        f.write(content)

    _jobs[job_id] = {"status": "processing"}

    def _transcode_h264(src: str, dst: str) -> bool:
        """Re-encode src (mp4v) -> dst (H.264/yuv420p) for browser playback."""
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", src, "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-an", dst],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"[Warning] H.264 video transcoding skipped (ffmpeg missing or errored: {exc}). Serving raw video stream.")
            return False

    def _run():
        try:
            from main import run_pipeline
            stats = run_pipeline(input_path, output_path)
            tmp_path = output_path + ".h264.mp4"
            if _transcode_h264(output_path, tmp_path):
                os.replace(tmp_path, output_path)
            _jobs[job_id] = {
                "status": "done",
                "stats": stats,
                "output_filename": output_filename,
            }
        except Exception as exc:
            _jobs[job_id] = {"status": "error", "error": str(exc)}

    threading.Thread(target=_run, daemon=True).start()
    return {"job_id": job_id}


@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    """Poll this endpoint to get the status and results of a processing job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]


@app.get("/video/{filename}")
def serve_video(filename: str):
    """Serve a processed output video by filename."""
    safe_filename = os.path.basename(filename)
    path = os.path.join("output_videos", safe_filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4")
