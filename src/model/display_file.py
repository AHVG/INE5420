from model.drawable import Point, Line, Wireframe, Bezier, BSpline, Point3D


class DisplayFile:

    def __init__(self):
        self.objects = [
            Point3D("First", [(-25, 50, 0)], "#f00"),
        ]
    
    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, index):
        self.objects.pop(index)
    
    def clear_objects(self):
        self.objects.clear()

