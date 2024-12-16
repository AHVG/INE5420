import math

from object3d import *


class Transformation:
    """Classe para representar uma transformação."""
    def __init__(self, t_type, params):
        self.type = t_type  # 'translate', 'rotate', 'scale'
        self.params = params  # Parâmetros da transformação

    def __str__(self):
        if self.type == 'translate':
            dx, dy, dz = self.params
            return f"Translação: dx={dx}, dy={dy}, dz={dz}"
        elif self.type == 'rotate':
            angle, axis = self.params
            return f"Rotação: ângulo={angle}, eixo={axis}"
        elif self.type == 'scale':
            sx, sy, sz = self.params
            return f"Escala: sx={sx}, sy={sy}, sz={sz}"
        else:
            return "Transformação desconhecida"


def translate_object(obj, dx, dy, dz):
    """Translada um objeto modificando suas coordenadas diretamente."""
    if isinstance(obj, Point3D):
        obj.x += dx
        obj.y += dy
        obj.z += dz
    elif isinstance(obj, Line3D):
        translate_object(obj.start, dx, dy, dz)
        translate_object(obj.end, dx, dy, dz)
    elif isinstance(obj, Polygon3D):
        for vertex in obj.vertices:
            translate_object(vertex, dx, dy, dz)
    elif isinstance(obj, BezierCurve3D) or isinstance(obj, BSplineCurve3D):
        for point in obj.control_points:
            translate_object(point, dx, dy, dz)
    elif isinstance(obj, Cone3D):
        translate_object(obj.apex, dx, dy, dz)
        translate_object(obj.base_center, dx, dy, dz)
        for vertex in obj.base_vertices:
            translate_object(vertex, dx, dy, dz)
    elif isinstance(obj, Cube3D):
        for vertex in obj.vertices:
            translate_object(vertex, dx, dy, dz)
    elif isinstance(obj, BezierSurface3D):
        for row in obj.control_points:
            for point in row:
                translate_object(point, dx, dy, dz)
    else:
        pass  # Para outros tipos de objetos

def scale_object(obj, sx, sy, sz):
    """Escalona um objeto modificando suas coordenadas diretamente."""
    if isinstance(obj, Point3D):
        obj.x *= sx
        obj.y *= sy
        obj.z *= sz
    elif isinstance(obj, Line3D):
        scale_object(obj.start, sx, sy, sz)
        scale_object(obj.end, sx, sy, sz)
    elif isinstance(obj, Polygon3D):
        for vertex in obj.vertices:
            scale_object(vertex, sx, sy, sz)
    elif isinstance(obj, BezierCurve3D) or isinstance(obj, BSplineCurve3D):
        for point in obj.control_points:
            scale_object(point, sx, sy, sz)
    elif isinstance(obj, Cone3D):
        scale_object(obj.apex, sx, sy, sz)
        scale_object(obj.base_center, sx, sy, sz)
        for vertex in obj.base_vertices:
            scale_object(vertex, sx, sy, sz)
        obj.height *= sy  # Ajusta a altura
        obj.radius *= sx  # Ajusta o raio (assumindo escalonamento uniforme em x e z)
    elif isinstance(obj, Cube3D):
        for vertex in obj.vertices:
            scale_object(vertex, sx, sy, sz)
        obj.size *= max(sx, sy, sz)  # Ajusta o tamanho (assumindo escalonamento uniforme)
    elif isinstance(obj, BezierSurface3D):
        for row in obj.control_points:
            for point in row:
                scale_object(point, sx, sy, sz)
    else:
        pass  # Para outros tipos de objetos

def rotate_object(obj, angle, axis):
    """Rotaciona um objeto modificando suas coordenadas diretamente."""
    angle_rad = math.radians(angle)
    if axis.lower() == 'x':
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rotation_func = lambda x, y, z: (x, y * cos_a - z * sin_a, y * sin_a + z * cos_a)
    elif axis.lower() == 'y':
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rotation_func = lambda x, y, z: (x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a)
    elif axis.lower() == 'z':
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rotation_func = lambda x, y, z: (x * cos_a - y * sin_a, x * sin_a + y * cos_a, z)
    else:
        raise ValueError("Axis must be 'x', 'y', or 'z'")

    def rotate_point(p):
        x, y, z = p.x, p.y, p.z
        p.x, p.y, p.z = rotation_func(x, y, z)

    if isinstance(obj, Point3D):
        rotate_point(obj)
    elif isinstance(obj, Line3D):
        rotate_object(obj.start, angle, axis)
        rotate_object(obj.end, angle, axis)
    elif isinstance(obj, Polygon3D):
        for vertex in obj.vertices:
            rotate_object(vertex, angle, axis)
    elif isinstance(obj, BezierCurve3D) or isinstance(obj, BSplineCurve3D):
        for point in obj.control_points:
            rotate_object(point, angle, axis)
    elif isinstance(obj, Cone3D):
        rotate_object(obj.apex, angle, axis)
        rotate_object(obj.base_center, angle, axis)
        for vertex in obj.base_vertices:
            rotate_object(vertex, angle, axis)
    elif isinstance(obj, Cube3D):
        for vertex in obj.vertices:
            rotate_object(vertex, angle, axis)
    elif isinstance(obj, BezierSurface3D):
        for row in obj.control_points:
            for point in row:
                rotate_object(point, angle, axis)
    else:
        pass  # Para outros tipos de objetos
