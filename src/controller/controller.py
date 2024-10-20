import numpy as np

from model.window import Window
from model.viewport import Viewport
from model.display_file import DisplayFile
from model.drawable import Point, Line, Wireframe, Bezier, BSpline
from model.transformation import Transformation2D
from model.obj_file_handler import ObjFileHandler

class Controller:

    def __init__(self):
        self.window = Window()
        self.viewport = Viewport(self.window)
        self.display_file = DisplayFile()
        self.transformation = None

    def rotate_left(self, angle):
        self.window.increase_angle(-angle)
    
    def rotate_right(self, angle):
        self.window.increase_angle(angle)

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
    
    def create_point(self, name, x1, y1, color):
        self.display_file.add_object(Point(name, [(x1, y1)], color))

    def create_line(self, name, x1, y1, x2, y2, color):
        self.display_file.add_object(Line(name, [(x1, y1), (x2, y2)], color))

    def create_wireframe(self, name, points, color, is_solid):
        self.display_file.add_object(Wireframe(name, points, color, is_solid))

    def create_bezier(self, name, points, color):
        self.display_file.add_object(Bezier(name, control_points=points, color=color))
    
    def create_bspline(self, name, points, color):
        self.display_file.add_object(BSpline(name, control_points=points, color=color))

    def remove_objects(self, indexes):
        self.display_file.remove_object(indexes)

    def set_aspect_ratio(self, aspect_ratio):
        self.viewport.set_aspect_ratio(aspect_ratio)
        self.window.set_aspect_ratio(aspect_ratio)

    def setup_transformation(self, index):
        drawable = self.display_file.objects[index]
        self.transformation = Transformation2D(drawable)

    def rotate_relative_to_origin(self, angle):
        self.transformation.rotation(np.radians(angle), (0, 0))

    def rotate_relative_to_center_of_object(self, angle):
        self.transformation.rotation(np.radians(angle))

    def rotate_relative_to_point(self, angle, point):
        self.transformation.rotation(np.radians(angle), point)

    def translate(self, displacement):
        self.transformation.translation(displacement)

    def scale(self, factor):
        self.transformation.escalation(factor)

    def apply(self):
        self.transformation.apply()
        self.transformation = None
    
    def export_world(self, file_path):
        ObjFileHandler.export_file(self.display_file.objects, file_path)
    
    def import_world(self, file_path):
        objects = ObjFileHandler.import_file(file_path)
        self.display_file.clear_objects()
        for o in objects:
            self.display_file.add_object(o)
        self.window.reset()
        self.window.set_aspect_ratio((self.viewport.width, self.viewport.height))

    def set_line_clipping_method(self, method):
        for object_ in self.display_file.objects:
            if isinstance(object_, Line):
                object_.set_clip_method(method)
