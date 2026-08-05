import os
import sys
import pathlib
from copy import deepcopy
import numpy as np
from tactical_view_convert.Homography import Homography
from utils import get_foot_position

folder_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(folder_path,"../"))

class TacticalViewConvert:
    def __init__(self, court_image_path):
        self.court_image_path = court_image_path
        self.width=300
        self.height=161

        self.actual_width_ft = 94
        self.actual_height_ft = 50

        self.key_points = [
            # left edge
            (0,0),
            (0,int((3/self.actual_height_ft)*self.height)),
            (0,int((19/self.actual_height_ft)*self.height)),
            (0,int((31/self.actual_height_ft)*self.height)),
            (0,int((47/self.actual_height_ft)*self.height)),
            (0,int(self.height)),

            # Middle line
            (int(self.width/2),self.height),
            (int(self.width/2),0),

            # Left Free throw line
            (int((19/self.actual_width_ft)*self.width),int((19/self.actual_height_ft)*self.height)),
            (int((19/self.actual_width_ft)*self.width),int((31/self.actual_height_ft)*self.height)),

            # right edge
            (self.width,int(self.height)),
            (self.width,int((47/self.actual_height_ft)*self.height)),
            (self.width,int((31/self.actual_height_ft)*self.height)),
            (self.width,int((19/self.actual_height_ft)*self.height)),
            (self.width,int((3/self.actual_height_ft)*self.height)),
            (self.width,0),

            # Right Free throw line
            (int(((self.actual_width_ft-19)/self.actual_width_ft)*self.width),int((19/self.actual_height_ft)*self.height)),
            (int(((self.actual_width_ft-19)/self.actual_width_ft)*self.width),int((31/self.actual_height_ft)*self.height)),
        ]

    def validate_keypoints(self, keypoints):
        keypoints = deepcopy(keypoints)
        for frame_idx, keypt_result in enumerate(keypoints):
            if keypt_result.keypoints is None:
                continue
            keypt_data = keypt_result.keypoints.xy.tolist()[0]

            detected_idx = [i for i, kp in enumerate(keypt_data) if kp[0] > 0 and kp[1] > 0]
            if len(detected_idx) < 3:
                continue

            # Single voting pass: every pair (j, k) of other valid keypoints casts
            # one vote. Threshold 1.5 means only grossly misplaced keypoints
            # (>150% ratio deviation) accumulate enough invalid votes, so valid
            # keypoints with normal perspective distortion are preserved.
            # No while loop: avoids cascade where removing one keypoint shifts
            # votes for others and empties the pool.
            VOTE_THRESHOLD = 0.7
            invalid_kypts = set()
            for i in detected_idx:
                if i >= len(self.key_points):
                    break
                other_idx = [j for j in detected_idx if j != i and j < len(self.key_points)]
                if len(other_idx) < 2:
                    continue
                valid_votes = 0
                invalid_votes = 0
                for pi in range(len(other_idx)):
                    for pj in range(pi + 1, len(other_idx)):
                        j, k = other_idx[pi], other_idx[pj]
                        dist_ij = ((keypt_data[i][0] - keypt_data[j][0])**2 + (keypt_data[i][1] - keypt_data[j][1])**2)**0.5
                        dist_ik = ((keypt_data[i][0] - keypt_data[k][0])**2 + (keypt_data[i][1] - keypt_data[k][1])**2)**0.5
                        t_ij = ((self.key_points[i][0] - self.key_points[j][0])**2 + (self.key_points[i][1] - self.key_points[j][1])**2)**0.5
                        t_ik = ((self.key_points[i][0] - self.key_points[k][0])**2 + (self.key_points[i][1] - self.key_points[k][1])**2)**0.5
                        if t_ik == 0:
                            continue
                        prop_detected = dist_ij / dist_ik if dist_ik > 0 else float('inf')
                        prop_tactical = t_ij / t_ik
                        if abs(prop_detected - prop_tactical) / prop_tactical > VOTE_THRESHOLD:
                            invalid_votes += 1
                        else:
                            valid_votes += 1
                if invalid_votes > valid_votes and (valid_votes + invalid_votes) > 0:
                    keypoints[frame_idx].keypoints.xy[0][i] *= 0
                    keypoints[frame_idx].keypoints.xyn[0][i] *= 0
                    invalid_kypts.add(i)

        return keypoints

    def transform_to_tactical(self, keypoints_list, player_tracks):
        """Transform per-frame player foot positions into tactical (minimap) coordinates.

        Returns:
            List of dicts, one per frame: {player_id: (x_px, y_px)} in minimap space.
        """
        tactical_player_positions = []

        for frame_idx, (frame_keypoints, frame_tracks) in enumerate(zip(keypoints_list, player_tracks)):
            if frame_keypoints.keypoints is None:
                tactical_player_positions.append({})
                continue
            raw_keypoints = frame_keypoints.keypoints.xy.tolist()[0]  # list of [x, y] pairs in pixel space

            if not raw_keypoints:
                tactical_player_positions.append({})
                continue

            valid_indexes = [i for i, kp in enumerate(raw_keypoints) if kp[0] > 0 and kp[1] > 0]

            if len(valid_indexes) < 4:
                tactical_player_positions.append({})
                continue

            try:
                homography = Homography(
                    source=np.array([raw_keypoints[i] for i in valid_indexes], dtype=np.float32),
                    target=np.array([self.key_points[i] for i in valid_indexes], dtype=np.float32),
                )

                frame_tactical = {}
                for player_id, player_data in frame_tracks.items():
                    bbox = player_data["bbox"]
                    foot_pos = np.array([get_foot_position(bbox)], dtype=np.float32)
                    transformed = homography.transform(foot_pos)
                    tx, ty = transformed[0]
                    # Clamp to minimap bounds
                    tx = int(np.clip(tx, 0, self.width))
                    ty = int(np.clip(ty, 0, self.height))
                    frame_tactical[player_id] = (tx, ty)

                tactical_player_positions.append(frame_tactical)
            except ValueError as e:
                print(f"Error computing homography for frame {frame_idx}: {e}")
                tactical_player_positions.append({})

        return tactical_player_positions