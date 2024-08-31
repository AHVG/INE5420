import numpy as np


class Drawable:

    def __init__(self, kind, name, points, color="#000000"):
        self.kind = kind
        self.name = name
        self.points = np.array(points, dtype=np.float64)
        self.color = color

    def draw(self, canvas):
        pass


class Point(Drawable):

    def __init__(self, name, points):
        assert len(points) == 1, "Número de pontos precisa ser = 1 para criar um Point"
        super().__init__("point", name, points)

    def draw(self, canvas):
        x, y = self.points[0]
        canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")


class Line(Drawable):

    def __init__(self, name, points):
        assert len(points) == 2, "Número de pontos precisa ser = 2 para criar uma Line"
        super().__init__("line", name, points)

    def draw(self, canvas):
        canvas.create_line(*self.points[0], *self.points[1], fill="black", width=2)


class Wireframe(Drawable):

    def __init__(self, name, points):
        assert len(points) >= 3, "Número de pontos precisa ser > 3 para criar um Wireframe"
        super().__init__("wireframe", name, points)

    def draw(self, canvas):
        for i, point in enumerate(self.points):
            x1, y1 = point
            x2, y2 = self.points[(i + 1) % len(self.points)]
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
