import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Line:
    start: Point
    end: Point

@dataclass
class Polygon:
    vertices: List[Point]

class Clipping:
    def __init__(self, clip_window: Tuple[float, float, float, float], method: str = 'liang-barsky'):
        """
        Initialize the Clipping class.

        :param clip_window: A tuple (xmin, ymin, xmax, ymax) defining the clipping window.
        :param method: Clipping method for lines ('liang-barsky' or 'nicholl-lee-nicholl').
        """
        self.xmin, self.ymin, self.xmax, self.ymax = clip_window
        self.method = method.lower()
        if self.method not in ['liang-barsky', 'nicholl-lee-nicholl']:
            raise ValueError("Method must be 'liang-barsky' or 'nicholl-lee-nicholl'.")

    def point_clipping(self, point: Point) -> bool:
        """
        Determine if a point is inside the clipping window.

        :param point: Point to be clipped.
        :return: True if inside, False otherwise.
        """
        inside = self.xmin <= point.x <= self.xmax and self.ymin <= point.y <= self.ymax
        print(f"Point {point} is {'inside' if inside else 'outside'} the clipping window.")
        return inside

    def line_clipping(self, line: Line) -> Optional[Line]:
        """
        Clip a line using the selected clipping algorithm.

        :param line: Line to be clipped.
        :return: Clipped Line if visible, None otherwise.
        """
        if self.method == 'liang-barsky':
            return self._liang_barsky(line)
        elif self.method == 'nicholl-lee-nicholl':
            return self._nicholl_lee_nicholl(line)
        else:
            raise ValueError("Unsupported clipping method.")

    def _liang_barsky(self, line: Line) -> Optional[Line]:
        """
        Liang-Barsky line clipping algorithm.

        :param line: Line to be clipped.
        :return: Clipped Line if visible, None otherwise.
        """
        p = [- (line.end.x - line.start.x), (line.end.x - line.start.x),
             - (line.end.y - line.start.y), (line.end.y - line.start.y)]
        q = [line.start.x - self.xmin, self.xmax - line.start.x,
             line.start.y - self.ymin, self.ymax - line.start.y]
        u1, u2 = 0.0, 1.0

        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    print("Line is parallel and outside the clipping window.")
                    return None  # Parallel and outside
                else:
                    print("Line is parallel and inside/on the clipping boundary.")
                    continue  # Parallel and inside or on boundary
            u = q[i] / p[i]
            if p[i] < 0:
                if u > u1:
                    u1 = u
                    print(f"Updating u1 to {u1}")
            else:
                if u < u2:
                    u2 = u
                    print(f"Updating u2 to {u2}")
            if u1 > u2:
                print("No visible segment after clipping.")
                return None  # No visible segment

        clipped_start = Point(line.start.x + u1 * (line.end.x - line.start.x),
                             line.start.y + u1 * (line.end.y - line.start.y))
        clipped_end = Point(line.start.x + u2 * (line.end.x - line.start.x),
                           line.start.y + u2 * (line.end.y - line.start.y))
        print(f"Clipped Line: {clipped_start} to {clipped_end}")
        return Line(clipped_start, clipped_end)

    def _nicholl_lee_nicholl(self, line: Line) -> Optional[Line]:
        """
        Nicholl-Lee-Nicholl line clipping algorithm.

        :param line: Line to be clipped.
        :return: Clipped Line if visible, None otherwise.
        """
        INSIDE = 0  # 0000
        LEFT = 1    # 0001
        RIGHT = 2   # 0010
        BOTTOM = 4  # 0100
        TOP = 8     # 1000

        def compute_out_code(p: Point) -> int:
            code = INSIDE
            if p.x < self.xmin:
                code |= LEFT
            elif p.x > self.xmax:
                code |= RIGHT
            if p.y < self.ymin:
                code |= BOTTOM
            elif p.y > self.ymax:
                code |= TOP
            return code

        p0, p1 = line.start, line.end
        out_code0 = compute_out_code(p0)
        out_code1 = compute_out_code(p1)

        accept = False

        while True:
            print(f"Outcodes: P0={out_code0}, P1={out_code1}")
            if not (out_code0 | out_code1):
                accept = True
                break
            elif (out_code0 & out_code1):
                break
            else:
                if out_code0 != 0:
                    out_code_out = out_code0
                else:
                    out_code_out = out_code1

                if out_code_out & TOP:
                    if (p1.y - p0.y) == 0:
                        print("Line is parallel to top edge; no intersection.")
                        return None
                    x = p0.x + (p1.x - p0.x) * (self.ymax - p0.y) / (p1.y - p0.y)
                    y = self.ymax
                elif out_code_out & BOTTOM:
                    if (p1.y - p0.y) == 0:
                        print("Line is parallel to bottom edge; no intersection.")
                        return None
                    x = p0.x + (p1.x - p0.x) * (self.ymin - p0.y) / (p1.y - p0.y)
                    y = self.ymin
                elif out_code_out & RIGHT:
                    if (p1.x - p0.x) == 0:
                        print("Line is parallel to right edge; no intersection.")
                        return None
                    y = p0.y + (p1.y - p0.y) * (self.xmax - p0.x) / (p1.x - p0.x)
                    x = self.xmax
                elif out_code_out & LEFT:
                    if (p1.x - p0.x) == 0:
                        print("Line is parallel to left edge; no intersection.")
                        return None
                    y = p0.y + (p1.y - p0.y) * (self.xmin - p0.x) / (p1.x - p0.x)
                    x = self.xmin

                print(f"Intersection at ({x}, {y})")

                if out_code_out == out_code0:
                    p0 = Point(x, y)
                    out_code0 = compute_out_code(p0)
                else:
                    p1 = Point(x, y)
                    out_code1 = compute_out_code(p1)

        if accept:
            print(f"Clipped Line: {p0} to {p1}")
            return Line(p0, p1)
        else:
            print("Line is completely outside the clipping window.")
            return None

    def polygon_clipping(self, polygon: Polygon) -> Optional[Polygon]:
        """
        Clip a polygon using the Sutherland-Hodgman algorithm.

        :param polygon: Polygon to be clipped.
        :return: Clipped Polygon if visible, None otherwise.
        """
        def clip_polygon_against_edge(subject_polygon: List[Point], edge: str) -> List[Point]:
            clipped_polygon = []
            len_vertices = len(subject_polygon)

            for i in range(len_vertices):
                current = subject_polygon[i]
                prev = subject_polygon[i - 1]

                if edge == 'left':
                    inside_current = current.x >= self.xmin
                    inside_prev = prev.x >= self.xmin
                elif edge == 'right':
                    inside_current = current.x <= self.xmax
                    inside_prev = prev.x <= self.xmax
                elif edge == 'bottom':
                    inside_current = current.y >= self.ymin
                    inside_prev = prev.y >= self.ymin
                elif edge == 'top':
                    inside_current = current.y <= self.ymax
                    inside_prev = prev.y <= self.ymax
                else:
                    raise ValueError("Invalid clipping edge.")

                # Determine if an intersection should be calculated
                if inside_current:
                    if not inside_prev:
                        intersection = self._compute_intersection(prev, current, edge)
                        if intersection:
                            clipped_polygon.append(intersection)
                    clipped_polygon.append(current)
                elif inside_prev:
                    intersection = self._compute_intersection(prev, current, edge)
                    if intersection:
                        clipped_polygon.append(intersection)
            return clipped_polygon

        clipped_vertices = polygon.vertices.copy()

        for edge in ['left', 'right', 'bottom', 'top']:
            clipped_vertices = clip_polygon_against_edge(clipped_vertices, edge)
            print(f"After clipping against {edge} edge: {[ (p.x, p.y) for p in clipped_vertices ]}")
            if not clipped_vertices:
                print("Polygon is completely outside the clipping window.")
                return None

        # Remove consecutive duplicate points if any
        final_vertices = []
        for pt in clipped_vertices:
            if not final_vertices or (pt.x != final_vertices[-1].x or pt.y != final_vertices[-1].y):
                final_vertices.append(pt)
        # Ensure the polygon is closed (first point == last point)
        if final_vertices and (final_vertices[0].x != final_vertices[-1].x or final_vertices[0].y != final_vertices[-1].y):
            final_vertices.append(final_vertices[0])

        # Remove the duplicated closing point for consistent representation
        if len(final_vertices) > 1 and final_vertices[0] == final_vertices[-1]:
            final_vertices.pop()

        clipped_polygon = Polygon(final_vertices)
        print(f"Clipped Polygon vertices: {[ (p.x, p.y) for p in clipped_polygon.vertices ]}")
        return clipped_polygon if clipped_polygon.vertices else None

    def _compute_intersection(self, p1: Point, p2: Point, edge: str) -> Optional[Point]:
        """
        Compute the intersection point of a line segment with a clipping boundary.

        :param p1: Start point of the line segment.
        :param p2: End point of the line segment.
        :param edge: Clipping edge ('left', 'right', 'bottom', 'top').
        :return: Intersection Point or None if parallel or coincident.
        """
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        if edge == 'left':
            x = self.xmin
            if dx == 0:
                print("Parallel to left edge; no intersection.")
                return None
            y = p1.y + dy * (self.xmin - p1.x) / dx
        elif edge == 'right':
            x = self.xmax
            if dx == 0:
                print("Parallel to right edge; no intersection.")
                return None
            y = p1.y + dy * (self.xmax - p1.x) / dx
        elif edge == 'bottom':
            y = self.ymin
            if dy == 0:
                print("Parallel to bottom edge; no intersection.")
                return None
            x = p1.x + dx * (self.ymin - p1.y) / dy
        elif edge == 'top':
            y = self.ymax
            if dy == 0:
                print("Parallel to top edge; no intersection.")
                return None
            x = p1.x + dx * (self.ymax - p1.y) / dy
        else:
            raise ValueError("Invalid clipping edge.")

        # Check if the intersection point is within the clipping boundary
        if (self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax):
            print(f"Intersection with {edge} edge at ({x}, {y})")
            return Point(x, y)
        else:
            print(f"Intersection with {edge} edge at ({x}, {y}) is outside the clipping window.")
            return None


