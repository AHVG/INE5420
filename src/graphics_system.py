import tkinter as tk
import numpy as np
import math

from tkinter import filedialog, messagebox


# Classe para representar uma transformação
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

class Object3D:
    def __init__(self, name=''):
        self.name = name  # Nome do objeto

    """Classe base para todos os objetos 3D."""
    def transform(self, view_matrix):
        """Aplica a transformação (visualização) ao objeto."""
        pass

    def project(self, project_func):
        """Projeta o objeto 3D em 2D."""
        pass

    def draw(self, canvas, clip_region):
        """Desenha o objeto no canvas."""
        pass

class Point3D(Object3D):
    """Classe para representar um ponto em 3D."""
    def __init__(self, x, y, z, color='green', name=""):
        super().__init__(name)
        self.x = x  # Coordenadas originais
        self.y = y
        self.z = z
        self.color = color
        self.tx = self.x  # Coordenadas transformadas
        self.ty = self.y
        self.tz = self.z

    def transform(self, view_matrix):
        x, y, z = self.x, self.y, self.z
        # Transforma o ponto usando a matriz de visualização
        self.tx = view_matrix[0][0]*x + view_matrix[0][1]*y + view_matrix[0][2]*z + view_matrix[0][3]
        self.ty = view_matrix[1][0]*x + view_matrix[1][1]*y + view_matrix[1][2]*z + view_matrix[1][3]
        self.tz = view_matrix[2][0]*x + view_matrix[2][1]*y + view_matrix[2][2]*z + view_matrix[2][3]

    def is_visible(self):
        """Verifica se o ponto está na frente do observador (z negativo)."""
        return self.tz < 0

    def project(self, project_func):
        self.screen_x, self.screen_y = project_func(self.tx, self.ty, self.tz)

    def draw(self, canvas, clip_region):
        x_min, y_min, x_max, y_max = clip_region
        x, y = self.screen_x, self.screen_y
        # Clipping 2D para pontos
        if x_min <= x <= x_max and y_min <= y <= y_max:
            canvas.create_oval(x-3, y-3, x+3, y+3, fill=self.color)

class Line3D(Object3D):
    """Classe para representar uma reta (segmento de linha) em 3D."""
    def __init__(self, start_point, end_point, color='red', name=""):
        super().__init__(name)
        self.start = start_point  # Ponto inicial (Point3D)
        self.end = end_point      # Ponto final (Point3D)
        self.color = color

    def transform(self, view_matrix):
        self.start.transform(view_matrix)
        self.end.transform(view_matrix)

    def is_visible(self):
        """Verifica se a linha está na frente do observador."""
        return self.start.tz < 0 or self.end.tz < 0

    def project(self, project_func):
        self.start.project(project_func)
        self.end.project(project_func)

    def draw(self, canvas, clip_region):
        x1, y1 = self.start.screen_x, self.start.screen_y
        x2, y2 = self.end.screen_x, self.end.screen_y
        # Aplicar o clipping 2D usando o algoritmo Cohen-Sutherland
        clipped_line = cohen_sutherland_clip(x1, y1, x2, y2, clip_region)
        if clipped_line:
            x1_clipped, y1_clipped, x2_clipped, y2_clipped = clipped_line
            canvas.create_line(x1_clipped, y1_clipped, x2_clipped, y2_clipped, fill=self.color)

class Polygon3D(Object3D):
    """Classe para representar um polígono em 3D."""
    def __init__(self, vertices, color='purple', fill_color=None, name=""):
        super().__init__(name)
        self.vertices = vertices  # Lista de objetos Point3D
        self.color = color
        self.fill_color = fill_color  # Pode ser None ou uma string de cor

    def transform(self, view_matrix):
        for vertex in self.vertices:
            vertex.transform(view_matrix)

    def is_visible(self):
        """Verifica se o polígono está na frente do observador."""
        return any(v.tz < 0 for v in self.vertices)

    def project(self, project_func):
        for vertex in self.vertices:
            vertex.project(project_func)

    def draw(self, canvas, clip_region):
        # Coleta as coordenadas projetadas dos vértices
        points = []
        for vertex in self.vertices:
            x, y = vertex.screen_x, vertex.screen_y
            points.append((x, y))

        # Aplicar o algoritmo de clipping de Sutherland-Hodgman 2D
        clipped_polygon = sutherland_hodgman_clip(points, clip_region)
        if clipped_polygon:
            # Converte a lista de pontos em uma lista plana de coordenadas
            flat_points = [coord for point in clipped_polygon for coord in point]
            if self.fill_color:
                canvas.create_polygon(flat_points, fill=self.fill_color, outline=self.color)
            else:
                # Desenha apenas as arestas do polígono sem preenchimento
                canvas.create_line(flat_points + flat_points[:2], fill=self.color)

class BezierCurve3D(Object3D):
    """Classe para representar uma curva de Bézier em 3D."""
    def __init__(self, control_points, color='orange', name=""):
        super().__init__(name)
        self.control_points = control_points  # Lista de objetos Point3D
        self.curve_points = []  # Pontos da curva após a avaliação
        self.color = color

    def transform(self, view_matrix):
        for point in self.control_points:
            point.transform(view_matrix)

    def is_visible(self):
        """Verifica se a curva está na frente do observador."""
        return any(p.tz < 0 for p in self.control_points)

    def project(self, project_func):
        # Avalia a curva de Bézier e projeta os pontos
        self.curve_points = []
        n = len(self.control_points) - 1
        steps = 100  # Número de segmentos da curva
        for i in range(steps + 1):
            t = i / steps
            x, y, z = self.de_casteljau(t)
            if z < 0:  # Clipping simples em Z
                screen_x, screen_y = project_func(x, y, z)
                self.curve_points.append((screen_x, screen_y))

    def de_casteljau(self, t):
        """Avalia a curva de Bézier usando o algoritmo de De Casteljau."""
        points = [(p.tx, p.ty, p.tz) for p in self.control_points]
        n = len(points)
        for r in range(1, n):
            points = [
                (
                    (1 - t) * points[i][0] + t * points[i + 1][0],
                    (1 - t) * points[i][1] + t * points[i + 1][1],
                    (1 - t) * points[i][2] + t * points[i + 1][2],
                )
                for i in range(n - r)
            ]
        return points[0]

    def draw(self, canvas, clip_region):
        # Desenha a curva conectando os pontos projetados
        x_min, y_min, x_max, y_max = clip_region
        for i in range(len(self.curve_points) - 1):
            x0, y0 = self.curve_points[i]
            x1, y1 = self.curve_points[i + 1]
            # Clipping 2D para cada segmento da curva
            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
            if clipped_line:
                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)

class BSplineCurve3D(Object3D):
    """Classe para representar uma curva B-spline em 3D."""
    def __init__(self, control_points, degree=3, color='brown', name=""):
        super().__init__(name)
        self.control_points = control_points  # Lista de objetos Point3D
        self.degree = degree
        self.color = color
        self.knots = []
        self.curve_points = []

    def generate_knot_vector(self):
        n = len(self.control_points)
        k = self.degree
        # Usando uma sequência uniforme de knots
        self.knots = [0] * k + list(range(1, n - k + 1)) + [n - k + 1] * k

    def transform(self, view_matrix):
        for point in self.control_points:
            point.transform(view_matrix)

    def is_visible(self):
        """Verifica se a curva está na frente do observador."""
        return any(p.tz < 0 for p in self.control_points)

    def project(self, project_func):
        # Avalia a curva B-spline e projeta os pontos
        self.curve_points = []
        self.generate_knot_vector()
        n = len(self.control_points) - 1
        steps = 100  # Número de segmentos da curva
        u_min = self.knots[self.degree]
        u_max = self.knots[-self.degree - 1]
        for i in range(steps + 1):
            u = u_min + (u_max - u_min) * i / steps
            x, y, z = self.de_boor(u)
            if z < 0:  # Clipping simples em Z
                screen_x, screen_y = project_func(x, y, z)
                self.curve_points.append((screen_x, screen_y))

    def de_boor(self, u):
        """Avalia a curva B-spline usando o algoritmo de De Boor."""
        k = self.degree
        knots = self.knots
        points = [(p.tx, p.ty, p.tz) for p in self.control_points]
        n = len(points) - 1

        # Encontra o intervalo de knots
        for i in range(len(knots) - 1):
            if knots[i] <= u < knots[i + 1]:
                break
        else:
            i = n

        d = [list(p) for p in points[i - k:i + 1]]

        for r in range(1, k + 1):
            for j in range(k, r - 1, -1):
                denom = knots[i + j - r + 1] - knots[i - k + j]
                if denom == 0:
                    alpha = 0
                else:
                    alpha = (u - knots[i - k + j]) / denom
                d[j][0] = (1 - alpha) * d[j - 1][0] + alpha * d[j][0]
                d[j][1] = (1 - alpha) * d[j - 1][1] + alpha * d[j][1]
                d[j][2] = (1 - alpha) * d[j - 1][2] + alpha * d[j][2]

        return d[k]

    def draw(self, canvas, clip_region):
        # Desenha a curva conectando os pontos projetados
        x_min, y_min, x_max, y_max = clip_region
        for i in range(len(self.curve_points) - 1):
            x0, y0 = self.curve_points[i]
            x1, y1 = self.curve_points[i + 1]
            # Clipping 2D para cada segmento da curva
            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
            if clipped_line:
                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)

