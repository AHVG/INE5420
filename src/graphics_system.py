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

    def draw(self, canvas):
        """Desenha o objeto no canvas."""
        pass

class Point3D(Object3D):
    """Classe para representar um ponto em 3D."""
    def __init__(self, x, y, z, color='green'):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.tx = self.x
        self.ty = self.y
        self.tz = self.z

    def transform(self, view_matrix):
        x, y, z = self.x, self.y, self.z
        self.tx = view_matrix[0][0]*x + view_matrix[0][1]*y + view_matrix[0][2]*z + view_matrix[0][3]
        self.ty = view_matrix[1][0]*x + view_matrix[1][1]*y + view_matrix[1][2]*z + view_matrix[1][3]
        self.tz = view_matrix[2][0]*x + view_matrix[2][1]*y + view_matrix[2][2]*z + view_matrix[2][3]

    def project(self, project_func):
        self.screen_x, self.screen_y = project_func(self.tx, self.ty, self.tz)

    def draw(self, canvas):
        x, y = self.screen_x, self.screen_y
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

    def draw(self, canvas):
        x1, y1 = self.start.screen_x, self.start.screen_y
        x2, y2 = self.end.screen_x, self.end.screen_y
        canvas.create_line(x1, y1, x2, y2, fill=self.color)

class Cube3D(Object3D):
    """Classe para representar um cubo em 3D."""
    def __init__(self, center, size, color='blue'):
        d = size / 2
        x, y, z = center.x, center.y, center.z
        self.color = color
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

    def draw(self, canvas):
        for edge in self.edges:
            edge.draw(canvas)
        for vertex in self.vertices:
            vertex.draw(canvas)

class Window:
    def __init__(self, width=800, height=600, title="Sistema Gráfico 3D com Perspectiva"):
        self.width = width
        self.height = height
        self.title = title

        # Configurações da janela
        self.root = tk.Tk()
        self.root.title(self.title)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='white')
        self.canvas.pack()

        # Centro da tela
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Parâmetros de projeção
        self.scale = 500  # Controle de zoom
        self.projection_distance = 1  # Distância de projeção para perspectiva

        self.eye = [0, 0, -5]  # Posição da câmera
        self.look_at = [0, 0, 0]  # Ponto para onde a câmera está olhando
        self.up = [0, 1, 0]  # Vetor "para cima"

        self.yaw = 0  # Rotação em torno do eixo Y
        self.pitch = 0  # Rotação em torno do eixo X

        self.objects = []

        self.create_objects()

        self.canvas.bind('<Left>', self.rotate_left)
        self.canvas.bind('<Right>', self.rotate_right)
        self.canvas.bind('<Up>', self.rotate_up)
        self.canvas.bind('<Down>', self.rotate_down)
        self.canvas.bind('<w>', self.move_forward)
        self.canvas.bind('<s>', self.move_backward)
        self.canvas.bind('<a>', self.move_left)
        self.canvas.bind('<d>', self.move_right)
        self.canvas.focus_set()

        self.update()

    def create_objects(self):
        cube = Cube3D(Point3D(0, 0, 0), 2, color='blue')
        self.objects.append(cube)

        point = Point3D(1, 1, 1, color='green')
        self.objects.append(point)

        line = Line3D(Point3D(-1, -1, -1), Point3D(1, 1, 1), color='red')
        self.objects.append(line)

    def rotate_left(self, event):
        self.yaw -= 5

    def rotate_right(self, event):
        self.yaw += 5

    def rotate_up(self, event):
        self.pitch += 5

    def rotate_down(self, event):
        self.pitch -= 5

    def move_forward(self, event):
        direction = self.get_direction_vector()
        self.eye[0] += direction[0] * 0.1
        self.eye[1] += direction[1] * 0.1
        self.eye[2] += direction[2] * 0.1

    def move_backward(self, event):
        direction = self.get_direction_vector()
        self.eye[0] -= direction[0] * 0.1
        self.eye[1] -= direction[1] * 0.1
        self.eye[2] -= direction[2] * 0.1

    def move_left(self, event):
        direction = self.get_right_vector()
        self.eye[0] -= direction[0] * 0.1
        self.eye[1] -= direction[1] * 0.1
        self.eye[2] -= direction[2] * 0.1

    def move_right(self, event):
        direction = self.get_right_vector()
        self.eye[0] += direction[0] * 0.1
        self.eye[1] += direction[1] * 0.1
        self.eye[2] += direction[2] * 0.1

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
        right = [
            direction[1]*up[2] - direction[2]*up[1],
            direction[2]*up[0] - direction[0]*up[2],
            direction[0]*up[1] - direction[1]*up[0],
        ]
        length = math.sqrt(sum([coord ** 2 for coord in right]))
        right = [coord / length for coord in right]
        return right

    def get_view_matrix(self):
        """Calcula a matriz de visualização usando o método LookAt."""
        eye = self.eye
        direction = self.get_direction_vector()
        center = [eye[0] + direction[0], eye[1] + direction[1], eye[2] + direction[2]]
        up = self.up

        f = self.normalize([center[i] - eye[i] for i in range(3)])
        s = self.normalize(self.cross(f, up))
        u = self.cross(s, f)

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

        view_matrix = self.get_view_matrix()

        for obj in self.objects:
            # Aplica a transformação (visualização) ao objeto
            obj.transform(view_matrix)
            # Aplica a projeção ao objeto
            obj.project(self.project_point)
            # Desenha o objeto no canvas
            obj.draw(self.canvas)

        # Atualiza a tela
        self.canvas.after(16, self.update)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    window = Window()
    window.run()