# Define clipping window
clip_window = (100, 100, 300, 300)  # xmin, ymin, xmax, ymax

# Initialize Clipping class with Liang-Barsky method
clipping = Clipping(clip_window, method='liang-barsky')

# Point Clipping
point = Point(150, 150)
print("Point Clipping:", clipping.point_clipping(point))  # Should be True

point_out = Point(50, 50)
print("Point Clipping:", clipping.point_clipping(point_out))  # Should be False

# Line Clipping
line = Line(Point(50, 150), Point(350, 150))
clipped_line = clipping.line_clipping(line)
if clipped_line:
    print(f"Clipped Line: ({clipped_line.start.x}, {clipped_line.start.y}) to "
            f"({clipped_line.end.x}, {clipped_line.end.y})")
else:
    print("Line is outside the clipping window.")

# Line parallel to clipping boundary (horizontal line with 'top' edge)
parallel_line = Line(Point(150, 300), Point(250, 300))
clipped_parallel_line = clipping.line_clipping(parallel_line)
if clipped_parallel_line:
    print(f"Clipped Parallel Line: ({clipped_parallel_line.start.x}, {clipped_parallel_line.start.y}) to "
            f"({clipped_parallel_line.end.x}, {clipped_parallel_line.end.y})")
else:
    print("Parallel Line is outside the clipping window or coincides with the boundary.")

