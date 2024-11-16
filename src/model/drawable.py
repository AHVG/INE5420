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
            "solid wireframe": "f",
            "curve2D": "c"
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

    def __matmul__(self, matrix):
        for i, point in enumerate(self.points):
            point_3d = np.array([point[0], point[1], point[2], 1.0], dtype=np.float64)
            transformed_point = point_3d @ matrix
            self.points[i] = np.asarray(transformed_point)[0,:-1]
        return self
    
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

    def __init__(self, name, points=None, control_points=None, section_indexes=None, precision=10, color="#000000"):
        if points is None and control_points is None:
            raise ValueError("Defina ao menos um: points ou control_points")

        self.section_indexes = [] if section_indexes is None else section_indexes
        self.precision = precision
        self.control_points = control_points if control_points is None else np.array(control_points, dtype=np.float64)
        super().__init__("curve2D", name, points if points is not None else self.calculate_points(), color)

    def calculate_points(self):
        pass

    def split_points(self):
        sections = []

        start_index = 0

        for index in self.section_indexes:
            s = self.points[start_index:index]
            if len(s):
                sections.append(s)
            start_index = index 

        if start_index < len(self.points):
            sections.append(self.points[start_index:])

        return sections

    def __matmul__(self, matrix):
        for i, point in enumerate(self.points):
            point_3d = np.array([point[0], point[1], point[2], 1.0], dtype=np.float64)
            transformed_point = point_3d @ matrix
            self.points[i] = np.asarray(transformed_point)[0,:-1]

        return self

    def draw(self, canvas):
        sections = self.split_points()
        for points in sections:
            for i, point in enumerate(points[1:]):
                i += 1
                prev_point = points[i - 1]
                canvas.create_line(prev_point[0], prev_point[1], point[0], point[1], fill=self.color, width=2)

    def clip(self, window_clip):
        new_points = []
        clipping = LineClipping(window_clip)
        self.section_indexes = []
        j = 0
        for i in range(1, len(self.points)):
            p1, p2 = self.points[i - 1], self.points[i]
            line = Line("test", [p1, p2])
            line = clipping.clip(line)
            if line is not None:
                j += 2
                new_points.append(line.points[0])
                new_points.append(line.points[1])
            else:
                self.section_indexes.append(j)

        new_control_points = []

        return self.__class__(self.name, new_points, new_control_points, self.section_indexes, precision=self.precision, color=self.color)


class Bezier(Curve2D):
    def __init__(self, name, points=None, control_points=None, section_indexes=None, precision=10, color="#000000"):
        if control_points is not None:
            assert points is not None or len(control_points) >= 4 and len(control_points) % 2 == 0, "Número de pontos precisa ser >= 4 e divisível por 2 para criar um Curve2D"

        super().__init__(name, points, control_points, section_indexes, precision, color)
    
    def calculate_bezier(self, p1, p2, p3, p4):
        points = []
        step = self.precision
        for t in range(0, 101, step):
            t /= 100.0
            x = p1[0] * (-t**3 + 3.0 * t**2 - 3.0 * t + 1) + p2[0] * (3.0 * t**3 - 6.0 * t**2 + 3.0 * t) + p3[0] * (-3.0 * t**3 + 3.0 * t**2) + p4[0] * t**3
            y = p1[1] * (-t**3 + 3.0 * t**2 - 3.0 * t + 1) + p2[1] * (3.0 * t**3 - 6.0 * t**2 + 3.0 * t) + p3[1] * (-3.0 * t**3 + 3.0 * t**2) + p4[1] * t**3
            z = 0
            points.append((x, y, z))

        return points

    def calculate_points(self):
        points = []
        p1, p2, p3, p4 = self.control_points[0], self.control_points[1], self.control_points[2], self.control_points[3]
        points.extend(self.calculate_bezier(p1, p2, p3, p4))

        _, _, prev_p3, prev_p4 = p1, p2, p3, p4
        for i in range(4, len(self.control_points), 2):
            current_p1 = prev_p4
            current_p2 = 2 * prev_p4 - prev_p3
            current_p3 = self.control_points[i]
            current_p4 = self.control_points[i + 1]
            _, _, prev_p3, prev_p4 = current_p1, current_p2, current_p3, current_p4
            points.extend(self.calculate_bezier(current_p1, current_p2, current_p3, current_p4))

        return points


class BSpline(Curve2D):
    
    def fwdDiff(self, n, x, dx, d2x, d3x, y, dy, d2y, d3y, z=0):
        points = []
        old_x, old_y, old_z = x, y, z

        for _ in range(n):
            x += dx
            dx += d2x
            d2x += d3x

            y += dy
            dy += d2y
            d2y += d3y

            points.append((old_x, old_y, old_z))

            old_x, old_y, old_z = x, y, z
        
        points.append((old_x, old_y, old_z))
        return points

    def calculate_points(self):
        points = []
        delta = 1 / self.precision
        n = self.precision

        M_bspline = (1 / 6) * np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ])

        for i in range(len(self.control_points) - 3):
            p0, p1, p2, p3 = self.control_points[i:i + 4]

            Gx = np.array([p0[0], p1[0], p2[0], p3[0]])
            Gy = np.array([p0[1], p1[1], p2[1], p3[1]])

            Cx = M_bspline @ Gx
            Cy = M_bspline @ Gy

            E = np.array([
                [0, 0, 0, 1],
                [delta**3, delta**2, delta, 0],
                [6 * delta**3, 2 * delta**2, 0, 0],
                [6 * delta**3, 0, 0, 0]
            ])

            fx, dfx, d2fx, d3fx = E @ Cx
            fy, dfy, d2fy, d3fy = E @ Cy

            points.extend(self.fwdDiff(n, fx, dfx, d2fx, d3fx, fy, dfy, d2fy, d3fy))
            
        return points
