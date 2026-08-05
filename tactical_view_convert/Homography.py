import numpy as np
import cv2

class Homography:
    def __init__(self, source: np.ndarray, target: np.ndarray):
        if source.shape != target.shape:
            raise ValueError("Source and target points must have the same shape.")
        
        if source.shape[1] != 2:
            raise ValueError("Source and target points must be 2D.")
        
        source = source.astype(np.float32)
        target = target.astype(np.float32)

        self.m, _ = cv2.findHomography(source, target)
        if self.m is None:
            raise ValueError("Homography computation failed. Check the input points.")
        
    def transform(self, points: np.ndarray) -> np.ndarray:
        if points.shape[1] != 2:
            raise ValueError("Input points must be 2D.")
        
        if points.size == 0:
            return points # just return points, nothing to process

        points = points.reshape(-1, 1, 2).astype(np.float32)
        transformed_points = cv2.perspectiveTransform(points, self.m) # returns shape (N, 1, 2)
        return transformed_points.reshape(-1, 2).astype(np.float32)