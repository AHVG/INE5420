import numpy as np


class Viewport: pass


class Viewport:
    WIDTH = 800
    HEIGHT = 600
    BOUNDS = (0, 800, 0, 600)

    def __init__(self, window):
        self.bounds = Viewport.BOUNDS
        self.window = window

    def transform(self, point):
        window_bounds = self.window.get_bounds()
        x_viewport = ((point[0] - window_bounds[0]) / (window_bounds[1] - window_bounds[0])) * (self.bounds[1] - self.bounds[0])
        y_viewport = (1 - (point[1] - window_bounds[2]) / (window_bounds[3] - window_bounds[2])) * (self.bounds[3] - self.bounds[2])
        return x_viewport, y_viewport
