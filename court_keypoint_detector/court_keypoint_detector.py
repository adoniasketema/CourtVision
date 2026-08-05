import os
import pickle
import sys
sys.path.append('../')
from ultralytics import YOLO
from utils.video_utils import stub_matches_video, save_stub_meta
from utils.hw_utils import get_optimal_device_and_precision

class CourtKeypointDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_keypoints(self, frames, read_from_stub=False, stub_path=None, video_path=None):
        if read_from_stub and stub_path:
            if stub_matches_video(stub_path, video_path) if video_path else os.path.exists(stub_path):
                print(f"  Loading court keypoint stub from {stub_path}")
                with open(stub_path, "rb") as f:
                    return pickle.load(f)
            elif video_path:
                print(f"  Court keypoint stub is stale or missing — regenerating for {video_path}")

        device, use_half = get_optimal_device_and_precision()
        batch_size = 32
        court_keypoints = []
        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i:i+batch_size]
            print(f"Processing court keypoints for frames {i} to {min(i + batch_size, len(frames))} on [{device.upper()}]...")
            detections_batch = self.model.predict(
                batch_frames,
                conf=0.5,
                verbose=False,
                device=device,
                half=use_half,
                batch=len(batch_frames),
            )
            for detection in detections_batch:
                court_keypoints.append(detection)

        if stub_path:
            os.makedirs(os.path.dirname(stub_path) or ".", exist_ok=True)
            with open(stub_path, "wb") as f:
                pickle.dump(court_keypoints, f)
            if video_path:
                save_stub_meta(stub_path, video_path)

        return court_keypoints