from model.drawable import Point, Line, Wireframe, Curve2D


class DisplayFile:

    def __init__(self):
        self.objects = [
            Point("First", [(-25, 50)], "#f00"),
            Line("Second", [(-40, -32), (10, 90)], "#0f0"),
            Wireframe("Third", [(-15, 15), (0, 20), (15, 15), (20, 0), (15, -15), (0, -20), (-15, -15), (-20, 0)], "#00f", True),
            Line("eixo x", [(-10000, 0), (10000, 0)]),
            Line("eixo y", [(0, -10000), (0, 10000)]),
            Wireframe("Quadrado", [(10, 10), (10, 100), (100, 100), (100, 10)], "#ff0"),
            Curve2D("Teste Curva", [(10.0,0.0), (10.0,50.0), (60.0,50.0), (60.0,0.0), (60.0,-50.0), (110.0,0.0), (130.0,80.0), (160.0,30.0), (130.0,80.0), (50.0,-100.0), (130.0,80.0), (-150.0,-100.0)], "#f00")
        ]
    
    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, index):
        self.objects.pop(index)
    
    def clear_objects(self):
        self.objects.clear()

