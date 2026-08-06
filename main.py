import json
import os

import cv2
import numpy as np

from utils import read_video, save_video
from utils.drawing_utils import draw_ellipse, draw_triangle, draw_team_ball_control
from trackers import PlayerTracker, BallTracker
from player_ball_assigner import PlayerBallAssigner
from pass_detector import PassDetector
from court_keypoint_detector import CourtKeypointDetector
from tactical_view_convert import TacticalViewConvert
import supervision as sv
from drawings import TacticalViewDrawer, SpeedDistanceDrawer, CourtKeypointDrawer
from team_assigner.team_assigner import TeamAssigner

# ── Constants ────────────────────────────────────────────────────────────────
TEAM_1_COLOR = (0, 0, 255)    # red   (BGR)
TEAM_2_COLOR = (255, 255, 0)  # yellow (BGR)
BALL_COLOR   = (0, 255, 0)    # green  (BGR)

MODEL_PATH              = "models/player_detector.pt"
BALL_MODEL_PATH         = "models/ball_detector.pt"
COURT_KEYPOINT_MODEL    = "models/court_keypoint_detector.pt"
COURT_IMAGE_PATH        = "assets/court_images/duke_basketball_court.jpg"
INPUT_VIDEO             = "input_videos/video_2.mp4"
OUTPUT_VIDEO            = "output_videos/output_video.mp4"

os.makedirs("stubs", exist_ok=True)
os.makedirs("output_videos", exist_ok=True)


