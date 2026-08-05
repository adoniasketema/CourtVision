import cv2
import json
import os

def read_video(video_path):
    cap=cv2.VideoCapture(video_path)
    frames=[]
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def _stub_meta_path(stub_path):
    return stub_path + ".meta.json"


def _video_fingerprint(video_path):
    stat = os.stat(video_path)
    return {
        "path": os.path.abspath(video_path),
        "size": stat.st_size,
        "mtime": stat.st_mtime,
    }


def stub_matches_video(stub_path, video_path):
    """Return True only if stub_path exists AND was built from video_path."""
    meta_path = _stub_meta_path(stub_path)
    if not os.path.exists(stub_path) or not os.path.exists(meta_path):
        return False
    try:
        with open(meta_path) as f:
            saved = json.load(f)
        return saved == _video_fingerprint(video_path)
    except Exception:
        return False


def save_stub_meta(stub_path, video_path):
    """Write a sidecar .meta.json recording which video the stub was built from."""
    with open(_stub_meta_path(stub_path), "w") as f:
        json.dump(_video_fingerprint(video_path), f)


def save_video(output_video_frames, output_video_path):
    if not os.path.exists(os.path.dirname(output_video_path)):
        os.mkdir(os.path.dirname(output_video_path))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, 24.0, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()
