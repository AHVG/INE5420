import numpy as np

def rotate_vector(v, u, angle):
    # Normaliza os vetores de entrada
    angle = angle * np.pi / 180
    v = v / np.linalg.norm(v)
    u = u / np.linalg.norm(u)

    # Calcula o vetor normal ao plano definido por v e u
    n = np.cross(v, u)
    n = n / np.linalg.norm(n)  # Normaliza o vetor normal

    # Calcula a projeção de u no plano de v, mantendo apenas o componente perpendicular a n
    u_in_plane = u - np.dot(u, n) * n
    u_in_plane = u_in_plane / np.linalg.norm(u_in_plane)  # Normaliza u no plano

    # Usa o cosseno e seno para rotacionar v em direção a u no plano
    v_rotated = np.cos(angle) * v + np.sin(angle) * u_in_plane

    # Remove pequenas componentes residuais fora do plano (precisão numérica)
    v_rotated -= np.dot(v_rotated, n) * n

    return v_rotated

class Window:

    INITIAL_OFFSET = np.array([0, 0, 0], dtype=np.float64)
    INITIAL_ZOOM_FACTOR = 1.0

    MAX_ZOOM = 4.0
    MIN_ZOOM = 0.1

    def __init__(self):
        self.initial_width = 200.0
        self.initial_height = 200.0
        self.initial_depth = 600.0
        self.width = self.initial_width
        self.height = self.initial_height
        self.depth = self.initial_depth
        self.angle = 0.0
        self.zoom_factor = Window.INITIAL_ZOOM_FACTOR
        self.offset = np.array(Window.INITIAL_OFFSET, dtype=np.float64)
        self.vpn = np.array([0, 0, 1], dtype=np.float64)  # Vetor normal (view plane normal)
        self.v_right = np.array([1, 0, 0], dtype=np.float64)  # Vetor para a direita
        self.v_up = np.array([0, 1, 0], dtype=np.float64)  # Vetor para cima

    def get_bounds(self):
        return np.array([self.offset[0] - 1, self.offset[0] + 1, self.offset[1] - 1, self.offset[1] + 1, self.offset[2] - 1, self.offset[2] + 1], dtype=np.float64)

    def get_offset(self):
        return self.offset

    def increase_offset(self, delta):
        """
        Move o centro da janela e atualiza os vetores de orientação.
        """
        self.offset += np.array(delta, dtype=np.float64)
        self.update_orientation_vectors()

    def set_zoom(self, factor):
        if factor >= Window.MAX_ZOOM:
            factor = Window.MAX_ZOOM

        if factor <= Window.MIN_ZOOM:
            factor = Window.MIN_ZOOM

        self.zoom_factor = factor
        self.width = self.initial_width * factor
        self.height = self.initial_height * factor

    def zoom_in(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor - selected_zoom_factor / 100)

    def zoom_out(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor + selected_zoom_factor / 100)

    def move_up(self):
        mod = 0.01 * self.height
        delta = mod * self.v_up
        self.increase_offset(delta)

    def move_down(self):
        mod = -0.01 * self.height
        delta = mod * self.v_up
        self.increase_offset(delta)

    def move_left(self):
        mod = -0.01 * self.width
        delta = mod * self.v_right
        self.increase_offset(delta)

    def move_right(self):
        mod = 0.01 * self.width
        delta = mod * self.v_right
        self.increase_offset(delta)

    def move_forward(self):
        mod = 0.01 * self.depth
        delta = mod * self.vpn
        self.increase_offset(delta)

    def move_backward(self):
        mod = -0.01 * self.depth
        delta = mod * self.vpn
        self.increase_offset(delta)

    def normalize_orientation_vectors(self):
        """
        Recalcula os vetores de orientação para garantir a ortonormalidade.
        """
        self.vpn = self.vpn / np.linalg.norm(self.vpn)
        self.v_right = np.cross(self.v_up, self.vpn)
        self.v_right = self.v_right / np.linalg.norm(self.v_right)
        self.v_up = np.cross(self.vpn, self.v_right)
        self.v_up = self.v_up / np.linalg.norm(self.v_up)
        print(self.vpn)
        print(self.v_right)
        print(self.v_up)
        print(self.offset)

    def increase_angle(self, angle):
        """
        Rotaciona a janela em torno do eixo v_right (pitch).
        """
        self.angle += angle
        self.v_up = rotate_vector(self.v_up, self.v_right, angle)
        self.normalize_orientation_vectors()

    def set_aspect_ratio(self, aspect_ratio):
        self.initial_width = aspect_ratio[0]
        self.initial_height = aspect_ratio[1]
        self.initial_depth = aspect_ratio[2] if len(aspect_ratio) > 2 else self.initial_depth

        self.width = self.initial_width
        self.height = self.initial_height
        self.depth = self.initial_depth

    def reset(self):
        self.__init__()

    def update_orientation_vectors(self):
        """
        Atualiza os vetores de orientação após um movimento, considerando o novo centro.
        Esse método pode ser expandido para incluir outras atualizações, caso necessário.
        """

        self.normalize_orientation_vectors()
