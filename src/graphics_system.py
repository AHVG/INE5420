import tkinter as tk
import math

class Object3D:
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
    def __init__(self, x, y, z, color='green'):
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

    def project(self, project_func):
        self.screen_x, self.screen_y = project_func(self.tx, self.ty, self.tz)

    def draw(self, canvas, clip_region):
        x_min, y_min, x_max, y_max = clip_region
        x, y = self.screen_x, self.screen_y
        # Clipping para pontos: verificar se o ponto está dentro da região
        if x_min <= x <= x_max and y_min <= y <= y_max:
            canvas.create_oval(x-3, y-3, x+3, y+3, fill=self.color)

class Line3D(Object3D):
    """Classe para representar uma reta (segmento de linha) em 3D."""
    def __init__(self, start_point, end_point, color='red'):
        self.start = start_point  # Ponto inicial (Point3D)
        self.end = end_point      # Ponto final (Point3D)
        self.color = color

    def transform(self, view_matrix):
        self.start.transform(view_matrix)
        self.end.transform(view_matrix)

    def project(self, project_func):
        self.start.project(project_func)
        self.end.project(project_func)

    def draw(self, canvas, clip_region):
        x1, y1 = self.start.screen_x, self.start.screen_y
        x2, y2 = self.end.screen_x, self.end.screen_y
        # Aplicar o clipping usando o algoritmo Cohen-Sutherland
        clipped_line = cohen_sutherland_clip(x1, y1, x2, y2, clip_region)
        if clipped_line:
            x1_clipped, y1_clipped, x2_clipped, y2_clipped = clipped_line
            canvas.create_line(x1_clipped, y1_clipped, x2_clipped, y2_clipped, fill=self.color)

class BezierCurve3D(Object3D):
    """Classe para representar uma curva de Bézier em 3D."""
    def __init__(self, control_points, color='orange'):
        self.control_points = control_points  # Lista de objetos Point3D
        self.curve_points = []  # Pontos da curva após a avaliação
        self.color = color

    def transform(self, view_matrix):
        for point in self.control_points:
            point.transform(view_matrix)

    def project(self, project_func):
        # Avalia a curva de Bézier e projeta os pontos
        self.curve_points = []
        n = len(self.control_points) - 1
        steps = 100  # Número de segmentos da curva
        for i in range(steps + 1):
            t = i / steps
            x, y, z = self.de_casteljau(t)
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
            # Clipping para cada segmento da curva
            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
            if clipped_line:
                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)

class BSplineCurve3D(Object3D):
    """Classe para representar uma curva B-spline em 3D."""
    def __init__(self, control_points, degree=3, color='brown'):
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
            # Clipping para cada segmento da curva
            clipped_line = cohen_sutherland_clip(x0, y0, x1, y1, clip_region)
            if clipped_line:
                x0_clipped, y0_clipped, x1_clipped, y1_clipped = clipped_line
                canvas.create_line(x0_clipped, y0_clipped, x1_clipped, y1_clipped, fill=self.color)

class Polygon3D(Object3D):
    """Classe para representar um polígono em 3D."""
    def __init__(self, vertices, color='purple', fill_color=None):
        self.vertices = vertices  # Lista de objetos Point3D
        self.color = color
        self.fill_color = fill_color  # Pode ser None ou uma string de cor

    def transform(self, view_matrix):
        for vertex in self.vertices:
            vertex.transform(view_matrix)

    def project(self, project_func):
        for vertex in self.vertices:
            vertex.project(project_func)

    def draw(self, canvas, clip_region):
        # Coleta as coordenadas projetadas dos vértices
        points = []
        for vertex in self.vertices:
            x, y = vertex.screen_x, vertex.screen_y
            points.append((x, y))

        # Aplicar o algoritmo de clipping de Sutherland-Hodgman
        clipped_polygon = sutherland_hodgman_clip(points, clip_region)
        if clipped_polygon:
            # Converte a lista de pontos em uma lista plana de coordenadas
            flat_points = [coord for point in clipped_polygon for coord in point]
            if self.fill_color:
                canvas.create_polygon(flat_points, fill=self.fill_color, outline=self.color)
            else:
                # Desenha apenas as arestas do polígono sem preenchimento
                canvas.create_line(flat_points + flat_points[:2], fill=self.color)

class Cone3D(Object3D):
    """Classe para representar um cone em 3D."""
    def __init__(self, base_center, height, radius, segments=20, color='magenta', fill_color='pink'):
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
    def __init__(self, center, size, color='blue'):
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
        # Define as 12 arestas que conectam os vértices
        self.edges = [
            Line3D(self.vertices[0], self.vertices[1], self.color),
            Line3D(self.vertices[0], self.vertices[2], self.color),
            Line3D(self.vertices[0], self.vertices[4], self.color),
            Line3D(self.vertices[1], self.vertices[3], self.color),
            Line3D(self.vertices[1], self.vertices[5], self.color),
            Line3D(self.vertices[2], self.vertices[3], self.color),
            Line3D(self.vertices[2], self.vertices[6], self.color),
            Line3D(self.vertices[3], self.vertices[7], self.color),
            Line3D(self.vertices[4], self.vertices[5], self.color),
            Line3D(self.vertices[4], self.vertices[6], self.color),
            Line3D(self.vertices[5], self.vertices[7], self.color),
            Line3D(self.vertices[6], self.vertices[7], self.color),
        ]

    def transform(self, view_matrix):
        for vertex in self.vertices:
            vertex.transform(view_matrix)

    def project(self, project_func):
        for vertex in self.vertices:
            vertex.project(project_func)

    def draw(self, canvas, clip_region):
        for edge in self.edges:
            edge.draw(canvas, clip_region)
        # Opcional: desenhar os vértices do cubo
        for vertex in self.vertices:
            vertex.draw(canvas, clip_region)

