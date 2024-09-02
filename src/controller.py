from  window import Window
from display_file import DisplayFile
from constants import INITIAL_VIEWPORT
from drawable import Point, Line, Wireframe


class Controller:

    def __init__(self, view=None):
        self.view = view

        self.viewport = INITIAL_VIEWPORT
        self.window = Window()
        self.display_file = DisplayFile(self.window, self.viewport)

    def zoom_out(self, factor):
        self.window.zoom_out(factor)
        self.display_file.draw()

    def zoom_in(self, factor):
        self.window.zoom_in(factor)
        self.display_file.draw()

    def move_up(self):
        self.window.move_up()
        self.display_file.draw()

    def move_down(self):
        self.window.move_down()
        self.display_file.draw()

    def move_left(self):
        self.window.move_left()
        self.display_file.draw()

    def move_right(self):
        self.window.move_right()
        self.display_file.draw()
    
    def create_point(self, name, x1, y1):
        self.display_file.add_object(Point(name, [(x1, y1)]))

    def create_line(self, name, x1, y1, x2, y2):
        self.display_file.add_object(Line(name, [(x1, y1), (x2, y2)]))

    def create_wireframe(self, name, points):
        self.display_file.add_object(Wireframe(name, points))

    def remove_object(self, index):
        pass