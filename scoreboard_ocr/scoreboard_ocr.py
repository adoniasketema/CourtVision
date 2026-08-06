import cv2
import numpy as np
import pytesseract
import re
from collections import Counter

class ScoreboardOCR:
    def __init__(self, sample_rate_frames=30):
        self.sample_rate_frames = sample_rate_frames
        
    def _crop_scoreboard(self, frame):
        h, w = frame.shape[:2]
        # Crop the bottom 20% and middle 60% of the screen where sports scoreboards usually sit
        crop_y1 = int(h * 0.80)
        crop_y2 = h
        crop_x1 = int(w * 0.20)
        crop_x2 = int(w * 0.80)
        return frame[crop_y1:crop_y2, crop_x1:crop_x2]
        
    def _preprocess_for_ocr(self, img):
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Increase contrast and resize to improve OCR accuracy
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        gray = cv2.resize(gray, (0,0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        # Thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return thresh

    def _extract_text(self, img):
        try:
            # psm 11 = Sparse text with as much text as possible in no particular order
            custom_config = r'--oem 3 --psm 11'
            text = pytesseract.image_to_string(img, config=custom_config)
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def process_video(self, frames):
        print(f"Running Scoreboard OCR on {len(frames)} frames...")
        team_names = []
        score_timeline = []  # List of (frame_idx, score1, score2)
        
        for i in range(0, len(frames), self.sample_rate_frames):
            frame = frames[i]
            scoreboard_img = self._crop_scoreboard(frame)
            processed_img = self._preprocess_for_ocr(scoreboard_img)
            text = self._extract_text(processed_img)
            
            if not text:
                continue
                
            text = text.replace('\n', ' ')
            
            # Find contiguous uppercase words (at least 3 letters) to extract Team Names
            team_strings = re.findall(r'[A-Z]{3,}(?:\s+[A-Z]{3,})*', text)
            if len(team_strings) >= 2:
                team_names.append((team_strings[0], team_strings[-1]))
            
            # Find all numbers
            numbers = [int(n) for n in re.findall(r'\b\d+\b', text)]
            valid_scores = [n for n in numbers if n <= 150]
            
            if len(valid_scores) >= 2:
                # Heuristic: the largest two numbers are likely the scores (ignoring quarter '1st' or ranking '3', '19')
                sorted_scores = sorted(valid_scores, reverse=True)
                s1, s2 = sorted_scores[0], sorted_scores[1]
                
                # Keep them in the order they appeared on screen (left team vs right team)
                final_pair = [n for n in valid_scores if n == s1 or n == s2]
                if len(final_pair) >= 2:
                    score_timeline.append((i, final_pair[0], final_pair[-1]))
                    
        # Determine consensus team names over the whole video
        team_1_name = "TEAM 1"
        team_2_name = "TEAM 2"
        if team_names:
            most_common = Counter(team_names).most_common(1)[0][0]
            team_1_name, team_2_name = most_common
            
        # Detect scoring events (when the score value jumps)
        scoring_events = []
        last_s1, last_s2 = None, None
        
        for frame_idx, s1, s2 in score_timeline:
            if last_s1 is not None and last_s2 is not None:
                if s1 > last_s1:
                    scoring_events.append({"frame": frame_idx, "team": 1, "points": s1 - last_s1, "new_score": s1})
                if s2 > last_s2:
                    scoring_events.append({"frame": frame_idx, "team": 2, "points": s2 - last_s2, "new_score": s2})
            last_s1, last_s2 = s1, s2
            
        # Final scores
        final_score_1 = score_timeline[-1][1] if score_timeline else 0
        final_score_2 = score_timeline[-1][2] if score_timeline else 0

        return {
            "team_1_name": team_1_name,
            "team_2_name": team_2_name,
            "score_1": final_score_1,
            "score_2": final_score_2,
            "events": scoring_events
        }
