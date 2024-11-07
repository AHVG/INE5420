from abc import ABC, abstractmethod

from typing import Tuple
import numpy as np


class Clipping(ABC):

    def __init__(self, clip_window: Tuple[float, float, float, float]):
        self.xmin, self.ymin, self.xmax, self.ymax = clip_window

    @abstractmethod
    def clip(self, drawable):
        pass


class PointClipping(Clipping):

    def clip(self, point):
        x, y, z = point.points[0]
        if self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax:
            return point
        return None


class LineClipping(Clipping):

    def __init__(self, clip_window: Tuple[float, float, float, float]):
        super().__init__(clip_window)
    
    def clip(self, line):
        if line.clip_method == 'liang-barsky':
            return self.liang_barsky(line)
        else:
            return self.nicholl_lee_nicholl(line)

    def liang_barsky(self, line):
        from model.drawable import Line
        x0, y0 = line.points[0]
        x1, y1 = line.points[1]
        dx = x1 - x0
        dy = y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - self.xmin, self.xmax - x0, y0 - self.ymin, self.ymax - y0]
        u1, u2 = 0.0, 1.0

        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
            else:
                u = q[i] / p[i]
                if p[i] < 0:
                    if u > u1:
                        u1 = u
                else:
                    if u < u2:
                        u2 = u
        if u1 > u2:
            return None

        clipped_start = [x0 + u1 * dx, y0 + u1 * dy]
        clipped_end = [x0 + u2 * dx, y0 + u2 * dy]
        return Line(name=line.name + "_clipped", points=[clipped_start, clipped_end], color=line.color)

    def nicholl_lee_nicholl(self, line):
        from model.drawable import Line
        x0, y0 = line.points[0]
        x1, y1 = line.points[1]

        if self._point_in_window(x0, y0) and self._point_in_window(x1, y1):
            return line

        if (x0 < self.xmin and x1 < self.xmin) or (x0 > self.xmax and x1 > self.xmax) or \
           (y0 < self.ymin and y1 < self.ymin) or (y0 > self.ymax and y1 > self.ymax):
            return None

        def clip_x(y0, y1, x_boundary):
            if x1 - x0 == 0:
                return y0
            slope = (y1 - y0) / (x1 - x0)
            return y0 + slope * (x_boundary - x0)

        def clip_y(x0, x1, y_boundary):
            if y1 - y0 == 0:
                return x0
            slope = (x1 - x0) / (y1 - y0)
            return x0 + slope * (y_boundary - y0)

        if x0 < self.xmin:
            y0 = clip_x(y0, y1, self.xmin)
            x0 = self.xmin
        elif x0 > self.xmax:
            y0 = clip_x(y0, y1, self.xmax)
            x0 = self.xmax

        if x1 < self.xmin:
            y1 = clip_x(y0, y1, self.xmin)
            x1 = self.xmin
        elif x1 > self.xmax:
            y1 = clip_x(y0, y1, self.xmax)
            x1 = self.xmax

        if y0 < self.ymin:
            x0 = clip_y(x0, x1, self.ymin)
            y0 = self.ymin
        elif y0 > self.ymax:
            x0 = clip_y(x0, x1, self.ymax)
            y0 = self.ymax

        if y1 < self.ymin:
            x1 = clip_y(x0, x1, self.ymin)
            y1 = self.ymin
        elif y1 > self.ymax:
            x1 = clip_y(x0, x1, self.ymax)
            y1 = self.ymax

        return Line(name=line.name + "_clipped", points=[[x0, y0], [x1, y1]], color=line.color)

    def _point_in_window(self, x, y):
        return self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax


class WireframeClipping(Clipping):
    def clip(self, wireframe):
        from model.drawable import Wireframe
        output_polygon = wireframe.points

        output_polygon = self._clip_polygon(output_polygon, self.xmin, self._clip_left)
        output_polygon = self._clip_polygon(output_polygon, self.xmax, self._clip_right)
        output_polygon = self._clip_polygon(output_polygon, self.ymin, self._clip_bottom)
        output_polygon = self._clip_polygon(output_polygon, self.ymax, self._clip_top)

        if output_polygon.size > 0:
            return Wireframe(name=wireframe.name + "_clipped", points=output_polygon, color=wireframe.color, is_solid=wireframe.is_solid)
        return None

    def _clip_polygon(self, vertices: np.ndarray, boundary: float, clip_func) -> np.ndarray:
        clipped_vertices = []
        if len(vertices) == 0:
            return np.array(clipped_vertices)

        prev_vertex = vertices[-1]
        for curr_vertex in vertices:
            if clip_func(curr_vertex, boundary):
                if not clip_func(prev_vertex, boundary):
                    clipped_vertices.append(self._intersection(prev_vertex, curr_vertex, boundary, clip_func))
                clipped_vertices.append(curr_vertex)
            elif clip_func(prev_vertex, boundary):
                clipped_vertices.append(self._intersection(prev_vertex, curr_vertex, boundary, clip_func))
            prev_vertex = curr_vertex

        return np.array(clipped_vertices)

    def _intersection(self, p1: np.ndarray, p2: np.ndarray, boundary: float, clip_func) -> np.ndarray:
        if clip_func == self._clip_left or clip_func == self._clip_right:
            dy = p2[1] - p1[1]
            dx = p2[0] - p1[0]
            if dx == 0:
                return np.array([p1[0], p1[1]])
            slope = dy / dx
            y = p1[1] + slope * (boundary - p1[0])
            return np.array([boundary, y])
        elif clip_func == self._clip_bottom or clip_func == self._clip_top:
            dy = p2[1] - p1[1]
            dx = p2[0] - p1[0]
            if dy == 0:
                return np.array([p1[0], p1[1]])
            slope = dx / dy
            x = p1[0] + slope * (boundary - p1[1])
            return np.array([x, boundary])

    def _clip_left(self, vertex: np.ndarray, boundary: float) -> bool:
        return vertex[0] >= boundary

    def _clip_right(self, vertex: np.ndarray, boundary: float) -> bool:
        return vertex[0] <= boundary

    def _clip_bottom(self, vertex: np.ndarray, boundary: float) -> bool:
        return vertex[1] >= boundary

    def _clip_top(self, vertex: np.ndarray, boundary: float) -> bool:
        return vertex[1] <= boundary