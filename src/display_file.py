from drawable import Point, Line, Wireframe
from transformation import Transformation2D


class DisplayFile:

    def __init__(self, canvas, window, viewport):
        self.canvas = canvas
        self.window = window
        self.viewport = viewport
        self.objects = [Point("First", [(-25, 50)]), Line("Second", [(-40, -32), (10, 90)]), Wireframe("Third", [(-15, 15), (0, 20), (15, 15), (20, 0), (15, -15), (0, -20), (-15, -15), (-20, 0)])]
        self.draw()
    
    def add_object(self, object):
        self.objects.append(object)

    def draw(self):
        self.canvas.delete("all")
        for o in self.objects:
            o.draw(self.canvas, self.window, self.viewport)
