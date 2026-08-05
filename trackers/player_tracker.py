import os
import pickle

import supervision as sv
from ultralytics import YOLO

from utils.video_utils import stub_matches_video, save_stub_meta
from utils.hw_utils import get_optimal_device_and_precision


class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def detect_frames(self, frames, max_frames=None):
        if max_frames is not None:
            frames = frames[:max_frames]

        from utils.hw_utils import get_optimal_device_and_precision, get_inference_batch_size
        device, use_half = get_optimal_device_and_precision()
        batch_size = get_inference_batch_size(device)
        detections = []
        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i : i + batch_size]
            print(f"Processing frames {i} to {min(i + batch_size, len(frames))} on [{device.upper()}]...")
            batch_detections = self.model.predict(
                batch_frames,
                conf=0.5,
                imgsz=640,
                verbose=False,
                device=device,
                half=use_half,
                batch=len(batch_frames),
            )
            detections += batch_detections
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None, max_frames=None, video_path=None):
        if read_from_stub and stub_path:
            if stub_matches_video(stub_path, video_path) if video_path else os.path.exists(stub_path):
                print(f"  Loading player stub from {stub_path}")
                with open(stub_path, "rb") as f:
                    return pickle.load(f)
            elif video_path:
                print(f"  Player stub is stale or missing — regenerating for {video_path}")

        detections = self.detect_frames(frames, max_frames=max_frames)
        tracks = []

        for frame_num, detection in enumerate(detections):
            cls_names_inv = {v: k for k, v in detection.names.items()}

            detection_supervision = sv.Detections.from_ultralytics(detection)
            detection_with_tracks = self.tracker.update_with_detections(
                detection_supervision
            )

            tracks.append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv.get("Player", -1):
                    tracks[frame_num][track_id] = {"bbox": bbox}

        if stub_path:
            os.makedirs(os.path.dirname(stub_path) or ".", exist_ok=True)
            with open(stub_path, "wb") as f:
                pickle.dump(tracks, f)
            if video_path:
                save_stub_meta(stub_path, video_path)

        return tracks