class Cone3D(Object3D):
    """Classe para representar um cone em 3D."""
    def __init__(self, base_center, height, radius, segments=20, color='magenta', fill_color='pink', name=""):
        super().__init__(name)
        self.base_center = base_center  # Point3D
        self.height = height
        self.radius = radius
        self.segments = segments
        self.color = color
        self.fill_color = fill_color

        # Vértice do topo do cone
        self.apex = Point3D(base_center.x, base_center.y + height, base_center.z)

        # Gera os pontos da base
        angle_increment = 2 * math.pi / segments
        self.base_vertices = []
        for i in range(segments):
            angle = i * angle_increment
            x = base_center.x + radius * math.cos(angle)
            z = base_center.z + radius * math.sin(angle)
            y = base_center.y
            self.base_vertices.append(Point3D(x, y, z))

        # Cria as faces do cone (como triângulos)
        self.faces = []
        for i in range(segments):
            next_i = (i + 1) % segments
            triangle = [self.apex, self.base_vertices[i], self.base_vertices[next_i]]
            self.faces.append(Polygon3D(triangle, color=self.color, fill_color=self.fill_color))

        # Base do cone
        self.base_face = Polygon3D(self.base_vertices, color=self.color, fill_color=self.fill_color)

    def transform(self, view_matrix):
        self.apex.transform(view_matrix)
        self.base_center.transform(view_matrix)
        for vertex in self.base_vertices:
            vertex.transform(view_matrix)
        self.base_face.transform(view_matrix)
        for face in self.faces:
            face.transform(view_matrix)

    def is_visible(self):
        """Verifica se o cone está na frente do observador."""
        return self.apex.tz < 0 or any(v.tz < 0 for v in self.base_vertices)

    def project(self, project_func):
        self.apex.project(project_func)
        self.base_center.project(project_func)
        for vertex in self.base_vertices:
            vertex.project(project_func)
        self.base_face.project(project_func)
        for face in self.faces:
            face.project(project_func)

    def draw(self, canvas, clip_region):
        # Desenha as faces laterais
        for face in self.faces:
            face.draw(canvas, clip_region)
        # Desenha a base
        self.base_face.draw(canvas, clip_region)

class Cube3D(Object3D):
    """Classe para representar um cubo em 3D."""
    def __init__(self, center, size, color='blue', name=""):
        super().__init__(name)
        self.size = size
        d = size / 2
        x, y, z = center.x, center.y, center.z
        self.color = color
        # Define os 8 vértices do cubo
        self.vertices = [
            Point3D(x - d, y - d, z - d),
            Point3D(x - d, y - d, z + d),
            Point3D(x - d, y + d, z - d),
            Point3D(x - d, y + d, z + d),
            Point3D(x + d, y - d, z - d),
            Point3D(x + d, y - d, z + d),
            Point3D(x + d, y + d, z - d),
            Point3D(x + d, y + d, z + d),
        ]
        # Define as faces do cubo (como polígonos)
        self.faces = [
            Polygon3D([self.vertices[0], self.vertices[1], self.vertices[3], self.vertices[2]], color=self.color),
            Polygon3D([self.vertices[4], self.vertices[5], self.vertices[7], self.vertices[6]], color=self.color),
            Polygon3D([self.vertices[0], self.vertices[1], self.vertices[5], self.vertices[4]], color=self.color),
            Polygon3D([self.vertices[2], self.vertices[3], self.vertices[7], self.vertices[6]], color=self.color),
            Polygon3D([self.vertices[0], self.vertices[2], self.vertices[6], self.vertices[4]], color=self.color),
            Polygon3D([self.vertices[1], self.vertices[3], self.vertices[7], self.vertices[5]], color=self.color),
        ]

    def transform(self, view_matrix):
        for vertex in self.vertices:
            vertex.transform(view_matrix)
        for face in self.faces:
            face.transform(view_matrix)

    def is_visible(self):
        """Verifica se o cubo está na frente do observador."""
        return any(v.tz < 0 for v in self.vertices)

    def project(self, project_func):
        for vertex in self.vertices:
            vertex.project(project_func)
        for face in self.faces:
            face.project(project_func)

    def draw(self, canvas, clip_region):
        for face in self.faces:
            face.draw(canvas, clip_region)

class BezierSurface3D(Object3D):
    """Classe para representar uma superfície bicúbica de Bézier em 3D."""
    def __init__(self, control_points_matrix, color='cyan', wireframe=True, name=""):
        """
        control_points_matrix: matriz 4x4 de pontos de controle (Point3D)
        color: cor da superfície
        wireframe: se True, desenha a malha; se False, preenche os polígonos
        """
        super().__init__(name)
        self.control_points = control_points_matrix  # Matriz 4x4 de pontos de controle
        self.color = color
        self.wireframe = wireframe
        self.surface_points = []  # Pontos avaliados na superfície

    def transform(self, view_matrix):
        for row in self.control_points:
            for point in row:
                point.transform(view_matrix)

    def is_visible(self):
        """Verifica se a superfície está na frente do observador."""
        return any(point.tz < 0 for row in self.control_points for point in row)

    def project(self, project_func):
        # Avalia a superfície de Bézier e projeta os pontos
        self.surface_points = []
        steps = 10  # Número de divisões na superfície
        for i in range(steps + 1):
            u = i / steps
            row = []
            for j in range(steps + 1):
                v = j / steps
                x, y, z = self.de_casteljau_surface(u, v)
                if z < 0:  # Clipping simples em Z
                    screen_x, screen_y = project_func(x, y, z)
                    row.append((screen_x, screen_y))
                else:
                    row.append(None)
            self.surface_points.append(row)

    def de_casteljau_surface(self, u, v):
        """Avalia a superfície bicúbica de Bézier usando o algoritmo de De Casteljau."""
        # Primeiro, para cada linha de pontos de controle, avaliamos no parâmetro u
        temp = []
        for i in range(4):
            points = [(p.tx, p.ty, p.tz) for p in self.control_points[i]]
            temp.append(self.de_casteljau_curve(points, u))
        # Depois, avaliamos a curva resultante no parâmetro v
        x, y, z = self.de_casteljau_curve(temp, v)
        return x, y, z

    def de_casteljau_curve(self, points, t):
        """Avalia uma curva de Bézier unidimensional usando o algoritmo de De Casteljau."""
        n = len(points)
        for r in range(1, n):
            points = [
                (
                    (1 - t) * points[i][0] + t * points[i + 1][0],
                    (1 - t) * points[i][1] + t * points[i + 1][1],
                    (1 - t) * points[i][2] + t * points[i + 1][2],
                )
                for i in range(n - r)
            ]
        return points[0]

    def draw(self, canvas, clip_region):
        # Desenha a superfície como uma malha de linhas ou polígonos
        steps = len(self.surface_points) - 1
        for i in range(steps):
            for j in range(steps):
                p0 = self.surface_points[i][j]
                p1 = self.surface_points[i][j + 1]
                p2 = self.surface_points[i + 1][j + 1]
                p3 = self.surface_points[i + 1][j]
                # Verifica se os pontos estão visíveis
                if None not in (p0, p1, p2, p3):
                    if self.wireframe:
                        # Desenha as arestas do quadrilátero
                        lines = [
                            (p0, p1),
                            (p1, p2),
                            (p2, p3),
                            (p3, p0),
                        ]
                        for line in lines:
                            x0, y0 = line[0]
                            x1, y1 = line[1]
                            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
                            if clipped_line:
                                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)
                    else:
                        # Desenha o quadrilátero preenchido
                        polygon = [p0, p1, p2, p3]
                        clipped_polygon = sutherland_hodgman_clip(polygon, clip_region)
                        if clipped_polygon:
                            flat_points = [coord for point in clipped_polygon for coord in point]
                            canvas.create_polygon(flat_points, fill=self.color, outline='black')

