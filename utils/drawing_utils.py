import cv2
import numpy as np


def draw_ellipse(frame, bbox, color, track_id=None):
    x1, y1, x2, y2 = map(int, bbox)
    x_center = (x1 + x2) // 2
    y_foot = y2
    width = x2 - x1

    cv2.ellipse(
        frame,
        center=(x_center, y_foot),
        axes=(width // 2, 8),
        angle=0,
        startAngle=-45,
        endAngle=235,
        color=color,
        thickness=2,
        lineType=cv2.LINE_4,
    )

    if track_id is not None:
        rect_w = 40
        rect_h = 20
        x1_r = x_center - rect_w // 2
        x2_r = x_center + rect_w // 2
        y1_r = y_foot - 15 - rect_h
        y2_r = y_foot - 15

        cv2.rectangle(frame, (x1_r, y1_r), (x2_r, y2_r), color, cv2.FILLED)

        text_x = x1_r + 6
        if track_id > 99:
            text_x -= 6

        cv2.putText(
            frame,
            str(track_id),
            (text_x, y1_r + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            2,
        )

    return frame


def draw_triangle(frame, bbox, color):
    x1, y1, x2, _ = map(int, bbox)
    x_center = (x1 + x2) // 2

    triangle_pts = np.array(
        [[x_center, y1], [x_center - 10, y1 - 20], [x_center + 10, y1 - 20]],
        dtype=np.int32,
    )

    cv2.drawContours(frame, [triangle_pts], 0, color, cv2.FILLED)
    cv2.drawContours(frame, [triangle_pts], 0, (0, 0, 0), 2)

    return frame


def draw_team_ball_control(frame, frame_num, team_ball_control):
    h, w = frame.shape[:2]

    x1 = int(w * 0.68)
    y1 = int(h * 0.78)
    x2 = w - 10
    y2 = h - 10

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), cv2.FILLED)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    control_so_far = team_ball_control[: frame_num + 1]
    team_1_frames = int(np.sum(control_so_far == 1))
    team_2_frames = int(np.sum(control_so_far == 2))
    total = team_1_frames + team_2_frames

    if total == 0:
        team_1_pct, team_2_pct = 0.0, 0.0
    else:
        team_1_pct = team_1_frames / total * 100
        team_2_pct = team_2_frames / total * 100

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.5, w / 2500)
    thickness = max(1, int(w / 900))
    line_gap = int((y2 - y1) * 0.45)

    cv2.putText(
        frame,
        f"Team 1: {team_1_pct:.1f}%",
        (x1 + 10, y1 + line_gap),
        font,
        font_scale,
        (0, 0, 0),
        thickness,
    )
    cv2.putText(
        frame,
        f"Team 2: {team_2_pct:.1f}%",
        (x1 + 10, y1 + line_gap * 2),
        font,
        font_scale,
        (0, 0, 0),
        thickness,
    )

    return frame
