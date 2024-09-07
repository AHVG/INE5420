from model.window import Window
from model.viewport import Viewport
from model.display_file import DisplayFile
from model.drawable import Point, Line, Wireframe


class Controller:

    def __init__(self):
        self.window = Window()
        self.viewport = Viewport(self.window)
        self.window.set_aspect_ratio((self.viewport.WIDTH, self.viewport.HEIGHT))
        self.display_file = DisplayFile()

    def zoom_out(self, factor):
        self.window.zoom_out(factor)

    def zoom_in(self, factor):
        self.window.zoom_in(factor)

    def move_up(self):
        self.window.move_up()

    def move_down(self):
        self.window.move_down()

    def move_left(self):
        self.window.move_left()

    def move_right(self):
        self.window.move_right()
    
    def create_point(self, name, x1, y1):
        self.display_file.add_object(Point(name, [(x1, y1)]))

    def create_line(self, name, x1, y1, x2, y2):
        self.display_file.add_object(Line(name, [(x1, y1), (x2, y2)]))

    def create_wireframe(self, name, points):
        self.display_file.add_object(Wireframe(name, points))

    def remove_objects(self, indexes):
        self.display_file.remove_object(indexes)
