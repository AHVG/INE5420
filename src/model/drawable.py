import numpy as np

from model.obj_file_handler import Exportable, Importable
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
        assert len(points) >= 3, "Número de pontos precisa ser > 3 para criar um Wireframe"
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
