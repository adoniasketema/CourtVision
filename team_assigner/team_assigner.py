import cv2
import numpy as np
from collections import defaultdict, Counter
from sklearn.cluster import KMeans

_MIN_SAMPLES = 10  # minimum feature samples per player to be included in clustering


def _crop_torso(frame, bbox):
    x1, y1, x2, y2 = map(int, bbox)
    h = y2 - y1
    w = x2 - x1
    # Take vertical middle 50% (torso) and horizontal center 60% to reduce background noise from edges
    torso_y1 = y1 + int(0.25 * h)
    torso_y2 = y1 + int(0.75 * h)
    torso_x1 = x1 + int(0.20 * w)
    torso_x2 = x2 - int(0.20 * w)
    if torso_x2 <= torso_x1:
        torso_x1, torso_x2 = x1, x2
    return frame[torso_y1:torso_y2, torso_x1:torso_x2]


def _jersey_feature(img):
    if img.size == 0 or img.shape[0] < 2 or img.shape[1] < 2:
        return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if hsv.size < 30:
        return None

    # Compute normalized histograms across H, S, and V channels without discarding low-saturation pixels.
    # This ensures accurate clustering for white jerseys (low S, high V), dark jerseys (low V),
    # and saturated colors (specific H and high S).
    h_hist = cv2.calcHist([hsv], [0], None, [24], [0, 180])
    s_hist = cv2.calcHist([hsv], [1], None, [16], [0, 256])
    v_hist = cv2.calcHist([hsv], [2], None, [16], [0, 256])

    cv2.normalize(h_hist, h_hist)
    cv2.normalize(s_hist, s_hist)
    cv2.normalize(v_hist, v_hist)

    return np.concatenate([h_hist.flatten(), s_hist.flatten(), v_hist.flatten()]).astype(np.float64)


class TeamAssigner:
    """
    Assigns players to teams by clustering per-player HSV feature embeddings
    into 2 groups via KMeans.
    """

    def __init__(self):
        self.track_to_team = {}  # {player_id: team_id (1 or 2)}

    def assign_team_color(self, frames, player_tracks):
        """
        Extract jersey feature vectors across all frames, cluster high-confidence players via KMeans,
        and assign every detected track to Team 1 or Team 2 based on centroid proximity.
        """
        player_features = defaultdict(list)

        for frame_num, players in enumerate(player_tracks):
            frame = frames[frame_num]
            for player_id, player_data in players.items():
                torso = _crop_torso(frame, player_data["bbox"])
                if torso.size > 0:
                    feat = _jersey_feature(torso)
                    if feat is not None:
                        player_features[player_id].append(feat)

        # Average features per player for clustering; start with high-sample players
        fit_embeddings = {
            pid: np.mean(feats, axis=0)
            for pid, feats in player_features.items()
            if len(feats) >= _MIN_SAMPLES
        }

        # Fallback if few long-lived tracks exist
        if len(fit_embeddings) < 2:
            fit_embeddings = {
                pid: np.mean(feats, axis=0)
                for pid, feats in player_features.items()
                if len(feats) >= 1
            }

        if len(fit_embeddings) < 2:
            print("  Warning: not enough player data to cluster teams. Defaulting all to team 1.")
            return

        X = np.array(list(fit_embeddings.values()), dtype=np.float64)
        kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(X)

        # Predict team cluster for ALL detected players (even those seen for < _MIN_SAMPLES frames)
        all_embeddings = {
            pid: np.mean(feats, axis=0)
            for pid, feats in player_features.items()
            if len(feats) > 0
        }

        predictions = {}
        for pid, feat in all_embeddings.items():
            pred_label = int(kmeans.predict(np.array([feat], dtype=np.float64))[0])
            predictions[pid] = pred_label

        # Align clusters so that Team 1 represents the larger cluster consistently
        team_a_label = Counter(predictions.values()).most_common(1)[0][0]
        self.track_to_team = {
            pid: (1 if label == team_a_label else 2)
            for pid, label in predictions.items()
        }
        print(f"  Team assignment complete: {len(self.track_to_team)} players assigned.")

    def get_player_team(self, frame, player_bbox, player_id, frame_num=0):
        """Return team ID (1 or 2) for the given player. Defaults to 1 if unseen."""
        return self.track_to_team.get(player_id, 1)

