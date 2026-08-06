import cv2
import numpy as np

TEAM_1_COLOR = (238, 245, 255)  # seashell (BGR)
TEAM_2_COLOR = (0, 0, 128)      # maroon   (BGR)
BALL_HIGHLIGHT_COLOR = (0, 0, 255)


class TacticalViewDrawer:
    """Draws a court minimap appended as a strip at the bottom of each frame."""

    def draw(
        self,
        video_frames,
        court_image_path,
        width,
        height,
        tactical_court_keypoints,
        tactical_player_positions=None,
        player_assignment=None,
        ball_aquisition=None,
    ):
        """
        Args:
            video_frames: list of BGR frames.
            court_image_path: path to the court background image.
            width: minimap width in pixels.
            height: minimap height in pixels.
            tactical_court_keypoints: list of (x, y) tuples in minimap space.
            tactical_player_positions: list of per-frame dicts {player_id: (x, y)}.
            player_assignment: dict {player_id: team_id} (global, not per-frame).
            ball_aquisition: list of player_id with ball per frame (or None).

        Returns:
            List of frames with the minimap strip appended at the bottom.
        """
        court_image = cv2.imread(court_image_path)
        if court_image is None:
            raise FileNotFoundError(f"Court image not found: {court_image_path}")
        court_image = cv2.resize(court_image, (width, height))

        for index in range(len(video_frames)):
            frame = video_frames[index]
            frame_h, frame_w = frame.shape[:2]

            # ── Build bottom minimap panel (same width as the video frame) ──────
            panel = np.zeros((height, frame_w, 3), dtype=np.uint8)

            # Centre the court image horizontally in the panel
            x_offset = (frame_w - width) // 2
            if x_offset >= 0:
                panel[:, x_offset : x_offset + width] = court_image
            else:
                # Court wider than frame — crop symmetrically
                crop = -x_offset
                panel[:, :frame_w] = court_image[:, crop : crop + frame_w]

            # ── Draw tactical keypoints ──────────────────────────────────────────
            for keypt_idx, keypt in enumerate(tactical_court_keypoints):
                kx, ky = keypt
                kx += x_offset
                cv2.circle(panel, (kx, ky), 4, (0, 255, 0), -1)

            # ── Draw player positions ────────────────────────────────────────────
            if tactical_player_positions is not None and index < len(tactical_player_positions):
                frame_positions = tactical_player_positions[index]
                player_with_ball = ball_aquisition[index] if ball_aquisition is not None else None

                for player_id, (px, py) in frame_positions.items():
                    team_id = player_assignment.get(player_id, 1) if player_assignment else 1
                    color = TEAM_1_COLOR if team_id == 1 else TEAM_2_COLOR

                    draw_x = px + x_offset
                    draw_y = py

                    cv2.circle(panel, (draw_x, draw_y), 7, color, -1)
                    cv2.putText(
                        panel,
                        f"P{player_id}",
                        (draw_x + 5, draw_y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35,
                        color,
                        1,
                    )

                    if player_with_ball is not None and player_id == player_with_ball:
                        cv2.circle(panel, (draw_x, draw_y), 11, BALL_HIGHLIGHT_COLOR, 2)

            # ── Stack: game frame on top, minimap panel on bottom ────────────────
            video_frames[index] = np.vstack([frame, panel])

        return video_frames
