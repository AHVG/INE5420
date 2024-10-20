from model.transformation import Transformation2D
import numpy as np

class Viewport:

    def __init__(self, window):
        self.window = window
        self.line_clipping_method = 'liang-barsky'

    def transform(self, drawable):
        drawable = drawable.copy()

        drawable = Transformation2D(drawable).rotation(\
                   np.radians(self.window.angle), self.window.get_offset()).escalation_relative_to_a_point(\
                   [1/(self.window.width/2), 1/(self.window.height/2)], self.window.get_offset()).apply()

        drawable = drawable.clip((self.window.get_bounds()[0] + 1/15, self.window.get_bounds()[2] + 1/15, self.window.get_bounds()[1] - 1/15, self.window.get_bounds()[3] - 1/15))

        if not drawable:
            return

        return drawable.transform(self.window, self)

    def set_window(self, window):
        self.window = window
    
    def set_aspect_ratio(self, aspect_ratio):
        self.width = aspect_ratio[0]
        self.height = aspect_ratio[1]
        self.bounds = (0, self.width, 0, self.height)