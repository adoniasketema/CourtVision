import os
import pickle

import pandas as pd
from ultralytics import YOLO

from utils.video_utils import stub_matches_video, save_stub_meta
from utils.hw_utils import get_optimal_device_and_precision


class BallTracker:
    """
    Detects and tracks the basketball across video frames.

    Detection output format (one dict per frame):
        {1: {"bbox": [x1, y1, x2, y2]}}   — ball found
        {}                                   — ball not found

    After calling interpolate_ball_positions() all frames have an entry.
    """

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_frames(self, frames):
        detections = []
        device, use_half = get_optimal_device_and_precision()
        batch_size = 32
        for i in range(0, len(frames), batch_size):
            batch = frames[i : i + batch_size]
            print(f"Processing ball detections for frames {i} to {min(i + batch_size, len(frames))} on [{device.upper()}]...")
            batch_dets = self.model.predict(
                batch,
                conf=0.3,
                verbose=False,
                device=device,
                half=use_half,
                batch=len(batch),
            )
            detections += batch_dets
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None, video_path=None):
        """
        Return per-frame ball detections, optionally loading/saving from a stub.
        """
        if read_from_stub and stub_path:
            if stub_matches_video(stub_path, video_path) if video_path else os.path.exists(stub_path):
                print(f"  Loading ball stub from {stub_path}")
                with open(stub_path, "rb") as f:
                    return pickle.load(f)
            elif video_path:
                print(f"  Ball stub is stale or missing — regenerating for {video_path}")

        detections = self.detect_frames(frames)
        ball_tracks = []

        for detection in detections:
            cls_names_inv = {v: k for k, v in detection.names.items()}
            ball_class_id = cls_names_inv.get("Ball", cls_names_inv.get("ball", -1))

            ball_tracks.append({})

            if ball_class_id == -1:
                continue

            # Collect all ball detections and take highest-confidence one
            candidates = []
            for box in detection.boxes:
                if int(box.cls[0]) == ball_class_id:
                    conf = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()
                    candidates.append((conf, bbox))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                ball_tracks[-1][1] = {"bbox": candidates[0][1]}

        if stub_path:
            os.makedirs(os.path.dirname(stub_path) or ".", exist_ok=True)
            with open(stub_path, "wb") as f:
                pickle.dump(ball_tracks, f)
            if video_path:
                save_stub_meta(stub_path, video_path)

        return ball_tracks

    # ------------------------------------------------------------------
    # Interpolation
    # ------------------------------------------------------------------

    def interpolate_ball_positions(self, ball_positions):
        """
        Fill in frames where the ball was not detected using pandas interpolation.

        Parameters
        ----------
        ball_positions : list of dict  — output of get_object_tracks()

        Returns
        -------
        list of dict  — same format, but every frame has a bbox entry
        """
        raw = []
        for entry in ball_positions:
            if 1 in entry and "bbox" in entry[1]:
                raw.append(entry[1]["bbox"])
            else:
                raw.append([None, None, None, None])

        df = pd.DataFrame(raw, columns=["x1", "y1", "x2", "y2"])
        df = df.astype(float)
        if df.dropna().empty:
            print("  Warning: no ball detections found — cannot interpolate.")
            return [{} for _ in ball_positions]
        df = df.interpolate()
        df = df.bfill()

        result = []
        for _, row in df.iterrows():
            if pd.notna(row["x1"]):
                result.append(
                    {"bbox": [row["x1"], row["y1"], row["x2"], row["y2"]]}
                )
            else:
                result.append({"bbox": None})

        # Wrap in the {1: ...} format expected by main.py
        return [{1: entry} if entry["bbox"] is not None else {} for entry in result]
