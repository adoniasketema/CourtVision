Basketball Computer Vision Analysis System — Project Context for Claude Code
Project Overview
This is an NBA basketball analysis system built with machine learning, computer vision, and deep learning. The system processes basketball game video footage and extracts rich tactical and performance insights using multiple AI models.
Inspired by: YouTube Tutorial by Abdullah Tarek
Reference GitHub: https://github.com/abdullahtarek/basketball_analysis

Long-Term Vision
The current per-frame analysis pipeline is Phase 1 — the foundation for two larger goals:
Phase 2: Video Segment Classification
Automatically classify temporal segments of game footage into tactical categories:

Offense types: half-court set, transition offense, pick-and-roll, isolation, fast break
Defense types: man-to-man, zone, press, transition defense
Neutral: dead ball, timeout, free throw, out-of-bounds

This will be built on top of the existing pipeline's per-frame features (player positions, possession, formation in top-down view, speed vectors) aggregated over time windows. Likely approach: train a temporal classifier (e.g. LSTM, Transformer, or 3D CNN) on sequences of extracted features rather than raw pixels.
Phase 3: Coach Workflow App — Film Study Playlist Tool
A web/desktop application for coaches to:

Browse and search processed game footage by play type, player, or time range
Auto-generate playlists of clips matching a category (e.g. "all pick-and-roll possessions")
Tag and annotate clips with custom labels and notes
Export clip compilations for team film sessions

Architecture implications to keep in mind while building Phase 1:

All per-clip metadata and stats should be stored in a queryable format (SQLite or Postgres), not just flat JSON/CSV
Video clips need to be indexable by timestamp — design output so segments can be cut and retrieved efficiently
The top-down tactical view is essential for the classifier — keep it as a first-class output, not just a visualization
Player track IDs should be stable and exportable so the app can filter by individual player across games
Consider a Clip / Possession / Segment data model early, since it will be the core unit of the coach app


What This System Does
Given a basketball game video, the system produces an annotated output video and statistics including:

Player & ball detection and tracking across all frames
Team assignment based on jersey color
Ball possession / acquisition percentage per team
Pass and interception counts per team
Player speed (in km/h or m/s) and distance covered (in meters)
Tactical top-down court view via perspective transformation
Court keypoint detection to understand spatial positioning


Technology Stack
ComponentTechnologyObject DetectionYOLOv8 (Ultralytics)Object TrackingByteTrack / supervision trackersTeam ClassificationZero-Shot Image Classification (Hugging Face)Keypoint DetectionCustom-trained YOLO keypoint modelPerspective TransformOpenCV getPerspectiveTransform / warpPerspectiveDeep Learning FrameworkPyTorchVideo ProcessingOpenCV (cv2)Data ManipulationNumPy, PandasVisualizationOpenCV drawing utilitiesSegment Classification (Phase 2)LSTM / Transformer over extracted featuresCoach App Backend (Phase 3)FastAPI + SQLite/PostgresCoach App Frontend (Phase 3)TBD (React or Electron)

Key External Resources

Basketball Player Detection Dataset: https://universe.roboflow.com/ (workspace: basketball detection)
Court Keypoint Dataset: https://universe.roboflow.com/fyp-3bw... (use the corrected dataset linked in video description)
Zero-Shot Classifier Model: https://huggingface.co/patrickjohncyh/fashion-clip
Supervision Library: https://github.com/roboflow/supervision (for tracking, annotation, ByteTrack)


Project Architecture / Module Breakdown
1. Object Detection & Tracking (detectors/, trackers/)

Use YOLOv8 pretrained on COCO, fine-tuned on a custom basketball dataset
Detects: player, ball, referee
Tracking is done with ByteTrack (via supervision library) to assign consistent IDs across frames
Separate tracker instances for players and the ball
Ball detection is sparse (occlusion, fast movement) → requires interpolation

Key classes/files:

PlayerTracker — wraps YOLO + ByteTrack for players
BallTracker — wraps YOLO + ByteTrack for ball; handles missing detections
Detection output format: {frame_num: [{track_id, bbox, class}, ...]}


