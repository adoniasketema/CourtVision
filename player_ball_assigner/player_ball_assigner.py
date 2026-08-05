from utils.bbox_utils import get_center_of_bbox, get_foot_position, measure_distance

MAX_PLAYER_BALL_DISTANCE = 70  # pixels


class PlayerBallAssigner:
    """
    Determines which player (if any) has possession of the ball in a frame.
    """

    def assign_ball_to_player(self, players, ball_bbox):
        """
        Parameters
        ----------
        players : dict  {track_id: {"bbox": [x1,y1,x2,y2]}}
        ball_bbox : list  [x1, y1, x2, y2]

        Returns
        -------
        int  track_id of the closest player within threshold, or -1
        """
        ball_pos = get_center_of_bbox(ball_bbox)

        min_dist = float("inf")
        assigned_player = -1

        for player_id, player_data in players.items():
            foot = get_foot_position(player_data["bbox"])
            dist = measure_distance(foot, ball_pos)

            if dist < MAX_PLAYER_BALL_DISTANCE and dist < min_dist:
                min_dist = dist
                assigned_player = player_id

        return assigned_player
