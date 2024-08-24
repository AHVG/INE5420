import copy


def viewport_transform(point, window, viewport):
    x_viewport = ((point[0] - window[0]) / (window[1] - window[0])) * (viewport[1] - viewport[0])
    y_viewport = (1 - (point[1] - window[2]) / (window[3] - window[2])) * (viewport[3] - viewport[2])
    return x_viewport, y_viewport


class Drawable:

    def __init__(self, kind: str, name: str, points: list[tuple[float, float]]):
        self.kind = kind
        self.name = name
        self.points = copy.deepcopy(points)

    def draw(self, canvas, window, viewport):
        pass


class Point(Drawable):
    
    def __init__(self, name, points):
        assert len(points) == 1, "Número de pontos precisa ser = 1 para criar um Point"
        super().__init__("point", name, points)

    def draw(self, canvas, window, viewport):
        x, y = viewport_transform(self.points[0], window, viewport)  # É um ponto, então tem que ter um ponto apenas
        canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")


class Line(Drawable):

    def __init__(self, name, points):
        assert len(points) == 2, "Número de pontos precisa ser = 2 para criar uma Line"
        super().__init__("line", name, points)
    
    def draw(self, canvas, window, viewport):
        points = [viewport_transform(point, window, viewport) for point in self.points]
        canvas.create_line(*points, fill="black", width=2)


class Wireframe(Drawable):
    
    def __init__(self, name, points):
        assert len(points) > 3, "Número de pontos precisa ser > 3 para criar um Wireframe"
        super().__init__("wireframe", name, points)

    def draw(self, canvas, window, viewport):
        for i, point in enumerate(self.points):
            x1, y1 = viewport_transform(point, window, viewport)
            x2, y2 = viewport_transform(self.points[(i + 1) % len(self.points)], window, viewport)
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
