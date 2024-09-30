from model.transformation import Transformation2D
import numpy as np

class Viewport:

    def __init__(self, window):
        self.window = window

    def transform(self, drawable):
        points = []
        drawable = drawable.__class__(drawable.name, drawable.points, drawable.color)
        drawable = Transformation2D(drawable).rotation(\
                   np.radians(self.window.angle), self.window.get_offset()).escalation_relative_to_a_point(\
                   [1/(self.window.width/2), 1/(self.window.height/2)], self.window.get_offset()).apply()

        for point in drawable.points:
            window_bounds = self.window.get_bounds()
            x_viewport = ((point[0] - window_bounds[0]) / (window_bounds[1] - window_bounds[0])) * (self.bounds[1] - self.bounds[0])
            y_viewport = (1 - (point[1] - window_bounds[2]) / (window_bounds[3] - window_bounds[2])) * (self.bounds[3] - self.bounds[2])
            points.append([x_viewport, y_viewport])        
        return drawable.__class__(drawable.name, points, drawable.color)

    def set_window(self, window):
        self.window = window
    
    def set_aspect_ratio(self, aspect_ratio):
        self.width = aspect_ratio[0]
        self.height = aspect_ratio[1]
        self.bounds = (0, self.width, 0, self.height)