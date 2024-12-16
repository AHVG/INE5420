import numpy as np
import math

from clipping import *


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