2. Ball Interpolation (trackers/ball_tracker.py)

Ball is often undetected for several consecutive frames (occlusion, motion blur)
Use pandas interpolation (DataFrame.interpolate()) to fill in missing bounding box positions between known detections
Interpolate on the center (x, y) of the bounding box, then reconstruct full bbox


3. Team Assignment (team_assigner/)

Uses Zero-Shot Image Classification via Hugging Face (patrickjohncyh/fashion-clip or similar)
Crops each player's jersey region from the frame
Classifies jersey color/style into Team A or Team B without labeled training data
Assignment is done once per player (first N frames) and cached by track_id
Uses KMeans clustering on jersey pixel colors as a fallback/supplement

Key class: TeamAssigner

assign_team_color(frame, player_detections) — clusters jersey colors
get_player_team(frame, player_bbox, player_id) — returns team ID (1 or 2)


4. Ball Acquisition / Possession (player_ball_assigner/)

For each frame, determine which player (if any) has possession of the ball
Logic: find the player whose bounding box is closest to the ball's center position
Apply a distance threshold — if no player is within threshold, possession = None
Accumulate per-team possession counts across all frames
Output: ball_acquisition_percentage = {team1: X%, team2: Y%}

Key class: PlayerBallAssigner

assign_ball_to_player(players, ball_bbox) — returns player_id or -1


5. Pass & Interception Detection (pass_detector/)

A pass occurs when possession transfers between two players on the same team
An interception occurs when possession transfers between players on different teams
Track possession history frame-by-frame; detect transitions
Filter out noise: require possession to be held for a minimum number of frames before counting a transfer

Key logic:
pythonif current_team != previous_team:
    interceptions[current_team] += 1
elif current_player != previous_player and current_team == previous_team:
    passes[current_team] += 1

6. Court Keypoint Detection (court_keypoint_detector/)

Train a YOLO keypoint model on labeled basketball court images
Detects fixed landmark points on the court (e.g., corners of the paint, three-point line endpoints, center circle)
Keypoints define the mapping between pixel space and real-world court coordinates
Used as input to perspective transformation

Dataset: Custom Roboflow dataset with annotated court keypoints
Model output: List of (x, y) pixel coordinates for each keypoint per frame

7. Perspective Transformation (view_transformer/)

