import numpy as np


class Window:

    INITIAL_WINDOW_WIDTH = 200.0
    INITIAL_WINDOW_HEIGHT = 200.0
    INITIAL_WINDOW_ANGLE = 0.0
    INITIAL_OFFSET = np.array([0, 0], dtype=np.float64)

    MAX_ZOOM = 4.0
    MIN_ZOOM = 0.1

    def __init__(self):
        self.zoom_factor = 1.0
        
        self.offset = Window.INITIAL_OFFSET
        self.angle = Window.INITIAL_WINDOW_ANGLE

        self.width = Window.INITIAL_WINDOW_WIDTH
        self.height = Window.INITIAL_WINDOW_HEIGHT

    def increase_offset(self, offset):
        self.offset += np.array(offset, dtype=np.float64)

    def set_zoom(self, factor):
        if factor >= Window.MAX_ZOOM or factor <= Window.MIN_ZOOM:
            return

        self.zoom_factor = factor
        self.width = Window.INITIAL_WINDOW_WIDTH * factor
        self.height = Window.INITIAL_WINDOW_HEIGHT * factor

    def zoom_in(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor - selected_zoom_factor/100)

    def zoom_out(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor + selected_zoom_factor/100)

    def move_up(self):
        self.increase_offset([0.0, 0.01 * self.height])

    def move_down(self):
        self.increase_offset([0.0, -0.01 * self.height])

    def move_left(self):
        self.increase_offset([-0.01 * self.width, 0.0])

    def move_right(self):
        self.increase_offset([0.01 * self.width, 0.0])

    def viewport_transform(self, point, viewport):
        bounds = np.array([self.offset[0] - self.width / 2.0, self.offset[0] + self.width / 2.0, self.offset[1] - self.height / 2.0, self.offset[1] + self.height / 2.0], dtype=np.float64)
        x_viewport = ((point[0] - bounds[0]) / (bounds[1] - bounds[0])) * (viewport[1] - viewport[0])
        y_viewport = (1 - (point[1] - bounds[2]) / (bounds[3] - bounds[2])) * (viewport[3] - viewport[2])
        return x_viewport, y_viewport
