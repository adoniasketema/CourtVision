import cv2
import numpy as np
from collections import defaultdict

SPEED_WINDOW = 5   # frames used for rolling-average speed
SIDEBAR_WIDTH = 220
_FPS_TO_MPH = 3600 / 5280  # feet/s → mph


class SpeedDistanceDrawer:
    """Calculates player speed and distance from tactical positions, then draws them.

    Speed (km/h) is shown as a badge circle above each player on the game frame.
    Cumulative distance (m) is shown in a sidebar panel appended to the right.
    """

    # ── Calculation ───────────────────────────────────────────────────────────

    def calculate(
        self,
        tactical_player_positions,
        fps,
        minimap_w,
        minimap_h,
        court_w_ft=94,
        court_h_ft=50,
    ):
        """Derive per-frame speeds (mph) and running cumulative distances (ft) from minimap coords.

        Args:
            tactical_player_positions: list of per-frame dicts {player_id: (x_px, y_px)}.
            fps: video frame rate.
            minimap_w / minimap_h: minimap dimensions in pixels.
            court_w_ft / court_h_ft: real court dimensions in feet (NBA: 94 × 50).

        Returns:
            per_frame_speeds: list of {player_id: speed_mph} per frame.
            cumulative_distances: list of {player_id: dist_ft_so_far} per frame.
        """
        ft_per_px_x = court_w_ft / minimap_w
        ft_per_px_y = court_h_ft / minimap_h

        prev_positions = {}                        # player_id → (x_px, y_px)
        running_totals = defaultdict(float)        # player_id → cumulative feet
        dist_window = defaultdict(list)            # player_id → [(frame_idx, dist_ft)]

        per_frame_speeds = []
        cumulative_distances = []

        for frame_idx, frame_positions in enumerate(tactical_player_positions):
            frame_speeds = {}

            for player_id, (x, y) in frame_positions.items():
                if player_id in prev_positions:
                    px, py = prev_positions[player_id]
                    dx_ft = (x - px) * ft_per_px_x
                    dy_ft = (y - py) * ft_per_px_y
                    dist_ft = float(np.sqrt(dx_ft ** 2 + dy_ft ** 2))

                    running_totals[player_id] += dist_ft

                    # Keep only the last SPEED_WINDOW frames in the buffer
                    dist_window[player_id].append((frame_idx, dist_ft))
                    dist_window[player_id] = [
                        (fi, d)
                        for fi, d in dist_window[player_id]
                        if frame_idx - fi < SPEED_WINDOW
                    ]

                    avg_dist_ft = sum(d for _, d in dist_window[player_id]) / len(
                        dist_window[player_id]
                    )
                    # feet/frame * fps = feet/s; * _FPS_TO_MPH = mph
                    speed_mph = round(avg_dist_ft * fps * _FPS_TO_MPH, 1)
                    frame_speeds[player_id] = speed_mph
                else:
                    frame_speeds[player_id] = 0.0

                prev_positions[player_id] = (x, y)

            per_frame_speeds.append(frame_speeds)
            # Snapshot of running totals for this frame (copy so it doesn't mutate)
            cumulative_distances.append(dict(running_totals))

        return per_frame_speeds, cumulative_distances

    # ── Speed badges on game frames ───────────────────────────────────────────

    def annotate_speed(self, frames, player_tracks, per_frame_speeds, player_teams):
        """Draw a circular speed badge above each player's head on the game frames.

        Args:
            frames: list of annotated game frames (BGR).
            player_tracks: per-frame list of {player_id: {bbox}}.
            per_frame_speeds: output of calculate() — per-frame {player_id: speed_kmh}.
            player_teams: {player_id: team_id}.

        Returns:
            List of frames with speed badges drawn.
        """
        for frame_idx in range(len(frames)):
            frame = frames[frame_idx]

            if frame_idx >= len(per_frame_speeds) or frame_idx >= len(player_tracks):
                continue

            frame_speeds = per_frame_speeds[frame_idx]
            frame_players = player_tracks[frame_idx]

            for player_id, player_data in frame_players.items():
                speed = frame_speeds.get(player_id)
                if speed is None:
                    continue

                x1, y1, x2, _ = map(int, player_data["bbox"])
                cx = (x1 + x2) // 2
                # Place badge above the player's head
                cy = max(y1 - 35, 30)

                team_id = player_teams.get(player_id, 1)
                fill_color = (238, 245, 255) if team_id == 1 else (0, 0, 128)
                text_color = (0, 0, 0) if team_id == 1 else (255, 255, 255)

                # Badge circle
                radius = 22
                cv2.circle(frame, (cx, cy), radius, fill_color, cv2.FILLED)
                cv2.circle(frame, (cx, cy), radius, (0, 0, 0), 1)

                # Speed value centred inside circle
                speed_text = f"{speed:.0f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                (tw, th), _ = cv2.getTextSize(speed_text, font, 0.45, 1)
                cv2.putText(
                    frame,
                    speed_text,
                    (cx - tw // 2, cy + th // 2),
                    font,
                    0.45,
                    text_color,
                    1,
                )

                # "mph" unit label just below the badge
                unit = "mph"
                (uw, _), _ = cv2.getTextSize(unit, font, 0.3, 1)
                cv2.putText(
                    frame,
                    unit,
                    (cx - uw // 2, cy + radius + 11),
                    font,
                    0.3,
                    fill_color,
                    1,
                )

            frames[frame_idx] = frame
        return frames

    # ── Distance sidebar ──────────────────────────────────────────────────────

    def draw_sidebar(self, frames, cumulative_distances, player_teams):
        """Append a dark sidebar on the right of every frame showing running distances.

        The distance value updates each frame so viewers see how far each player
        has travelled up to that point in the video.

        Args:
            frames: list of BGR frames (may already include the minimap bottom strip).
            cumulative_distances: output of calculate() — per-frame {player_id: dist_m}.
            player_teams: {player_id: team_id}.

        Returns:
            List of frames with sidebar appended on the right.
        """
        team1_players = sorted(pid for pid, t in player_teams.items() if t == 1)
        team2_players = sorted(pid for pid, t in player_teams.items() if t == 2)

        for frame_idx in range(len(frames)):
            frame = frames[frame_idx]
            h, w = frame.shape[:2]
            sidebar = np.full((h, SIDEBAR_WIDTH, 3), (28, 28, 28), dtype=np.uint8)

            dists = cumulative_distances[frame_idx] if frame_idx < len(cumulative_distances) else {}

            # ── Header ──────────────────────────────────────────────────────
            cv2.putText(
                sidebar, "DISTANCE", (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1,
            )
            cv2.line(sidebar, (12, 38), (SIDEBAR_WIDTH - 12, 38), (70, 70, 70), 1)

            y = 62
            row_h = 26
            font = cv2.FONT_HERSHEY_SIMPLEX

            def draw_team_section(players, team_id):
                nonlocal y
                team_label_color = (200, 220, 255) if team_id == 1 else (140, 140, 255)
                dot_fill = (238, 245, 255) if team_id == 1 else (0, 0, 160)

                cv2.putText(
                    sidebar, f"Team {team_id}",
                    (12, y), font, 0.45, team_label_color, 1,
                )
                y += 20
                cv2.line(sidebar, (12, y), (SIDEBAR_WIDTH - 12, y), (55, 55, 55), 1)
                y += 10

                for pid in players:
                    if y + row_h > h - 8:
                        break
                    dist = dists.get(pid, 0.0)

                    # Coloured dot
                    cv2.circle(sidebar, (20, y - 4), 6, dot_fill, cv2.FILLED)

                    # Player label + distance
                    cv2.putText(
                        sidebar,
                        f"P{pid}",
                        (32, y),
                        font, 0.4, (200, 200, 200), 1,
                    )
                    dist_str = f"{dist:.1f} ft"
                    (dw, _), _ = cv2.getTextSize(dist_str, font, 0.4, 1)
                    cv2.putText(
                        sidebar,
                        dist_str,
                        (SIDEBAR_WIDTH - dw - 10, y),
                        font, 0.4, (180, 220, 180), 1,
                    )
                    y += row_h

                y += 10  # gap between teams

            draw_team_section(team1_players, 1)
            draw_team_section(team2_players, 2)

            frames[frame_idx] = np.hstack([frame, sidebar])
            if frame_idx % 50 == 0:
                import gc; gc.collect()

        import gc; gc.collect()
        return frames