class BSplineSurface3D(Object3D):
    """Class to represent a bicubic B-spline surface in 3D using forward differences."""
    def __init__(self, control_points_matrix, color='yellow', wireframe=True, name=""):
        super().__init__(name)
        self.control_points = control_points_matrix  # Matrix of control points (list of lists of Point3D)
        self.color = color
        self.wireframe = wireframe
        self.surface_points = []  # Evaluated surface points
        self.steps = 10  # Number of divisions in u and v directions

    def transform(self, view_matrix):
        for row in self.control_points:
            for point in row:
                point.transform(view_matrix)

    def is_visible(self):
        """Check if any part of the surface is visible."""
        return any(point.tz < 0 for row in self.control_points for point in row)

    def project(self, project_func):
        """Evaluate the surface using forward differences and project the points."""
        self.surface_points = []
        self.project_func = project_func  # Store the projection function for use in other methods

        # Use forward differences to compute surface points
        n = len(self.control_points)
        m = len(self.control_points[0])
        if n < 4 or m < 4:
            # Need at least 4x4 control points
            return

        # Basis matrix for B-spline
        M_bspline = (1/6) * np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ])

        # Iterate over patches
        for i in range(n - 3):
            for j in range(m - 3):
                # Extract 4x4 control points for the current patch
                Gx = np.array([[self.control_points[i + a][j + b].tx for b in range(4)] for a in range(4)])
                Gy = np.array([[self.control_points[i + a][j + b].ty for b in range(4)] for a in range(4)])
                Gz = np.array([[self.control_points[i + a][j + b].tz for b in range(4)] for a in range(4)])

                # Compute the coefficients matrices
                Coeff_x = M_bspline @ Gx @ M_bspline.T
                Coeff_y = M_bspline @ Gy @ M_bspline.T
                Coeff_z = M_bspline @ Gz @ M_bspline.T

                # Evaluate the patch using forward differences
                patch_points = self.evaluate_patch_forward_differences(Coeff_x, Coeff_y, Coeff_z)
                self.surface_points.extend(patch_points)

    def evaluate_patch_forward_differences(self, Coeff_x, Coeff_y, Coeff_z):
        """Evaluate a single patch using forward differences."""
        steps = self.steps
        du = 1 / steps
        dv = 1 / steps

        # Initialize arrays to hold points
        patch_points = []

        # Compute initial values and deltas for u and v
        u = 0
        for s in range(steps + 1):
            v = 0
            # Initialize De Boor's algorithm for the u-direction
            U = np.array([u**3, u**2, u, 1])
            delta_U = np.array([3*u**2, 2*u, 1, 0]) * du
            delta2_U = np.array([6*u, 2, 0, 0]) * du**2
            delta3_U = np.array([6, 0, 0, 0]) * du**3

            # Evaluate the initial point in v-direction
            V = np.array([v**3, v**2, v, 1])
            delta_V = np.array([3*v**2, 2*v, 1, 0]) * dv
            delta2_V = np.array([6*v, 2, 0, 0]) * dv**2
            delta3_V = np.array([6, 0, 0, 0]) * dv**3

            # Compute initial point
            x = U @ Coeff_x @ V
            y = U @ Coeff_y @ V
            z = U @ Coeff_z @ V

            # Store the point if visible
            if z < 0:
                screen_x, screen_y = self.project_func(x, y, z)
                patch_points.append((screen_x, screen_y))
            else:
                patch_points.append(None)

            # Precompute deltas for v-direction
            delta_x_v = U @ Coeff_x @ delta_V
            delta_y_v = U @ Coeff_y @ delta_V
            delta_z_v = U @ Coeff_z @ delta_V

            delta2_x_v = U @ Coeff_x @ delta2_V
            delta2_y_v = U @ Coeff_y @ delta2_V
            delta2_z_v = U @ Coeff_z @ delta2_V

            delta3_x_v = U @ Coeff_x @ delta3_V
            delta3_y_v = U @ Coeff_y @ delta3_V
            delta3_z_v = U @ Coeff_z @ delta3_V

            # Iterate over v
            for t in range(steps):
                # Update x, y, z in v-direction using forward differences
                delta_x_v += delta2_x_v
                delta_y_v += delta2_y_v
                delta_z_v += delta2_z_v

                delta2_x_v += delta3_x_v
                delta2_y_v += delta3_y_v
                delta2_z_v += delta3_z_v

                x += delta_x_v
                y += delta_y_v
                z += delta_z_v

                if z < 0:
                    screen_x, screen_y = self.project_func(x, y, z)
                    patch_points.append((screen_x, screen_y))
                else:
                    patch_points.append(None)
                v += dv
            u += du
        return patch_points

    def draw(self, canvas, clip_region):
        """Draw the surface."""
        steps_u = self.steps
        steps_v = self.steps

        num_patches_u = len(self.control_points) - 3
        num_patches_v = len(self.control_points[0]) - 3

        total_steps_u = steps_u * num_patches_u
        total_steps_v = steps_v * num_patches_v

        for i in range(total_steps_u):
            for j in range(total_steps_v):
                idx = i * (total_steps_v + 1) + j
                p0 = self.surface_points[idx]
                p1 = self.surface_points[idx + 1]
                p2 = self.surface_points[idx + total_steps_v + 2]
                p3 = self.surface_points[idx + total_steps_v + 1]

                if None not in (p0, p1, p2, p3):
                    if self.wireframe:
                        # Draw lines
                        lines = [
                            (p0, p1),
                            (p1, p2),
                            (p2, p3),
                            (p3, p0)
                        ]
                        for line in lines:
                            x0, y0 = line[0]
                            x1, y1 = line[1]
                            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
                            if clipped_line:
                                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)
                    else:
                        # Draw filled polygon
                        polygon = [p0, p1, p2, p3]
                        clipped_polygon = sutherland_hodgman_clip(polygon, clip_region)
                        if clipped_polygon:
                            flat_points = [coord for point in clipped_polygon for coord in point]
                            canvas.create_polygon(flat_points, fill=self.color, outline='black')

# Funções de transformação

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

# Funções de clipping 2D

INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def compute_out_code(x, y, clip_region):
    x_min, y_min, x_max, y_max = clip_region
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= TOP  # Observação: invertido por causa da coordenada Y na tela
    elif y > y_max:
        code |= BOTTOM
    return code

def cohen_sutherland_clip(x0, y0, x1, y1, clip_region):
    """Implementação do algoritmo de clipping de linha de Cohen-Sutherland."""
    x_min, y_min, x_max, y_max = clip_region
    out_code0 = compute_out_code(x0, y0, clip_region)
    out_code1 = compute_out_code(x1, y1, clip_region)
    accept = False

    while True:
        if not (out_code0 | out_code1):
            # Ambos os pontos estão dentro da região
            accept = True
            break
        elif out_code0 & out_code1:
            # Ambos os pontos estão fora da região (na mesma área externa)
            break
        else:
            # Pelo menos um ponto está fora, precisamos recortar
            out_code_out = out_code0 if out_code0 else out_code1
            if out_code_out & TOP:
                x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
                y = y_min
            elif out_code_out & BOTTOM:
                x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
                y = y_max
            elif out_code_out & RIGHT:
                y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
                x = x_max
            elif out_code_out & LEFT:
                y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
                x = x_min

            # Atualiza o ponto fora da região
            if out_code_out == out_code0:
                x0, y0 = x, y
                out_code0 = compute_out_code(x0, y0, clip_region)
            else:
                x1, y1 = x, y
                out_code1 = compute_out_code(x1, y1, clip_region)

    if accept:
        return x0, y0, x1, y1
    else:
        return None

def sutherland_hodgman_clip(polygon, clip_region):
    """Implementação do algoritmo de clipping de polígono de Sutherland-Hodgman."""
    x_min, y_min, x_max, y_max = clip_region
    clip_edges = [
        ('left', x_min),
        ('right', x_max),
        ('bottom', y_max),
        ('top', y_min)  # Nota: invertido devido ao sistema de coordenadas
    ]

    def inside(p, edge):
        position, value = edge
        x, y = p
        if position == 'left':
            return x >= value
        elif position == 'right':
            return x <= value
        elif position == 'bottom':
            return y <= value
        elif position == 'top':
            return y >= value

    def compute_intersection(p1, p2, edge):
        position, value = edge
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and y1 == y2:
            return p1  # Segmento degenerado

        if position in ('left', 'right'):
            x = value
            y = y1 + (y2 - y1) * (value - x1) / (x2 - x1)
        else:  # 'top' ou 'bottom'
            y = value
            x = x1 + (x2 - x1) * (value - y1) / (y2 - y1)
        return (x, y)

    output_list = polygon
    for edge in clip_edges:
        input_list = output_list
        output_list = []
        if not input_list:
            break
        s = input_list[-1]
        for e in input_list:
            if inside(e, edge):
                if not inside(s, edge):
                    output_list.append(compute_intersection(s, e, edge))
                output_list.append(e)
            elif inside(s, edge):
                output_list.append(compute_intersection(s, e, edge))
            s = e

    return output_list