Maps the camera (perspective) view to a top-down (bird's-eye) tactical view
Uses OpenCV: cv2.getPerspectiveTransform(src_points, dst_points) to compute homography matrix
src_points: detected court keypoints in pixel space
dst_points: corresponding points in a normalized top-down court coordinate system (real-world meters)
Apply cv2.perspectiveTransform() to player positions to get their real-world court coordinates

Key class: ViewTransformer

transform_point(point) — converts pixel (x,y) to court meters (x,y)
Used to draw the tactical minimap overlay


8. Speed & Distance Calculator (speed_and_distance_estimator/)

Uses transformed (real-world) coordinates from the perspective transformer
Distance: Euclidean distance between player positions across consecutive frames
Speed: distance / time_elapsed — time derived from frame rate (fps)
Accumulate total distance and compute rolling speed window
Output annotations: speed (km/h) and distance (m) displayed next to each player

Key formulas:
pythondistance_meters = euclidean(pos_t1, pos_t2)  # in court coordinate space
speed_kmh = (distance_meters / frames_elapsed) * fps * 3.6

Data Flow (End-to-End Pipeline)
Input Video
    │
    ▼
[Frame Extraction] — OpenCV VideoCapture, process N frames at a time
    │
    ▼
[YOLO Detection] — players, ball, referees detected per frame
    │
    ▼
[ByteTrack Tracking] — assign consistent track IDs across frames
    │
    ├──► [Ball Interpolation] — fill missing ball positions
    │
    ├──► [Team Assignment] — zero-shot jersey classification per player ID
    │
    ├──► [Ball Possession Assignment] — which player/team holds the ball
    │
    ├──► [Pass / Interception Detection] — analyze possession transitions
    │
    ├──► [Court Keypoint Detection] — detect court landmarks in frame
    │
    ├──► [Perspective Transformation] — pixel → real-world court coords
    │
    └──► [Speed & Distance Estimation] — calculate movement metrics
    │
    ▼
[Annotation & Rendering] — draw bboxes, team colors, stats, tactical minimap
    │
    ▼
Output Annotated Video + Statistics JSON/CSV

Recommended Directory Structure
basketball_analysis/
├── input_videos/                  # Raw input game footage
├── output_videos/                 # Annotated output videos
├── models/                        # Trained model weights (.pt files)
│   ├── player_detector.pt         # Fine-tuned YOLO for players/ball
│   ├── court_keypoint_detector.pt # YOLO keypoint model for court
│   └── segment_classifier.pt      # (Phase 2) Temporal play-type classifier
├── trackers/
│   ├── player_tracker.py
│   └── ball_tracker.py
├── team_assigner/
│   └── team_assigner.py
├── player_ball_assigner/
│   └── player_ball_assigner.py
├── court_keypoint_detector/
│   └── court_keypoint_detector.py
├── view_transformer/
│   └── view_transformer.py
├── speed_and_distance_estimator/
│   └── speed_and_distance_estimator.py
├── segment_classifier/            # (Phase 2) Play-type classification
│   ├── feature_extractor.py       # Aggregates per-frame features into sequences
│   ├── classifier.py              # LSTM/Transformer model
│   └── labels.py                  # Play type label definitions
├── database/                      # (Phase 3) Persistence layer
│   ├── models.py                  # SQLAlchemy ORM: Segment, Game, Tag
│   ├── db.py                      # DB connection, migrations
│   └── queries.py                 # Reusable query helpers
├── api/                           # (Phase 3) Coach app backend
│   ├── main.py                    # FastAPI app
│   ├── routes/
│   │   ├── segments.py            # CRUD for segments/playlists
│   │   └── games.py
│   └── schemas.py                 # Pydantic request/response models
├── utils/
│   ├── video_utils.py             # read_video(), save_video(), cut_clip()
│   ├── bbox_utils.py
│   └── drawing_utils.py
├── training/
│   ├── train_player_detector.ipynb
│   ├── train_keypoint_detector.ipynb
│   └── train_segment_classifier.ipynb  # (Phase 2)
├── stubs/                         # Cached detection/tracking results (pickle)
│   ├── player_detections.pkl
│   └── ball_detections.pkl
├── main.py                        # Phase 1 pipeline entrypoint
└── requirements.txt

Important Implementation Notes
Detection Stubs / Caching

Re-running YOLO on every video frame is slow during development
Save detection results as .pkl files (stubs) after the first run
Load from stubs on subsequent runs using read_from_stub=True pattern
Controlled by flags in main.py

Bounding Box Conventions

All bboxes stored as [x1, y1, x2, y2] (top-left, bottom-right)
Player "foot position" = bottom-center of bbox: ((x1+x2)/2, y2) — used for court mapping
Ball position = center of bbox: ((x1+x2)/2, (y1+y2)/2)

Coordinate Systems

Pixel space: raw frame coordinates (e.g., 1920×1080)
Court space: real-world meters, origin at a court landmark

NBA full court: ~28.65m × 15.24m
Half court: ~14.33m × 15.24m



Team Color Assignment Edge Cases

Referees must be excluded from team assignment (detected as separate class, or filtered by jersey color)
Handle cases where the same player ID disappears and reappears (re-ID)
Goalkeepers / coaches near sideline may get misclassified

Frame Batching

Process video in batches of frames (e.g., 20-50 at a time) to manage memory
Track state (possession history, player positions) across batches


Common Utility Functions to Implement
python# bbox_utils.py
def get_center_of_bbox(bbox) -> tuple[float, float]
def get_bbox_width(bbox) -> float
def get_foot_position(bbox) -> tuple[float, float]  # bottom-center
def measure_distance(p1, p2) -> float               # Euclidean
def measure_xy_distance(p1, p2) -> tuple[float, float]
def get_closest_player_to_ball(players, ball_pos) -> int  # returns track_id

# video_utils.py  
def read_video(path) -> list[np.ndarray]             # returns list of frames
def save_video(frames, output_path, fps=24)

Training Notes
Fine-tuning YOLO for Player/Ball Detection

Base model: yolov8x.pt or yolov8n.pt (tradeoff: accuracy vs. speed)
Dataset: Roboflow basketball dataset (players, ball, referee classes)
Training: Ultralytics model.train(data='data.yaml', epochs=100, imgsz=640)

Training YOLO Keypoint Model

Dataset: Custom court keypoint dataset from Roboflow (use the CORRECTED dataset — see video description note)
YOLO pose/keypoint variant: yolov8x-pose.pt as base
Each image annotated with N keypoint locations on court lines/landmarks
Output: (x, y, confidence) per keypoint per frame


Key Hyperparameters & Constants
python# Detection
DETECTION_CONFIDENCE_THRESHOLD = 0.3
BALL_CLASS_ID = 0       # Adjust based on your dataset
PLAYER_CLASS_ID = 1
REFEREE_CLASS_ID = 2

# Possession
MAX_PLAYER_BALL_DISTANCE = 70   # pixels; tune based on video resolution

# Speed estimation
FRAMES_WINDOW = 5               # frames over which to average speed
FPS = 24                        # input video frame rate

# Court dimensions (meters) for perspective transform destination
COURT_WIDTH = 15.24             # meters (NBA)
COURT_LENGTH = 28.65            # meters (NBA)

Output Statistics Format
The pipeline should produce per-video stats structured as:
json{
  "team_1": {
    "ball_acquisition_pct": 58.3,
    "passes": 42,
    "interceptions": 7
  },
  "team_2": {
    "ball_acquisition_pct": 41.7,
    "passes": 35,
    "interceptions": 5
  },
  "players": {
    "1": { "distance_m": 312.4, "avg_speed_kmh": 14.2, "team": 1 },
    "7": { "distance_m": 289.1, "avg_speed_kmh": 12.8, "team": 2 }
  }
}
Future-Proof: Possession / Segment Data Model
Design with Phase 2 & 3 in mind. Each discrete possession or play segment should also be exportable as a structured record so it can be stored in a database and queried by the coach app:
python@dataclass
class Segment:
    segment_id: str           # UUID
    video_source: str         # source video filename/path
    start_frame: int
    end_frame: int
    start_time_sec: float
    end_time_sec: float
    team_possession: int      # 1 or 2
    play_type: str | None     # "pick_and_roll", "transition", etc. (Phase 2 output)
    player_ids: list[int]     # track IDs of players in segment
    passes: int
    turnovers: int
    top_down_frames: list     # serialized tactical view frames for classifier input
    tags: list[str]           # coach-added tags (Phase 3)
    notes: str | None         # coach annotations (Phase 3)
Store segments in SQLite (segments.db) alongside each processed video so the coach app can query: SELECT * FROM segments WHERE play_type = 'fast_break' AND team_possession = 1

Development Workflow

Setup: Install deps, download pretrained YOLO weights, set up Roboflow datasets
Stub generation: Run detection once on input video, save .pkl stubs
Module development: Build and test each module independently using stubs
Integration: Wire modules together in main.py
Training: Fine-tune custom models when baseline accuracy is insufficient
Evaluation: Check output video visually; validate stats against manual counts


Requirements
# Phase 1 — CV Pipeline
ultralytics>=8.0.0
supervision>=0.18.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
torch>=2.0.0
transformers>=4.30.0   # Hugging Face zero-shot classifier
Pillow>=9.0.0
scikit-learn>=1.3.0    # KMeans for jersey color clustering
roboflow               # Dataset management

# Phase 2 — Segment Classification
# (uses torch already listed above)

# Phase 3 — Coach App
fastapi>=0.110.0
uvicorn>=0.29.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-multipart       # video file uploads
ffmpeg-python          # clip cutting and export