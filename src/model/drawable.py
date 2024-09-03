import numpy as np


class Drawable:

    def __init__(self, kind, name, points):
        self.kind = kind
        self.name = name
        self.points = np.array(points, dtype=np.float64)

    def draw(self, canvas, viewport):
        pass


class Point(Drawable):

    def __init__(self, name, points):
        assert len(points) == 1, "Número de pontos precisa ser = 1 para criar um Point"
        super().__init__("point", name, points)

    def draw(self, canvas, viewport):
        x, y = viewport.transform(self.points[0])
        canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")


class Line(Drawable):

    def __init__(self, name, points):
        assert len(points) == 2, "Número de pontos precisa ser = 2 para criar uma Line"
        super().__init__("line", name, points)

    def draw(self, canvas, viewport):
        points = [viewport.transform(point) for point in self.points]
        canvas.create_line(*points, fill="black", width=2)


class Wireframe(Drawable):

    def __init__(self, name, points):
        assert len(points) >= 3, "Número de pontos precisa ser > 3 para criar um Wireframe"
        super().__init__("wireframe", name, points)

    def draw(self, canvas, viewport):
        for i, point in enumerate(self.points):
            x1, y1 = viewport.transform(point)
            x2, y2 = viewport.transform(self.points[(i + 1) % len(self.points)])
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
