import math


def get_center_of_bbox(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def get_bbox_width(bbox):
    return bbox[2] - bbox[0]


def get_foot_position(bbox):
    x1, _, x2, y2 = bbox
    return ((x1 + x2) / 2, y2)


def measure_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def measure_xy_distance(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])


def get_closest_player_to_ball(players, ball_pos):
    min_dist = float("inf")
    closest_id = -1
    for player_id, player_data in players.items():
        foot = get_foot_position(player_data["bbox"])
        dist = measure_distance(foot, ball_pos)
        if dist < min_dist:
            min_dist = dist
            closest_id = player_id
    return closest_id
