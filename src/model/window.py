import numpy as np


class Window:

    INITIAL_ANGLE = 0.0
    INITIAL_OFFSET = np.array([0, 0], dtype=np.float64)
    INITIAL_ZOOM_FACTOR = 1.0

    MAX_ZOOM = 4.0
    MIN_ZOOM = 0.1

    def __init__(self):
        self.initial_width = 200.0
        self.initial_height = 200.0
        self.width = self.initial_width
        self.height = self.initial_height

        self.zoom_factor = Window.INITIAL_ZOOM_FACTOR
        self.offset = Window.INITIAL_OFFSET
        self.angle = Window.INITIAL_ANGLE
    
    def get_bounds(self):
        return np.array([self.offset[0] - self.width / 2.0, self.offset[0] + self.width / 2.0, self.offset[1] - self.height / 2.0, self.offset[1] + self.height / 2.0], dtype=np.float64)

    def increase_offset(self, offset):
        self.offset += np.array(offset, dtype=np.float64)

    def set_zoom(self, factor):
        if factor >= Window.MAX_ZOOM:
            factor = Window.MAX_ZOOM

        if factor <= Window.MIN_ZOOM:
            factor = Window.MIN_ZOOM

        self.zoom_factor = factor
        self.width = self.initial_width* factor
        self.height = self.initial_height * factor

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

    def set_aspect_ratio(self, aspect_ratio):
        self.initial_width = aspect_ratio[0]
        self.initial_height = aspect_ratio[1]