class Window:
    def __init__(self, width=800, height=600, title="Sistema Gráfico 3D"):
        self.width = width
        self.height = height
        self.title = title

        # Configurações da janela
        self.root = tk.Tk()
        self.root.title(self.title)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='white')
        self.canvas.pack()

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

        # Posição e orientação do observador
        self.eye = [0, 0, -10]  # Posição da câmera
        self.up = [0, 1, 0]  # Vetor "para cima"

        # Ângulos de rotação para ajustar o vetor look_at
        self.yaw = 0  # Rotação em torno do eixo Y
        self.pitch = 0  # Rotação em torno do eixo X

        # Lista de objetos 3D
        self.objects = []

        # Inicializa os objetos 3D
        self.create_objects()

        # Liga os eventos de teclado e mouse
        self.canvas.bind('<Left>', self.rotate_left)
        self.canvas.bind('<Right>', self.rotate_right)
        self.canvas.bind('<Up>', self.rotate_up)
        self.canvas.bind('<Down>', self.rotate_down)
        self.canvas.bind('<w>', self.move_forward)
        self.canvas.bind('<s>', self.move_backward)
        self.canvas.bind('<a>', self.move_left)
        self.canvas.bind('<d>', self.move_right)
        self.canvas.focus_set()

        # Inicia o loop de atualização
        self.update()

    def create_objects(self):
        # Cubo no Octante 1 (x > 0, y > 0, z > 0)
        cube = Cube3D(Point3D(2, 2, 2), 2, color='blue')
        self.objects.append(cube)

        # Ponto no Octante 2 (x < 0, y > 0, z > 0)
        point = Point3D(-2, 2, 2, color='green')
        self.objects.append(point)

        # Reta no Octante 3 (x < 0, y < 0, z > 0)
        line = Line3D(Point3D(-2, -2, 2), Point3D(-1, -1, 2), color='red')
        self.objects.append(line)

        # Polígono no Octante 4 (x > 0, y < 0, z > 0) sem preenchimento
        vertices = [
            Point3D(1, -1, 2),
            Point3D(2, -2, 2),
            Point3D(3, -1, 2),
            Point3D(2, -0.5, 2)
        ]
        polygon = Polygon3D(vertices, color='purple')  # fill_color não especificado
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
        bezier_curve = BezierCurve3D(bezier_control_points, color='orange')
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
        bspline_curve = BSplineCurve3D(bspline_control_points, degree=3, color='brown')
        self.objects.append(bspline_curve)

        # Cone no Octante 7 (x < 0, y < 0, z < 0)
        cone = Cone3D(
            base_center=Point3D(-2, -2, -2),
            height=3,
            radius=1,
            segments=20,
            color='magenta',
            fill_color='pink'
        )
        self.objects.append(cone)

    def rotate_left(self, event):
        self.yaw -= 5  # Graus

    def rotate_right(self, event):
        self.yaw += 5  # Graus

    def rotate_up(self, event):
        self.pitch += 5  # Graus
        self.pitch = min(self.pitch, 89)  # Limita o pitch a 89 graus

    def rotate_down(self, event):
        self.pitch -= 5  # Graus
        self.pitch = max(self.pitch, -89)  # Limita o pitch a -89 graus

    def move_forward(self, event):
        direction = self.get_direction_vector()
        self.eye[0] += direction[0] * 0.5
        self.eye[1] += direction[1] * 0.5
        self.eye[2] += direction[2] * 0.5

    def move_backward(self, event):
        direction = self.get_direction_vector()
        self.eye[0] -= direction[0] * 0.5
        self.eye[1] -= direction[1] * 0.5
        self.eye[2] -= direction[2] * 0.5

    def move_left(self, event):
        direction = self.get_right_vector()
        self.eye[0] -= direction[0] * 0.5
        self.eye[1] -= direction[1] * 0.5
        self.eye[2] -= direction[2] * 0.5

    def move_right(self, event):
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
        """Projeta um ponto 3D em 2D usando projeção em perspectiva."""
        if z != 0:
            factor = self.scale / z
        else:
            factor = self.scale
        x = x * factor + self.center_x
        y = -y * factor + self.center_y  # Inverte o eixo Y para corresponder às coordenadas da tela
        return x, y

    def update(self):
        self.canvas.delete('all')

        # Desenha a margem da região de clipping
        x_min, y_min, x_max, y_max = self.clip_region
        self.canvas.create_rectangle(x_min, y_min, x_max, y_max, outline='black')

        view_matrix = self.get_view_matrix()

        for obj in self.objects:
            # Aplica a transformação (visualização) ao objeto
            obj.transform(view_matrix)
            # Aplica a projeção ao objeto
            obj.project(self.project_point)
            # Desenha o objeto no canvas com o clipping
            obj.draw(self.canvas, self.clip_region)

        # Atualiza a tela
        self.canvas.after(16, self.update)

    def run(self):
        self.root.mainloop()

# Funções de clipping

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

if __name__ == '__main__':
    window = Window()
    window.run()
