from constants import INITIAL_WINDOW


class Window:

    def __init__(self):
        self.zoom_factor = 1.0
        self.offset = [0.0, 0.0]
        self.bounds = list(INITIAL_WINDOW)

    def increase_offset(self, offset):
        self.offset = [offset[0] + self.offset[0], offset[1] + self.offset[1]]
        self.bounds[0] += offset[0]
        self.bounds[1] += offset[0]
        self.bounds[2] += offset[1]
        self.bounds[3] += offset[1]

    def set_zoom(self, factor):
        self.zoom_factor = factor
        cx = (INITIAL_WINDOW[0] + INITIAL_WINDOW[1]) / 2
        cy = (INITIAL_WINDOW[2] + INITIAL_WINDOW[3]) / 2
        width = (INITIAL_WINDOW[1] - INITIAL_WINDOW[0]) * factor
        height = (INITIAL_WINDOW[3] - INITIAL_WINDOW[2]) * factor
        self.bounds[0] = self.offset[0] + cx - width / 2
        self.bounds[1] = self.offset[0] + cx + width / 2
        self.bounds[2] = self.offset[1] + cy - height / 2
        self.bounds[3] = self.offset[1] + cy + height / 2
    
    def zoom_in(self):
        self.set_zoom(self.zoom_factor + 0.05)

    def zoom_out(self):
        self.set_zoom(self.zoom_factor - 0.05)

    def move_up(self):
        self.increase_offset([0.0, 5.0])

    def move_down(self):
        self.increase_offset([0.0, -5.0])

    def move_left(self):
        self.increase_offset([-5.0, 0.0])

    def move_right(self):
        self.increase_offset([5.0, 0.0])

    def viewport_transform(self, point, viewport):
        x_viewport = ((point[0] - self.bounds[0]) / (self.bounds[1] - self.bounds[0])) * (viewport[1] - viewport[0])
        y_viewport = (1 - (point[1] - self.bounds[2]) / (self.bounds[3] - self.bounds[2])) * (viewport[3] - viewport[2])
        return x_viewport, y_viewport
