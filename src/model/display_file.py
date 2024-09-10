from model.drawable import Point, Line, Wireframe


class DisplayFile:

    def __init__(self):
        self.objects = [
            Point("First", [(-25, 50)], "#f00"),
            Line("Second", [(-40, -32), (10, 90)], "#0f0"),
            Wireframe("Third", [(-15, 15), (0, 20), (15, 15), (20, 0), (15, -15), (0, -20), (-15, -15), (-20, 0)], "#00f"),
            Line("eixo x", [(-10000, 0), (10000, 0)]),
            Line("eixo y", [(0, -10000), (0, 10000)]),
            Wireframe("Quadrado", [(10, 10), (10, 100), (100, 100), (100, 10)], "#ff0")
        ]
    
    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, index):
        self.objects.pop(index)
