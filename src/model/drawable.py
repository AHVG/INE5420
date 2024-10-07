import numpy as np

from model.clipping import PointClipping
from model.clipping import LineClipping
from model.clipping import WireframeClipping

class Exportable:
    def export_to_file(self, offset):
        pass


class Importable:
    def import_from_file(self):
        pass


class Drawable(Exportable, Importable):

    def __init__(self, kind, name, points, color="#000000"):
        self.kind = kind
        self.name = name
        self.points = np.array(points, dtype=np.float64)
        self.color = color

    def copy(self, **kwargs):
        drawable_dict = self.__dict__.copy()
        drawable_dict.pop("kind")
        drawable_dict.update(kwargs)
        return self.__class__(**drawable_dict)
    
    def _convert_color_to_rgb(self):
        if len(self.color) == 7:
            return tuple(int(self.color[i + 1:i + 3], 16) / 255 for i in (0, 2, 4))
        
        return tuple(int(self.color[i + 1] + self.color[i + 1], 16) / 255 for i in (0, 1, 2))

    def export_to_file(self, offset):
        type_to_char = {
            "point": "p",
            "line": "l",
            "wireframe": "l",
            "solid wireframe": "f"
        }
        vertices = ""
        obj = ""
        mtl = ""

        color = self._convert_color_to_rgb()
        mtl += f"newmtl {self.name}\n"
        mtl += f"Kd {color[0]} {color[1]} {color[2]}\n"

        for point in self.points:
            vertices += f"v {point[0]} {point[1]} 0.0\n"

        obj += f"o {self.name}\n"
        obj += f"usemtl {self.name}\n"
        obj += f"{type_to_char[self.kind]} " + " ".join(str(i + offset) for i in range(1, len(self.points) + 1)) + "\n"

        return vertices, obj, mtl, offset + len(self.points)

    def draw(self, canvas):
        pass

    def clip(self, window_clip):
        pass


class Point(Drawable):

    def __init__(self, name, points, color="#000000"):
        assert len(points) == 1, "Número de pontos precisa ser = 1 para criar um Point"
        super().__init__("point", name, points, color)

    def draw(self, canvas):
        x, y = self.points[0]
        canvas.create_oval(x-2, y-2, x+2, y+2, fill=self.color, outline=self.color)

    def clip(self, window_clip):
        return PointClipping(window_clip).clip(self)
    
class Line(Drawable):

    def __init__(self, name, points, color="#000000", clip_method='liang-barsky'):
        assert len(points) == 2, "Número de pontos precisa ser = 2 para criar uma Line"
        super().__init__("line", name, points, color)
        self.clip_method = clip_method

    def draw(self, canvas):
        canvas.create_line(*self.points[0], *self.points[1], fill=self.color, width=2)

    def clip(self, window_clip):
        return LineClipping(window_clip).clip(self)

    def set_clip_method(self, method):
        self.clip_method = method

class Wireframe(Drawable):

    def __init__(self, name, points, color="#000000", is_solid=False):
        assert len(points) >= 3, "Número de pontos precisa ser >= 3 para criar um Wireframe"
        super().__init__("solid wireframe" if is_solid else "wireframe", name, points, color)
        self.is_solid = is_solid

    def draw(self, canvas):
        if self.is_solid:
            canvas.create_polygon(self.points.flatten().tolist(), fill=self.color, outline=self.color)            
        else:
            for i, point in enumerate(self.points):
                x1, y1 = point
                x2, y2 = self.points[(i + 1) % len(self.points)]
                canvas.create_line(x1, y1, x2, y2, fill=self.color, width=2)
    
    def clip(self, window_clip):
        return WireframeClipping(window_clip).clip(self)


class Curve2D(Drawable):

    def __init__(self, name, points, precision=10, color="#000000"):
        self.precision = precision
        super().__init__("curve2D", name, points, color)

    def calculate_bezier(self, p1, p2, p3, p4):
        points = []
        step = 10
        for t in range(0, 101, step):
            t /= 100.0
            x = p1[0] * (-t**3 + 3.0 * t**2 - 3.0 * t + 1) + p2[0] * (3.0 * t**3 - 6.0 * t**2 + 3.0 * t) + p3[0] * (-3.0 * t**3 + 3.0 * t**2) + p4[0] * t**3
            y = p1[1] * (-t**3 + 3.0 * t**2 - 3.0 * t + 1) + p2[1] * (3.0 * t**3 - 6.0 * t**2 + 3.0 * t) + p3[1] * (-3.0 * t**3 + 3.0 * t**2) + p4[1] * t**3
            points.append((x, y))

        return points
    
    def calculate_points(self):
        step = 1
        points = []
        p1, p2, p3, p4 = self.points[0], self.points[1], self.points[2], self.points[3]
        points.extend(self.calculate_bezier(p1, p2, p3, p4))

        _, prev_p2, prev_p3, prev_p4 = p1, p2, p3, p4
        for i in range(4, len(self.points), 2):
            current_p1 = prev_p4
            current_p2 = 2 * prev_p4 - prev_p3
            current_p3 = self.points[i]
            current_p4 = self.points[i + 1]
            _, prev_p2, prev_p3, prev_p4 = current_p1, current_p2, current_p3, current_p4
            points.extend(self.calculate_bezier(current_p1, current_p2, current_p3, current_p4))
        
        return points

    def draw(self, canvas):
        start = 1
        end = len(self.points)
        for i, point in enumerate(self.points[start:end]):
            i += start
            prev_point = self.points[i - 1]
            canvas.create_line(prev_point[0], prev_point[1], point[0], point[1], fill=self.color, width=2)

    def clip(self, window_clip):
        new_points = []
        points = self.calculate_points()
        clipping = LineClipping(window_clip)
        for i in range(1, len(points)):
            p1, p2 = points[i - 1], points[i]
            line = Line("test", [p1, p2])
            line = clipping.clip(line)
            if line:
                new_points.append(line.points[0])
                new_points.append(line.points[1])

        return Curve2D(self.name, new_points, precision=self.precision, color=self.color)