# Polygon Clipping
polygon = Polygon([
    Point(50, 50),
    Point(350, 50),
    Point(350, 350),
    Point(50, 350)
])
clipped_polygon = clipping.polygon_clipping(polygon)
if clipped_polygon:
    print("Clipped Polygon vertices:")
    for vertex in clipped_polygon.vertices:
        print(f"({vertex.x}, {vertex.y})")
else:
    print("Polygon is outside the clipping window.")

# Polygon with edges parallel to clipping boundaries
polygon_parallel = Polygon([
    Point(100, 100),
    Point(300, 100),
    Point(300, 300),
    Point(100, 300)
])
clipped_polygon_parallel = clipping.polygon_clipping(polygon_parallel)
if clipped_polygon_parallel:
    print("Clipped Polygon with Parallel Edges vertices:")
    for vertex in clipped_polygon_parallel.vertices:
        print(f"({vertex.x}, {vertex.y})")
else:
    print("Polygon with Parallel Edges is outside the clipping window.")

"""
Point Point(x=150, y=150) is inside the clipping window.
Point Clipping: True
Point Point(x=50, y=50) is outside the clipping window.
Point Clipping: False
Updating u1 to 0.16666666666666666
Updating u2 to 0.8333333333333334
Line is parallel and inside/on the clipping boundary.
Line is parallel and inside/on the clipping boundary.

Clipped Line: Point(x=100.0, y=150.0) to Point(x=300.0, y=150.0)
Clipped Line: (100.0, 150.0) to (300.0, 150.0)
Clipped Line: Point(x=150.0, y=300.0) to Point(x=250.0, y=300.0)
Clipped Parallel Line: (150.0, 300.0) to (250.0, 300.0)
Intersection with left edge at (100.0, 50.0)
Intersection with left edge at (100.0, 350.0)
After clipping against left edge: [(100.0, 50.0), (350, 50), (350, 350), (100.0, 350.0)]
Intersection with right edge at (300.0, 50.0)
Intersection with right edge at (300.0, 350.0)
After clipping against right edge: [(100.0, 50.0), (300.0, 50.0), (300.0, 350.0)]
Intersection with bottom edge at (133.33333333333334, 100)
Intersection with bottom edge at (300.0, 100)
After clipping against bottom edge: [(133.33333333333334, 100), (300.0, 100.0), (300.0, 350.0)]
Intersection with top edge at (266.6666666666667, 300)
Intersection with top edge at (300.0, 300)
After clipping against top edge: [(266.6666666666667, 300), (133.33333333333334, 100), (300.0, 100.0), (300.0, 300.0)]
Clipped Polygon vertices: [(266.6666666666667, 300), (133.33333333333334, 100), (300.0, 100.0), (300.0, 300.0)]
After clipping against left edge: [(100.0, 100.0), (300, 100), (300, 300), (100.0, 300.0)]
After clipping against right edge: [(100.0, 100.0), (300.0, 100.0), (300.0, 300.0), (100.0, 300.0)]
After clipping against bottom edge: [(100.0, 100.0), (300.0, 100.0), (300.0, 300.0), (100.0, 300.0)]
After clipping against top edge: [(100.0, 300.0), (100.0, 100.0), (300.0, 100.0), (300.0, 300.0)]
Clipped Polygon vertices: [(100.0, 300.0), (100.0, 100.0), (300.0, 100.0), (300.0, 300.0)]

"""