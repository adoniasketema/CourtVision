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

        output_frames = []
        for index, frame in enumerate(frames):
            if index >= len(court_keypoints):
                break
            annotated_frame = frame.copy()
            keypoints = court_keypoints[index]
            annotated_frame = vertex_annotator.annotate(scene=annotated_frame, key_points=keypoints)
            annotated_frame = vertex_label_annotator.annotate(scene=annotated_frame, key_points=keypoints)
            output_frames.append(annotated_frame)

        return output_frames