

class Viewport:

    def __init__(self, window):
        self.window = window

    def transform(self, drawable):
        points = []

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