class Window:
    def __init__(self, width=800, height=600, title="Sistema Gráfico 3D"):
        self.width = width
        self.height = height
        self.title = title

        # Configurações da janela
        self.root = tk.Tk()
        self.root.title(self.title)

        # Criação do menu
        self.create_menu()

        # Frame principal para conter o canvas e os botões
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Configurações para redimensionamento
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)

        # Canvas
        self.canvas = tk.Canvas(main_frame, bg='white', width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # Vincula o evento de redimensionamento do canvas
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # Painel lateral para os botões e a lista de objetos
        side_frame = tk.Frame(main_frame)
        side_frame.grid(row=0, column=1, sticky='ns')

        # Definindo a margem
        self.margin = 50  # Pixels
        # Região de clipping (limites do canvas com margem)
        self.clip_region = (
            self.margin,
            self.margin,
            self.width - self.margin,
            self.height - self.margin
        )

        # Centro da tela
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Parâmetros de projeção
        self.scale = 500  # Controle de zoom
        self.projection_type = 'perspective'  # Tipo de projeção inicial

        # Posição e orientação do observador
        self.eye = [0, 0, -10]  # Posição da câmera
        self.up = [0, 1, 0]  # Vetor "para cima"

        # Ângulos de rotação para ajustar o vetor look_at
        self.yaw = 0  # Rotação em torno do eixo Y
        self.pitch = 0  # Rotação em torno do eixo X

        # Lista de objetos 3D
        self.objects = []

        # Objeto selecionado
        self.selected_object = None

        # Lista de transformações pendentes
        self.transformations = []

        # Inicializa os objetos 3D
        self.create_objects()

        # Criação de Subframes dentro do side_frame
        # 1. Frame para os Botões de Navegação
        navigation_frame = tk.Frame(side_frame)
        navigation_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # 2. Frame para a Lista de Objetos e Controles de Transformação
        control_frame = tk.Frame(side_frame)
        control_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        create_frame = tk.Frame(side_frame)
        create_frame.grid(row=0, column=3, sticky='nsew', padx=5, pady=5)

        # Configurações de expansão para os subframes
        side_frame.rowconfigure(0, weight=0)  # navigation_frame não expande verticalmente
        side_frame.rowconfigure(1, weight=1)  # control_frame expande verticalmente
        side_frame.columnconfigure(0, weight=1)

        # Atualiza os métodos para usar os novos subframes
        self.create_navigation_buttons(navigation_frame)
        self.create_object_list_and_transform_controls(control_frame)
        self.create_layout(create_frame)

        self.bind_events()

        # Inicia o loop de atualização
        self.update()

    def create_menu(self):
        """Cria o menu da aplicação."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Exportar OBJ", command=self.export_obj_file)
        file_menu.add_command(label="Importar OBJ", command=self.import_obj_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

    def bind_events(self):
        # Liga os eventos de teclado
        self.root.bind('<Left>', self.rotate_left)
        self.root.bind('<Right>', self.rotate_right)
        self.root.bind('<Up>', self.rotate_up)
        self.root.bind('<Down>', self.rotate_down)
        self.root.bind('<w>', self.move_forward)
        self.root.bind('<s>', self.move_backward)
        self.root.bind('<a>', self.move_left)
        self.root.bind('<d>', self.move_right)
        self.root.bind('<plus>', self.zoom_in)   # Tecla '+'
        self.root.bind('<minus>', self.zoom_out)  # Tecla '-'
        self.root.bind('<MouseWheel>', self.on_mouse_wheel)  # Scroll do mouse
        self.root.bind('<p>', lambda event: self.toggle_projection())
        self.canvas.focus_set()

    def on_canvas_resize(self, event):
        """Atualiza os parâmetros quando o canvas é redimensionado."""
        self.width = event.width
        self.height = event.height

        # Atualiza o centro do canvas
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Atualiza a região de clipping
        self.clip_region = (
            self.margin,
            self.margin,
            self.width - self.margin,
            self.height - self.margin
        )

    def create_navigation_buttons(self, parent):
        # Cria botões para rotacionar a câmera
        rotate_label = tk.Label(parent, text="Rotação")
        rotate_label.grid(row=0, column=0, columnspan=3, pady=5)

        btn_rotate_up = tk.Button(parent, text="↑", command=lambda: self.rotate_up())
        btn_rotate_up.grid(row=1, column=1)

        btn_rotate_left = tk.Button(parent, text="←", command=lambda: self.rotate_left())
        btn_rotate_left.grid(row=2, column=0)

        btn_rotate_right = tk.Button(parent, text="→", command=lambda: self.rotate_right())
        btn_rotate_right.grid(row=2, column=2)

        btn_rotate_down = tk.Button(parent, text="↓", command=lambda: self.rotate_down())
        btn_rotate_down.grid(row=3, column=1)

        # Espaço entre grupos de botões
        spacer = tk.Label(parent, text="")
        spacer.grid(row=4, column=0, pady=10)

        # Cria botões para mover a câmera
        move_label = tk.Label(parent, text="Movimento")
        move_label.grid(row=5, column=0, columnspan=3, pady=5)

        btn_move_forward = tk.Button(parent, text="Avançar (W)", command=lambda: self.move_forward())
        btn_move_forward.grid(row=6, column=0, columnspan=3, sticky='ew')

        btn_move_backward = tk.Button(parent, text="Recuar (S)", command=lambda: self.move_backward())
        btn_move_backward.grid(row=7, column=0, columnspan=3, sticky='ew')

        btn_move_left = tk.Button(parent, text="Esquerda (A)", command=lambda: self.move_left())
        btn_move_left.grid(row=8, column=0, columnspan=3, sticky='ew')

        btn_move_right = tk.Button(parent, text="Direita (D)", command=lambda: self.move_right())
        btn_move_right.grid(row=9, column=0, columnspan=3, sticky='ew')

        # Espaço entre grupos de botões
        spacer = tk.Label(parent, text="")
        spacer.grid(row=10, column=0, pady=10)

        # Cria botões para zoom
        zoom_label = tk.Label(parent, text="Zoom")
        zoom_label.grid(row=11, column=0, columnspan=3, pady=5)

        btn_zoom_in = tk.Button(parent, text="Aumentar Zoom (+)", command=lambda: self.zoom_in())
        btn_zoom_in.grid(row=12, column=0, columnspan=3, sticky='ew')

        btn_zoom_out = tk.Button(parent, text="Diminuir Zoom (-)", command=lambda: self.zoom_out())
        btn_zoom_out.grid(row=13, column=0, columnspan=3, sticky='ew')

        # Espaço entre grupos de botões
        spacer = tk.Label(parent, text="")
        spacer.grid(row=14, column=0, pady=10)

        # Botão para alternar projeção
        self.projection_button = tk.Button(parent, text='Usar Projeção Paralela', command=self.toggle_projection)
        self.projection_button.grid(row=15, column=0, columnspan=3, sticky='ew')

        # Configurações para expandir os botões
        for i in range(3):
            parent.columnconfigure(i, weight=1)

    def create_object_list_and_transform_controls(self, parent):
        """Cria a lista de objetos e os controles de transformação no painel lateral."""
        # Dividimos o parent em linhas usando grid

        # Frame para a lista de objetos
        list_frame = tk.Frame(parent)
        list_frame.grid(row=0, column=0, sticky='nsew')

        # Frame para os controles de transformação
        trans_frame = tk.LabelFrame(parent, text="Transformações")
        trans_frame.grid(row=1, column=0, sticky='nsew', pady=10)

        # Frame para a lista de transformações pendentes
        pending_frame = tk.LabelFrame(parent, text="Transformações Pendentes")
        pending_frame.grid(row=2, column=0, sticky='nsew', pady=10)

        # Configurações de redimensionamento
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=0)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

        # Lista de objetos
        label = tk.Label(list_frame, text="Objetos na Cena")
        label.pack(pady=5)

        self.object_listbox = tk.Listbox(list_frame)
        self.object_listbox.pack(fill=tk.BOTH, expand=True)
        self.object_listbox.bind('<<ListboxSelect>>', self.on_object_select)

        # Preenche a lista com os nomes dos objetos
        for obj in self.objects:
            self.object_listbox.insert(tk.END, obj.name)

        # Controles de transformação
        # Controles de Translação
        tk.Label(trans_frame, text="Translação (dx, dy, dz):").grid(row=0, column=0, columnspan=3)
        self.entry_dx = tk.Entry(trans_frame, width=5)
        self.entry_dx.grid(row=1, column=0)
        self.entry_dy = tk.Entry(trans_frame, width=5)
        self.entry_dy.grid(row=1, column=1)
        self.entry_dz = tk.Entry(trans_frame, width=5)
        self.entry_dz.grid(row=1, column=2)
        btn_add_translate = tk.Button(trans_frame, text="Adicionar Translação", command=self.add_translation)
        btn_add_translate.grid(row=2, column=0, columnspan=3, pady=5)

        # Controles de Rotação
        tk.Label(trans_frame, text="Rotação (ângulo, eixo):").grid(row=3, column=0, columnspan=3)
        self.entry_angle = tk.Entry(trans_frame, width=5)
        self.entry_angle.grid(row=4, column=0)
        self.axis_var = tk.StringVar(value='x')
        tk.Radiobutton(trans_frame, text='X', variable=self.axis_var, value='x').grid(row=4, column=1)
        tk.Radiobutton(trans_frame, text='Y', variable=self.axis_var, value='y').grid(row=4, column=2)
        tk.Radiobutton(trans_frame, text='Z', variable=self.axis_var, value='z').grid(row=5, column=1)
        btn_add_rotate = tk.Button(trans_frame, text="Adicionar Rotação", command=self.add_rotation)
        btn_add_rotate.grid(row=6, column=0, columnspan=3, pady=5)

        # Controles de Escala
        tk.Label(trans_frame, text="Escala (sx, sy, sz):").grid(row=7, column=0, columnspan=3)
        self.entry_sx = tk.Entry(trans_frame, width=5)
        self.entry_sx.grid(row=8, column=0)
        self.entry_sy = tk.Entry(trans_frame, width=5)
        self.entry_sy.grid(row=8, column=1)
        self.entry_sz = tk.Entry(trans_frame, width=5)
        self.entry_sz.grid(row=8, column=2)
        btn_add_scale = tk.Button(trans_frame, text="Adicionar Escala", command=self.add_scaling)
        btn_add_scale.grid(row=9, column=0, columnspan=3, pady=5)

        # Configurações do grid
        for i in range(3):
            trans_frame.columnconfigure(i, weight=1)

        # Lista de transformações pendentes
        self.transformation_listbox = tk.Listbox(pending_frame)
        self.transformation_listbox.pack(fill=tk.BOTH, expand=True)

        # Botões para aplicar ou limpar transformações
        btn_apply_transformations = tk.Button(pending_frame, text="Aplicar Transformações", command=self.apply_transformations)
        btn_apply_transformations.pack(pady=5)

        btn_clear_transformations = tk.Button(pending_frame, text="Limpar Transformações", command=self.clear_transformations)
        btn_clear_transformations.pack(pady=5)

    def create_layout(self, parent):
        """Cria o layout com inputs e botões para criação de objetos."""
        # Título
        title = tk.Label(parent, text="Adicionar Objetos", bg='lightgray', font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        # Input e botão para Ponto
        tk.Label(parent, text="Ponto (x,y,z):", bg='lightgray').pack()
        self.point_entry = tk.Entry(parent)
        self.point_entry.pack()
        btn_add_point = tk.Button(parent, text="Adicionar Ponto", command=self.add_point)
        btn_add_point.pack(pady=5)

        # Input e botão para Linha
        tk.Label(parent, text="Linha (x1,y1,z1)-(x2,y2,z2):", bg='lightgray').pack()
        self.line_entry = tk.Entry(parent)
        self.line_entry.pack()
        btn_add_line = tk.Button(parent, text="Adicionar Linha", command=self.add_line)
        btn_add_line.pack(pady=5)

        # Input e botão para Polígono
        tk.Label(parent, text="Polígono (x1,y1,z1;x2,y2,z2;...):", bg='lightgray').pack()
        self.polygon_entry = tk.Entry(parent)
        self.polygon_entry.pack()
        btn_add_polygon = tk.Button(parent, text="Adicionar Polígono", command=self.add_polygon)
        btn_add_polygon.pack(pady=5)

        # Input e botão para Curva de Bézier
        tk.Label(parent, text="Curva Bézier (x1,y1,z1;x2,y2,z2;...):", bg='lightgray').pack()
        self.curve_entry = tk.Entry(parent)
        self.curve_entry.pack()
        btn_add_curve = tk.Button(parent, text="Adicionar Curva Bézier", command=self.add_bezier_curve)
        btn_add_curve.pack(pady=5)

        # --------------------- Entrada para Superfície Bicúbica ---------------------
        tk.Label(parent, text="Superfície Bicúbica 4x4:", bg='lightgray', font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        tk.Label(parent, text="Formato:", bg='lightgray').pack()
        tk.Label(parent, text="(x11,y11,z11),(x12,y12,z12),...;(x21,y21,z21),(x22,y22,z22),...;...;(x41,y41,z41),(x42,y42,z42),...", bg='lightgray', wraplength=180, justify='left').pack(padx=10)

        self.surface_entry = tk.Entry(parent, width=30)
        self.surface_entry.pack(pady=5)

        btn_add_surface = tk.Button(parent, text="Adicionar Superfície Bicúbica", command=self.add_bicubic_surface)
        btn_add_surface.pack(pady=5)
        
        # --------------------- Input for Bicubic B-spline Surface ---------------------
        tk.Label(parent, text="Superfície B-spline Bicúbica:", bg='lightgray', font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        tk.Label(parent, text="Formato:", bg='lightgray').pack()
        tk.Label(parent, text="(x11,y11,z11),(x12,y12,z12),...;(x21,y21,z21),(x22,y22,z22),...;...", bg='lightgray', wraplength=180, justify='left').pack(padx=10)

        self.bspline_surface_entry = tk.Entry(parent, width=30)
        self.bspline_surface_entry.pack(pady=5)

        btn_add_bspline_surface = tk.Button(parent, text="Adicionar Superfície B-spline", command=self.add_bspline_surface)
        btn_add_bspline_surface.pack(pady=5)

    def create_objects(self):
        # Superfície de Bézier
        control_points_matrix = [
            [Point3D(-1.5, -1.5, 4), Point3D(-0.5, -1.5, 2), Point3D(0.5, -1.5, -1), Point3D(1.5, -1.5, 2)],
            [Point3D(-1.5, -0.5, 1), Point3D(-0.5, -0.5, 3), Point3D(0.5, -0.5, 0), Point3D(1.5, -0.5, -1)],
            [Point3D(-1.5, 0.5, 4), Point3D(-0.5, 0.5, 0), Point3D(0.5, 0.5, 3), Point3D(1.5, 0.5, 4)],
            [Point3D(-1.5, 1.5, -2), Point3D(-0.5, 1.5, -2), Point3D(0.5, 1.5, 0), Point3D(1.5, 1.5, -1)],
        ]
        bezier_surface = BezierSurface3D(control_points_matrix, color='cyan', wireframe=True, name="Superficie de Bezier")
        rotate_object(bezier_surface, 30, 'x')
        self.objects.append(bezier_surface)

        # B-spline Bicubic Surface
        control_points_matrix_bspline = [
            [Point3D(-1.5, -1.5, 4), Point3D(-0.5, -1.5, 2), Point3D(0.5, -1.5, -1), Point3D(1.5, -1.5, 2)],
            [Point3D(-1.5, -0.5, 1), Point3D(-0.5, -0.5, 3), Point3D(0.5, -0.5, 0), Point3D(1.5, -0.5, -1)],
            [Point3D(-1.5, 0.5, 4), Point3D(-0.5, 0.5, 0), Point3D(0.5, 0.5, 3), Point3D(1.5, 0.5, 4)],
            [Point3D(-1.5, 1.5, -2), Point3D(-0.5, 1.5, -2), Point3D(0.5, 1.5, 0), Point3D(1.5, 1.5, -1)],
        ]
        bspline_surface = BSplineSurface3D(control_points_matrix_bspline, color='yellow', wireframe=True, name="Superfície B-spline")
        rotate_object(bspline_surface, 30, 'x')
        self.objects.append(bspline_surface)


        # Cubo no Octante 1 (x > 0, y > 0, z > 0)
        cube = Cube3D(Point3D(2, 2, 2), 2, color='blue', name="Cubo")
        rotate_object(cube, 45, 'x')
        rotate_object(cube, 30, 'y')
        translate_object(cube, 0, 0, -1)
        self.objects.append(cube)

        # Ponto no Octante 2 (x < 0, y > 0, z > 0)
        point = Point3D(-2, 2, 2, color='green', name="Ponto")
        translate_object(point, 1, 0, 0)
        self.objects.append(point)

        # Reta no Octante 3 (x < 0, y < 0, z > 0)
        line = Line3D(Point3D(-2, -2, 2), Point3D(-1, -1, 2), color='red', name="Linha")
        rotate_object(line, 45, 'z')
        self.objects.append(line)

        # Polígono no Octante 4 (x > 0, y < 0, z > 0) sem preenchimento
        vertices = [
            Point3D(1, -1, 2),
            Point3D(2, -2, 2),
            Point3D(3, -1, 2),
            Point3D(2, -0.5, 2)
        ]
        polygon = Polygon3D(vertices, color='purple', name="Poligono")  # fill_color não especificado
        scale_object(polygon, 1, 2, 1)
        self.objects.append(polygon)

        # Curva de Bézier no Octante 5 (x > 0, y > 0, z < 0)
        bezier_control_points = [
            Point3D(1, 1, -1),
            Point3D(2, 2, -1),
            Point3D(3, 0, -1),
            Point3D(4, 2, -1),
            Point3D(5, 1, -1),
            Point3D(6, 3, -1),
            Point3D(7, 0, -1)
        ]
        bezier_curve = BezierCurve3D(bezier_control_points, color='orange', name="Curva de Bezier")
        translate_object(bezier_curve, -2, 0, 0)
        self.objects.append(bezier_curve)

        # Curva B-spline no Octante 6 (x < 0, y > 0, z < 0)
        bspline_control_points = [
            Point3D(-1, 1, -1),
            Point3D(-2, 2, -2),
            Point3D(-3, 0, -3),
            Point3D(-4, 2, -4),
            Point3D(-5, 1, -5),
            Point3D(-6, 3, -6),
            Point3D(-7, 0, -7),
            Point3D(-8, 2, -8),
            Point3D(-9, 1, -9)
        ]
        bspline_curve = BSplineCurve3D(bspline_control_points, degree=3, color='brown', name="BSpline")
        scale_object(bspline_curve, 0.5, 0.5, 0.5)
        self.objects.append(bspline_curve)

        # Cone no Octante 7 (x < 0, y < 0, z < 0)
        cone = Cone3D(
            base_center=Point3D(-2, -2, -2),
            height=3,
            radius=1,
            segments=20,
            color='magenta',
            fill_color='pink',
            name="Cone"
        )
        rotate_object(cone, 30, 'y')
        self.objects.append(cone)

    def on_object_select(self, event):
        """Chamado quando um objeto é selecionado na lista."""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.selected_object = self.objects[index]
        else:
            self.selected_object = None

    def add_translation(self):
        """Adiciona uma translação à lista de transformações."""
        try:
            dx = float(self.entry_dx.get())
            dy = float(self.entry_dy.get())
            dz = float(self.entry_dz.get())
            transformation = Transformation('translate', (dx, dy, dz))
            self.transformations.append(transformation)
            self.transformation_listbox.insert(tk.END, str(transformation))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para a translação.")
        finally:
            # Limpa as entradas
            self.entry_dx.delete(0, tk.END)
            self.entry_dy.delete(0, tk.END)
            self.entry_dz.delete(0, tk.END)

    def add_rotation(self):
        """Adiciona uma rotação à lista de transformações."""
        try:
            angle = float(self.entry_angle.get())
            axis = self.axis_var.get()
            transformation = Transformation('rotate', (angle, axis))
            self.transformations.append(transformation)
            self.transformation_listbox.insert(tk.END, str(transformation))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para o ângulo.")
        finally:
            # Limpa a entrada
            self.entry_angle.delete(0, tk.END)

    def add_scaling(self):
        """Adiciona uma escala à lista de transformações."""
        try:
            sx = float(self.entry_sx.get())
            sy = float(self.entry_sy.get())
            sz = float(self.entry_sz.get())
            transformation = Transformation('scale', (sx, sy, sz))
            self.transformations.append(transformation)
            self.transformation_listbox.insert(tk.END, str(transformation))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para a escala.")
        finally:
            # Limpa as entradas
            self.entry_sx.delete(0, tk.END)
            self.entry_sy.delete(0, tk.END)
            self.entry_sz.delete(0, tk.END)

    def apply_transformations(self):
        """Aplica todas as transformações pendentes ao objeto selecionado."""
        if self.selected_object:
            for transformation in self.transformations:
                if transformation.type == 'translate':
                    dx, dy, dz = transformation.params
                    translate_object(self.selected_object, dx, dy, dz)
                elif transformation.type == 'rotate':
                    angle, axis = transformation.params
                    rotate_object(self.selected_object, angle, axis)
                elif transformation.type == 'scale':
                    sx, sy, sz = transformation.params
                    scale_object(self.selected_object, sx, sy, sz)
            # Limpa a lista de transformações após aplicar
            self.clear_transformations()
        else:
            messagebox.showwarning("Nenhum objeto selecionado", "Por favor, selecione um objeto na lista para aplicar as transformações.")

    def clear_transformations(self):
        """Limpa a lista de transformações pendentes."""
        self.transformations.clear()
        self.transformation_listbox.delete(0, tk.END)

    def add_bicubic_surface(self):
        """Adiciona uma superfície bicúbica com os pontos de controle especificados."""
        input_str = self.surface_entry.get()
        try:
            rows = input_str.strip().split(';')
            if len(rows) != 4:
                raise ValueError("A superfície bicúbica requer exatamente 4 linhas de pontos de controle.")

            control_points_matrix = []
            for row_index, row in enumerate(rows):
                # Remove espaços e divide os pontos
                points_str = row.strip().split('),(')
                # Remove possíveis '(' do primeiro ponto e ')' do último ponto
                points_str[0] = points_str[0].lstrip('(')
                points_str[-1] = points_str[-1].rstrip(')')
                if len(points_str) != 4:
                    raise ValueError(f"Cada linha deve conter exatamente 4 pontos de controle. Erro na linha {row_index + 1}.")

                row_points = []
                for point_str in points_str:
                    coords = point_str.split(',')
                    if len(coords) != 3:
                        raise ValueError(f"Formato inválido para o ponto: {point_str}")
                    x, y, z = map(float, coords)
                    row_points.append(Point3D(x, y, z))
                control_points_matrix.append(row_points)

            # Cria a superfície bicúbica
            bicubic_surface = BezierSurface3D(control_points_matrix, color='orange', wireframe=True, name="Superfície Bicúbica")
            rotate_object(bicubic_surface, 30, 'x')  # Aplicar rotações padrão ou personalizadas
            self.objects.append(bicubic_surface)

            # Limpa a entrada após adicionar
            self.surface_entry.delete(0, tk.END)

        except Exception as e:
            tk.messagebox.showerror("Erro ao Adicionar Superfície", f"Erro: {e}")

    def add_bspline_surface(self):
        """Adds a bicubic B-spline surface with specified control points."""
        input_str = self.bspline_surface_entry.get()
        try:
            rows = input_str.strip().split(';')
            if len(rows) < 4:
                raise ValueError("A B-spline surface requires at least 4 rows of control points.")

            control_points_matrix = []
            for row_index, row in enumerate(rows):
                # Remove spaces and split the points
                points_str = row.strip().split('),(')
                # Remove possible '(' from the first point and ')' from the last point
                points_str[0] = points_str[0].lstrip('(')
                points_str[-1] = points_str[-1].rstrip(')')
                if len(points_str) < 4:
                    raise ValueError(f"Each row must contain at least 4 control points. Error in row {row_index + 1}.")

                row_points = []
                for point_str in points_str:
                    coords = point_str.split(',')
                    if len(coords) != 3:
                        raise ValueError(f"Invalid format for point: {point_str}")
                    x, y, z = map(float, coords)
                    row_points.append(Point3D(x, y, z))
                control_points_matrix.append(row_points)

            # Check if the matrix is rectangular
            num_columns = len(control_points_matrix[0])
            for row in control_points_matrix:
                if len(row) != num_columns:
                    raise ValueError("All rows must have the same number of control points.")

            # Create the B-spline surface
            bspline_surface = BSplineSurface3D(control_points_matrix, color='yellow', wireframe=True, name="Superfície B-spline")
            rotate_object(bspline_surface, 30, 'x')
            self.objects.append(bspline_surface)
            self.object_listbox.insert(tk.END, bspline_surface.name)
            self.bspline_surface_entry.delete(0, tk.END)

        except Exception as e:
            tk.messagebox.showerror("Erro ao Adicionar Superfície B-spline", f"Erro: {e}")

    def add_point(self):
        """Adiciona um ponto com as coordenadas especificadas."""
        coords = self.point_entry.get()
        try:
            x, y, z = map(float, coords.split(','))
            point = Point3D(x, y, z, color='green', name="Ponto")
            self.objects.append(point)
            self.point_entry.delete(0, tk.END)
        except ValueError:
            tk.messagebox.showerror("Erro ao Adicionar Ponto", "Entrada inválida para as coordenadas do ponto.\nFormato esperado: x,y,z")

    def add_line(self):
        """Adiciona uma linha entre dois pontos especificados."""
        coords = self.line_entry.get()
        try:
            points = coords.split('-')
            if len(points) != 2:
                raise ValueError("Formato inválido para a linha.\nFormato esperado: x1,y1,z1-x2,y2,z2")
            x1, y1, z1 = map(float, points[0].split(','))
            x2, y2, z2 = map(float, points[1].split(','))
            start = Point3D(x1, y1, z1)
            end = Point3D(x2, y2, z2)
            line = Line3D(start, end, color='red', name="Linha")
            self.objects.append(line)
            self.line_entry.delete(0, tk.END)
        except ValueError as e:
            tk.messagebox.showerror("Erro ao Adicionar Linha", f"Erro: {e}")

    def add_polygon(self):
        """Adiciona um polígono com os vértices especificados."""
        coords = self.polygon_entry.get()
        try:
            points_str = coords.split(';')
            if len(points_str) < 3:
                raise ValueError("Um polígono deve ter pelo menos 3 pontos.")
            vertices = []
            for point_str in points_str:
                x, y, z = map(float, point_str.split(','))
                vertices.append(Point3D(x, y, z))
            polygon = Polygon3D(vertices, color='purple', name="Polígono")
            self.objects.append(polygon)
            self.polygon_entry.delete(0, tk.END)
        except ValueError as e:
            tk.messagebox.showerror("Erro ao Adicionar Polígono", f"Erro: {e}")

    def add_bezier_curve(self):
        """Adiciona uma curva de Bézier com os pontos de controle especificados."""
        coords = self.curve_entry.get()
        try:
            points_str = coords.split(';')
            if len(points_str) < 2:
                raise ValueError("Uma curva de Bézier deve ter pelo menos 2 pontos de controle.")
            control_points = []
            for point_str in points_str:
                x, y, z = map(float, point_str.split(','))
                control_points.append(Point3D(x, y, z))
            bezier_curve = BezierCurve3D(control_points, color='orange', name="Curva de Bézier")
            self.objects.append(bezier_curve)
            self.curve_entry.delete(0, tk.END)
        except ValueError as e:
            tk.messagebox.showerror("Erro ao Adicionar Curva Bézier", f"Erro: {e}")

    def toggle_projection(self):
        if self.projection_type == 'perspective':
            self.projection_type = 'parallel'
            self.projection_button.config(text='Usar Projeção Perspectiva')
        else:
            self.projection_type = 'perspective'
            self.projection_button.config(text='Usar Projeção Paralela')

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self, event=None):
        """Aumenta o zoom (aproxima a cena)."""
        self.scale *= 1.1  # Aumenta o scale em 10%
        if self.scale >= 1000:
            self.scale = 1000

    def zoom_out(self, event=None):
        """Diminui o zoom (afasta a cena)."""
        self.scale /= 1.1  # Diminui o scale em 10%
        if self.scale <= 250:
            self.scale = 250

    def rotate_left(self, event=None):
        self.yaw -= 5  # Graus

    def rotate_right(self, event=None):
        self.yaw += 5  # Graus

    def rotate_up(self, event=None):
        self.pitch += 5  # Graus
        self.pitch = min(self.pitch, 89)  # Limita o pitch a 89 graus

    def rotate_down(self, event=None):
        self.pitch -= 5  # Graus
        self.pitch = max(self.pitch, -89)  # Limita o pitch a -89 graus

    def move_forward(self, event=None):
        direction = self.get_direction_vector()
        self.eye[0] += direction[0] * 0.5
        self.eye[1] += direction[1] * 0.5
        self.eye[2] += direction[2] * 0.5

    def move_backward(self, event=None):
        direction = self.get_direction_vector()
        self.eye[0] -= direction[0] * 0.5
        self.eye[1] -= direction[1] * 0.5
        self.eye[2] -= direction[2] * 0.5

    def move_left(self, event=None):
        direction = self.get_right_vector()
        self.eye[0] -= direction[0] * 0.5
        self.eye[1] -= direction[1] * 0.5
        self.eye[2] -= direction[2] * 0.5

    def move_right(self, event=None):
        direction = self.get_right_vector()
        self.eye[0] += direction[0] * 0.5
        self.eye[1] += direction[1] * 0.5
        self.eye[2] += direction[2] * 0.5

    def get_direction_vector(self):
        """Calcula o vetor de direção baseado em yaw e pitch."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        x = math.cos(pitch_rad) * math.sin(yaw_rad)
        y = math.sin(pitch_rad)
        z = math.cos(pitch_rad) * math.cos(yaw_rad)
        return [x, y, z]

    def get_right_vector(self):
        """Calcula o vetor à direita da câmera."""
        direction = self.get_direction_vector()
        up = self.up
        # Produto vetorial de direção e up
        right = [
            direction[1]*up[2] - direction[2]*up[1],
            direction[2]*up[0] - direction[0]*up[2],
            direction[0]*up[1] - direction[1]*up[0],
        ]
        # Normaliza o vetor
        length = math.sqrt(sum([coord ** 2 for coord in right]))
        if length == 0:
            return [0, 0, 0]
        right = [coord / length for coord in right]
        return right

    def get_view_matrix(self):
        """Calcula a matriz de visualização usando o método LookAt."""
        eye = self.eye
        direction = self.get_direction_vector()
        center = [eye[0] + direction[0], eye[1] + direction[1], eye[2] + direction[2]]
        up = self.up

        # Calcula os vetores da câmera
        f = self.normalize([center[i] - eye[i] for i in range(3)])  # Vetor para frente
        s = self.normalize(self.cross(f, up))  # Vetor para a direita
        u = self.cross(s, f)  # Vetor para cima ajustado

        # Matriz de visualização
        view_matrix = [
            [s[0], s[1], s[2], -self.dot(s, eye)],
            [u[0], u[1], u[2], -self.dot(u, eye)],
            [-f[0], -f[1], -f[2], self.dot(f, eye)],
            [0, 0, 0, 1]
        ]

        return view_matrix

    def normalize(self, v):
        length = math.sqrt(sum([coord ** 2 for coord in v]))
        if length == 0:
            return [0, 0, 0]
        return [coord / length for coord in v]

    def cross(self, a, b):
        return [
            a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]
        ]

    def dot(self, a, b):
        return sum([a[i]*b[i] for i in range(3)])

    def project_point(self, x, y, z):
        """Projeta um ponto 3D em 2D usando projeção em perspectiva ou paralela."""
        if self.projection_type == 'perspective':
            if z != 0:
                factor = self.scale / z
            else:
                factor = self.scale
            x = x * factor + self.center_x
            y = -y * factor + self.center_y
        elif self.projection_type == 'parallel':
            factor = self.scale * 0.05  # Ajuste este valor conforme necessário
            x = -x * factor + self.center_x
            y = y * factor + self.center_y
        return x, y


    def calculate_average_distance(self, obj):
        """Calcula a distância média dos vértices do objeto à câmera."""
        distances = []
        if isinstance(obj, Point3D):
            distances.append(self.distance(obj.tx, obj.ty, obj.tz))
        elif isinstance(obj, Line3D):
            distances.append(self.distance(obj.start.tx, obj.start.ty, obj.start.tz))
            distances.append(self.distance(obj.end.tx, obj.end.ty, obj.end.tz))
        elif isinstance(obj, Polygon3D) or isinstance(obj, Cube3D) or isinstance(obj, Cone3D):
            vertices = []
            if isinstance(obj, Polygon3D):
                vertices = obj.vertices
            elif isinstance(obj, Cube3D):
                vertices = obj.vertices
            elif isinstance(obj, Cone3D):
                vertices = [obj.apex, obj.base_center] + obj.base_vertices
            for vertex in vertices:
                distances.append(self.distance(vertex.tx, vertex.ty, vertex.tz))

        if distances:
            return sum(distances) / len(distances)
        else:
            return 0  # Se o objeto não tiver vértices, consideramos distância zero

    def distance(self, x, y, z):
        """Calcula a distância euclidiana do ponto (x, y, z) à câmera."""
        ex, ey, ez = self.eye
        return math.sqrt((x - ex) ** 2 + (y - ey) ** 2 + (z - ez) ** 2)

    def update(self):
        self.canvas.delete('all')

        # Desenha a margem da região de clipping
        x_min, y_min, x_max, y_max = self.clip_region
        self.canvas.create_rectangle(x_min, y_min, x_max, y_max, outline='black')

        view_matrix = self.get_view_matrix()

        # Ordena os objetos de maior para menor distância (objetos mais distantes primeiro)
        sorted_objects = sorted(self.objects, key=self.calculate_average_distance, reverse=True)

        for obj in sorted_objects:
            # Aplica a transformação (visualização) ao objeto
            obj.transform(view_matrix)
            # Aplica o clipping simples em Z
            if obj.is_visible():
                # Aplica a projeção ao objeto
                obj.project(self.project_point)
                # Desenha o objeto no canvas com o clipping 2D
                obj.draw(self.canvas, self.clip_region)

        # Atualiza a tela
        self.canvas.after(16, self.update)

    def export_obj_file(self):
        """Exporta todos os objetos da cena para um arquivo OBJ."""
        # Abre um diálogo para selecionar onde salvar o arquivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ files", "*.obj")],
            title="Exportar para OBJ"
        )
        if not file_path:
            return  # O usuário cancelou

        try:
            with open(file_path, 'w') as obj_file:
                obj_file.write("# Exportação de todos os objetos da cena\n")

                vertex_list = []
                vertex_indices = {}
                current_index = 1  # OBJ indices começam em 1

                # Primeiro, coleta todos os vértices
                for obj in self.objects:
                    if isinstance(obj, (Point3D, Line3D, Polygon3D, Cube3D, Cone3D, BezierSurface3D)):
                        vertices = []
                        if isinstance(obj, Point3D):
                            vertices = [obj]
                        elif isinstance(obj, Line3D):
                            vertices = [obj.start, obj.end]
                        elif isinstance(obj, Polygon3D):
                            vertices = obj.vertices
                        elif isinstance(obj, Cube3D):
                            vertices = obj.vertices
                        elif isinstance(obj, Cone3D):
                            vertices = [obj.apex, obj.base_center] + obj.base_vertices
                        elif isinstance(obj, BezierSurface3D):
                            for row in obj.control_points:
                                vertices.extend(row)
                        # Adiciona vértices únicos
                        for vertex in vertices:
                            key = (vertex.tx, vertex.ty, vertex.tz)
                            if key not in vertex_indices:
                                vertex_indices[key] = current_index
                                vertex_list.append(vertex)
                                current_index += 1

                # Escreve todos os vértices
                for vertex in vertex_list:
                    obj_file.write(f"v {vertex.tx} {vertex.ty} {vertex.tz}\n")

                # Agora, escreve cada objeto
                for obj in self.objects:
                    obj_name = obj.name if obj.name else "Objeto"
                    obj_file.write(f"\no {obj_name}\n")
                    if isinstance(obj, Point3D):
                        idx = vertex_indices[(obj.tx, obj.ty, obj.tz)]
                        # Ponto pode ser representado como uma linha com um único vértice
                        obj_file.write(f"p {idx}\n")
                    elif isinstance(obj, Line3D):
                        idx1 = vertex_indices[(obj.start.tx, obj.start.ty, obj.start.tz)]
                        idx2 = vertex_indices[(obj.end.tx, obj.end.ty, obj.end.tz)]
                        obj_file.write(f"l {idx1} {idx2}\n")
                    elif isinstance(obj, Polygon3D):
                        indices = [vertex_indices[(v.tx, v.ty, v.tz)] for v in obj.vertices]
                        face_line = " ".join(map(str, indices))
                        obj_file.write(f"f {face_line}\n")
                    elif isinstance(obj, Cube3D):
                        for face in obj.faces:
                            indices = [vertex_indices[(v.tx, v.ty, v.tz)] for v in face.vertices]
                            face_line = " ".join(map(str, indices))
                            obj_file.write(f"f {face_line}\n")
                    elif isinstance(obj, Cone3D):
                        for face in obj.faces:
                            indices = [vertex_indices[(v.tx, v.ty, v.tz)] for v in face.vertices]
                            face_line = " ".join(map(str, indices))
                            obj_file.write(f"f {face_line}\n")
                        # Base do cone
                        base_indices = [vertex_indices[(v.tx, v.ty, v.tz)] for v in obj.base_face.vertices]
                        base_face_line = " ".join(map(str, base_indices))
                        obj_file.write(f"f {base_face_line}\n")
                    elif isinstance(obj, BezierSurface3D):
                        # Exportar superfícies bicúbicas de Bézier pode ser complexo.
                        # Para simplicidade, ignoraremos neste exemplo.
                        pass
                    else:
                        # Outros tipos de objetos podem ser tratados aqui
                        pass

            messagebox.showinfo("Exportação concluída", f"Objetos exportados para {file_path}")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Ocorreu um erro ao exportar os objetos:\n{e}")

    def import_obj_file(self):
        """Importa objetos de um arquivo OBJ e adiciona à cena."""
        # Abre um diálogo para selecionar o arquivo OBJ
        file_path = filedialog.askopenfilename(
            filetypes=[("OBJ files", "*.obj")],
            title="Importar OBJ"
        )
        if not file_path:
            return  # O usuário cancelou

        try:
            with open(file_path, 'r') as obj_file:
                vertices = []
                current_object = None
                current_object_name = "Objeto_importado"
                lines = obj_file.readlines()

                for line in lines:
                    if line.startswith('#') or line.strip() == '':
                        continue  # Ignora comentários e linhas vazias
                    parts = line.strip().split()
                    if not parts:
                        continue
                    if parts[0] == 'o':
                        # Novo objeto
                        if current_object:
                            self.objects.append(current_object)
                        current_object_name = ' '.join(parts[1:]) if len(parts) > 1 else "Objeto_importado"
                        current_object = None
                    elif parts[0] == 'v':
                        # Vértice
                        x, y, z = map(float, parts[1:4])
                        vertices.append(Point3D(x, y, z))
                    elif parts[0] == 'p':
                        # Ponto
                        idx = int(parts[1]) - 1  # OBJ indices começam em 1
                        if 0 <= idx < len(vertices):
                            p = vertices[idx]
                            if current_object is None:
                                current_object = Point3D(p.x, p.y, p.z, color='green', name=current_object_name)
                            else:
                                # Adiciona mais pontos ao objeto existente, se necessário
                                pass  # Pode implementar múltiplos pontos em um objeto
                    elif parts[0] == 'l':
                        # Linha
                        indices = [int(idx) - 1 for idx in parts[1:]]
                        if len(indices) >= 2:
                            start = vertices[indices[0]]
                            end = vertices[indices[1]]
                            line_obj = Line3D(Point3D(start.x, start.y, start.z, color='red'), 
                                              Point3D(end.x, end.y, end.z, color='red'),
                                              color='red',
                                              name=current_object_name)
                            self.objects.append(line_obj)
                    elif parts[0] == 'f':
                        # Face
                        face_indices = []
                        for part in parts[1:]:
                            idx = part.split('/')[0]  # Ignora textura e normais
                            face_indices.append(int(idx) - 1)
                        face_vertices = [vertices[idx] for idx in face_indices]
                        polygon = Polygon3D([Point3D(v.x, v.y, v.z) for v in face_vertices],
                                            color='purple',
                                            fill_color=None,  # Não preenche por padrão
                                            name=current_object_name)
                        self.objects.append(polygon)
                    # Outros comandos como 'vn', 'vt' podem ser adicionados aqui se necessário

                # Adiciona o último objeto, se existir
                if current_object:
                    self.objects.append(current_object)

            # Atualiza a lista de objetos na interface
            self.object_listbox.delete(0, tk.END)
            for obj in self.objects:
                self.object_listbox.insert(tk.END, obj.name)

            messagebox.showinfo("Importação concluída", f"Objetos importados de {file_path}")
        except Exception as e:
            messagebox.showerror("Erro na Importação", f"Ocorreu um erro ao importar o arquivo OBJ:\n{e}")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    window = Window()
    window.run()
