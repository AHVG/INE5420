from model.drawable import Point, Line, Wireframe
from model.transformation import Transformation3D


class DisplayFile:

    def __init__(self):
        self.objects = [
            Point("First", [(-25, 50, 0)], "#f00"),
            Line("Second", [(-40, -32, 0), (10, 90, 0)], "#0f0"),
            Wireframe("Third", [(-15, 15, 0), (0, 20, 0), (15, 15, 0), (20, 0, 0), (15, -15, 0), (0, -20, 0), (-15, -15, 0), (-20, 0, 0)], "#00f", True),
            Line("eixo x", [(-10000, 0, 0), (10000, 0, 0)]),
            Line("eixo y", [(0, -10000, 0), (0, 10000, 0)]),
            Line("eixo Z", [(0, 0, -10000), (0, 0, 10000)]),
            Transformation3D(Wireframe("Quadrado", [(10, 10, 0), (10, 100, 0), (100, 100, 0), (100, 10, 0)], "#ff0")).rotation_relative_to_axis(20, (0, 1, 1)).apply(),
            # Bezier("Teste Curva", control_points=[(10.0, 0.0, 0), (10.0, 50.0, 0), (60.0, 50.0, 0), (60.0, 0.0, 0), (60.0, -50.0, 0), (110.0, 0.0, 0), (130.0, 80.0, 0), (160.0, 30.0, 0), (130.0, 80.0, 0), (50.0, -100.0, 0), (130.0, 80.0, 0), (-150.0, -100.0, 0)], color="#f00"),
            # BSpline("Teste Spline", control_points=[(-20, 60, 0), (-50, 110, 0), (-80, 60, 0), (-110, 140, 0), (-160, 30, 0), (-200, 80, 0)], color="#f0f"),
            # BSpline("Circulo", control_points=[(-15 + 60, 15, 0), (0 + 60, 20, 0), (15 + 60, 15, 0), (20 + 60, 0, 0), (15 + 60, -15, 0), (60, -20, 0), (-15 + 60, -15, 0), (-20 + 60, 0, 0), (-15 + 60, 15, 0), (60, 20, 0), (15 + 60, 15, 0)], color="#000")
        ]
    
    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, index):
        self.objects.pop(index)
    
    def clear_objects(self):
        self.objects.clear()

