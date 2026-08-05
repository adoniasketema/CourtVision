class PassDetector:
    """
    Detects passes and interceptions from per-frame ball control data.

    Args:
        min_possession_frames: minimum consecutive frames a player must hold
            possession before the possession run counts. Shorter runs are
            treated as noise and skipped.
    """

    def __init__(self, min_possession_frames=5):
        self.min_possession_frames = min_possession_frames

    def detect(self, ball_control):
        """
        Analyse possession transitions across all frames.

        Parameters
        ----------
        ball_control : list of (player_id, team_id)
            One entry per frame.  player_id == -1 and team_id == 0 means
            no possession.

        Returns
        -------
        dict  e.g. {"team_1": {"passes": N, "interceptions": N}, ...}
        """
        stats = {
            "team_1": {"passes": 0, "interceptions": 0},
            "team_2": {"passes": 0, "interceptions": 0},
        }

        # Build possession runs, filtering noise
        runs = []  # list of (player_id, team_id, start_frame, end_frame)
        current_player, current_team, run_start = None, None, None

        for i, (player_id, team_id) in enumerate(ball_control):
            if team_id == 0 or player_id == -1:
                # No possession — flush current run
                if current_team is not None:
                    run_len = i - run_start
                    if run_len >= self.min_possession_frames:
                        runs.append((current_player, current_team, run_start, i - 1))
                current_player, current_team, run_start = None, None, None
                continue

            if current_team is None:
                current_player, current_team, run_start = player_id, team_id, i
            elif player_id != current_player or team_id != current_team:
                # Possession changed
                run_len = i - run_start
                if run_len >= self.min_possession_frames:
                    runs.append((current_player, current_team, run_start, i - 1))
                current_player, current_team, run_start = player_id, team_id, i

        # Flush last run
        if current_team is not None:
            run_len = len(ball_control) - run_start
            if run_len >= self.min_possession_frames:
                runs.append((current_player, current_team, run_start, len(ball_control) - 1))

        print(f"  [PassDetector] Validated {len(runs)} structured possession phases (possession threshold: {self.min_possession_frames} frames).")

        # Count transitions
        for i in range(1, len(runs)):
            prev_player, prev_team, _, _ = runs[i - 1]
            curr_player, curr_team, _, _ = runs[i]

            if curr_team == prev_team:
                # Same team, different player → pass
                if curr_player != prev_player:
                    stats[f"team_{prev_team}"]["passes"] += 1
            else:
                # Different team → interception credited to team that gained possession
                stats[f"team_{curr_team}"]["interceptions"] += 1

        return stats
