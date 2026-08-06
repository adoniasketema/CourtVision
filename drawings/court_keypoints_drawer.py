import supervision as sv

class CourtKeypointDrawer:
    def __init__(self):
        self.keypoints_color = "#ff2c2c" # Red color for keypoints

    def draw_keypoints(self, frames, court_keypoints):
        vertex_annotator = sv.VertexAnnotator(color=sv.Color.from_hex(self.keypoints_color), radius = 8)
        vertex_label_annotator = sv.VertexLabelAnnotator(
            color=sv.Color.from_hex(self.keypoints_color), 
            text_color=sv.Color.WHITE, 
            text_scale=0.5, 
            text_thickness=1
        )

        for index in range(min(len(frames), len(court_keypoints))):
            keypoints = court_keypoints[index]
            frame = frames[index]
            frame = vertex_annotator.annotate(scene=frame, key_points=keypoints)
            frame = vertex_label_annotator.annotate(scene=frame, key_points=keypoints)
            frames[index] = frame

        return frames