def run_pipeline(input_path: str, output_path: str) -> dict:
    """Run the full analysis pipeline on a video and return stats.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the annotated output video will be saved.

    Returns:
        Stats dict: { team_1: { ball_acquisition_pct, passes, interceptions },
                      team_2: { ... } }
    """
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    player_stub = f"stubs/{base_name}_player_tracks.pkl"
    ball_stub = f"stubs/{base_name}_ball_tracks.pkl"

    # ── 1. Load video ─────────────────────────────────────────────────────────
    print("Reading video...")
    _cap = cv2.VideoCapture(input_path)
    video_fps = _cap.get(cv2.CAP_PROP_FPS) or 24.0
    _cap.release()

    video_frames = read_video(input_path)
    print(f"  {len(video_frames)} frames loaded at {video_fps:.1f} fps.")

    # ── 2. Player tracking ────────────────────────────────────────────────────
    print("Running player tracker...")
    player_tracker = PlayerTracker(MODEL_PATH)
    player_tracks = player_tracker.get_object_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=player_stub,
        video_path=input_path,
    )
    del player_tracker
    import gc; gc.collect()

    # ── 3. Ball tracking ──────────────────────────────────────────────────────
    print("Running ball tracker...")
    ball_tracker = BallTracker(BALL_MODEL_PATH)
    ball_tracks = ball_tracker.get_object_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=ball_stub,
        video_path=input_path,
    )

    # ── 4. Ball interpolation ─────────────────────────────────────────────────
    print("Interpolating ball positions...")
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)
    del ball_tracker
    gc.collect()

    # Guard: stubs from a different video may have a different frame count.
    num_frames = min(len(video_frames), len(player_tracks), len(ball_tracks))
    if num_frames < len(video_frames):
        print(f"  Warning: track stubs have {num_frames} frames; "
              f"video has {len(video_frames)}. Capping to {num_frames}.")
    video_frames  = video_frames[:num_frames]
    player_tracks = player_tracks[:num_frames]
    ball_tracks   = ball_tracks[:num_frames]

    # ── 5 & 6. Team assignment ────────────────────────────────────────────────
    print("Assigning player teams...")
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames, player_tracks)
    player_teams = team_assigner.track_to_team
    del team_assigner
    gc.collect()

    # ── 7. Ball possession per frame ──────────────────────────────────────────
    print("Computing ball possession...")
    player_ball_assigner = PlayerBallAssigner()
    team_ball_control = []
    player_ball_control = []

    for frame_num, players in enumerate(player_tracks):
        ball_entry = ball_tracks[frame_num]
        ball_bbox = ball_entry.get(1, {}).get("bbox") if ball_entry else None

        if ball_bbox is not None:
            player_id = player_ball_assigner.assign_ball_to_player(players, ball_bbox)
            player_ball_control.append(player_id)
            if player_id != -1:
                team_ball_control.append(player_teams.get(player_id, 0))
            else:
                team_ball_control.append(0)
        else:
            player_ball_control.append(-1)
            team_ball_control.append(0)

    team_ball_control_np = np.array(team_ball_control)
    del player_ball_assigner
    gc.collect()

    # ── 8. Court keypoint detection ───────────────────────────────────────────
    print("Detecting court keypoints...")
    court_stub = f"stubs/{base_name}_court_keypoints.pkl"
    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_MODEL)
    court_keypoints = court_keypoint_detector.detect_keypoints(
        video_frames,
        read_from_stub=True,
        stub_path=court_stub,
    )
    court_keypoints = court_keypoints[:num_frames]
    del court_keypoint_detector
    gc.collect()

    # ── 9. Tactical view transformation ──────────────────────────────────────
    print("Transforming to tactical view...")
    tactical_converter = TacticalViewConvert(COURT_IMAGE_PATH)
    validated_keypoints = tactical_converter.validate_keypoints(court_keypoints)
    del court_keypoints
    gc.collect()

    tactical_player_positions = tactical_converter.transform_to_tactical(
        validated_keypoints, player_tracks
    )

    # ── 10. Speed & distance calculation ─────────────────────────────────────
    print("Calculating player speed and distance...")
    speed_distance_drawer = SpeedDistanceDrawer()
    per_frame_speeds, cumulative_distances = speed_distance_drawer.calculate(
        tactical_player_positions,
        fps=video_fps,
        minimap_w=tactical_converter.width,
        minimap_h=tactical_converter.height,
        court_w_ft=tactical_converter.actual_width_ft,
        court_h_ft=tactical_converter.actual_height_ft,
    )

    # ── 11. Pass / interception detection ────────────────────────────────────
    print("Detecting passes and interceptions...")
    pass_detector = PassDetector(min_possession_frames=2)
    ball_control_pairs = list(zip(player_ball_control, team_ball_control))
    pass_stats = pass_detector.detect(ball_control_pairs)
    del pass_detector
    gc.collect()

    # ── 12. Annotation loop (In-Place RAM Optimization) ───────────────────────
    print("Annotating frames & sweeping system memory...")
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

    output_frames = video_frames

    for frame_num in range(len(output_frames)):
        frame = output_frames[frame_num]
        players = player_tracks[frame_num]
        ball_entry = ball_tracks[frame_num]

        for player_id, player_data in players.items():
            bbox = player_data["bbox"]
            team_id = player_teams.get(player_id, 1)
            color = TEAM_1_COLOR if team_id == 1 else TEAM_2_COLOR

            frame = draw_ellipse(frame, bbox, color, track_id=player_id)

            if player_ball_control[frame_num] == player_id:
                frame = draw_triangle(frame, bbox, BALL_COLOR)

        if ball_entry and 1 in ball_entry:
            ball_bbox = ball_entry[1].get("bbox")
            if ball_bbox is not None:
                frame = draw_triangle(frame, ball_bbox, BALL_COLOR)

        frame = draw_team_ball_control(frame, frame_num, team_ball_control_np)
        output_frames[frame_num] = frame

    # ── 13. Speed badges on game frames ──────────────────────────────────────
    print("Drawing speed badges...")
    output_frames = speed_distance_drawer.annotate_speed(
        output_frames, player_tracks, per_frame_speeds, player_teams
    )

    # ── 14. Tactical minimap (bottom strip) ───────────────────────────────────
    print("Drawing tactical minimap...")
    tactical_drawer = TacticalViewDrawer()
    output_frames = tactical_drawer.draw(
        video_frames=output_frames,
        court_image_path=COURT_IMAGE_PATH,
        width=tactical_converter.width,
        height=tactical_converter.height,
        tactical_court_keypoints=tactical_converter.key_points,
        tactical_player_positions=tactical_player_positions,
        player_assignment=player_teams,
        ball_aquisition=player_ball_control,
    )

    # ── 15. Court keypoint overlay ────────────────────────────────────────────
    print("Drawing court keypoints...")
    sv_keypoints = [sv.KeyPoints.from_ultralytics(kp) for kp in validated_keypoints]
    court_keypoint_drawer = CourtKeypointDrawer()
    output_frames = court_keypoint_drawer.draw_keypoints(output_frames, sv_keypoints)

    # ── 17. Distance sidebar (right panel) ────────────────────────────────────
    print("Drawing distance sidebar...")
    output_frames = speed_distance_drawer.draw_sidebar(
        output_frames, cumulative_distances, player_teams
    )

    # ── 18. Save video ────────────────────────────────────────────────────────
    print(f"Saving output to {output_path}...")
    save_video(output_frames, output_path)

    # ── 17. Stats ─────────────────────────────────────────────────────────────
    team_1_frames = int(np.sum(team_ball_control_np == 1))
    team_2_frames = int(np.sum(team_ball_control_np == 2))
    total = team_1_frames + team_2_frames

    # Final distances are the last frame's cumulative snapshot
    final_distances = cumulative_distances[-1] if cumulative_distances else {}

    stats = {
        "team_1": {
            "ball_acquisition_pct": round(team_1_frames / total * 100, 1) if total else 0,
            "passes": pass_stats["team_1"]["passes"],
            "interceptions": pass_stats["team_1"]["interceptions"],
        },
        "team_2": {
            "ball_acquisition_pct": round(team_2_frames / total * 100, 1) if total else 0,
            "passes": pass_stats["team_2"]["passes"],
            "interceptions": pass_stats["team_2"]["interceptions"],
        },
        "players": {
            str(pid): {
                "team": player_teams.get(pid, 0),
                "distance_ft": round(dist, 2),
            }
            for pid, dist in sorted(final_distances.items())
        },
    }

    return stats


def main():
    stats = run_pipeline(INPUT_VIDEO, OUTPUT_VIDEO)
    print("\n── Statistics ──────────────────────────────")
    print(json.dumps(stats, indent=2))
    print("────────────────────────────────────────────")
    print("Done.")


if __name__ == "__main__":
    main()
