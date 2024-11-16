import numpy as np


class Window:

    INITIAL_ANGLE = 0.0
    INITIAL_OFFSET = np.array([0, 0, 0], dtype=np.float64)
    INITIAL_ZOOM_FACTOR = 1.0
    INITIAL_VPN = np.array([0, 0, 1], dtype=np.float64)  # Direção inicial do VPN

    MAX_ZOOM = 4.0
    MIN_ZOOM = 0.1

    def __init__(self):
        self.initial_width = 200.0
        self.initial_height = 200.0
        self.width = self.initial_width
        self.height = self.initial_height

        self.zoom_factor = Window.INITIAL_ZOOM_FACTOR
        self.offset = np.array(Window.INITIAL_OFFSET, dtype=np.float64)
        self.vpn = Window.INITIAL_VPN.copy()  # Define o vetor de visão inicial
        self.vpr = np.array([1, 0, 0], dtype=np.float64)
        self.vpu = np.array([0, 1, 0], dtype=np.float64)

    def get_bounds(self):
        return np.array([self.offset[0] - 1, self.offset[0] + 1, self.offset[1] - 1, self.offset[1] + 1], dtype=np.float64)

    def get_offset(self):
        return self.offset
    
    def increase_offset(self, offset):
        self.offset += np.array(offset, dtype=np.float64)

    def set_zoom(self, factor):
        if factor >= Window.MAX_ZOOM:
            factor = Window.MAX_ZOOM

        if factor <= Window.MIN_ZOOM:
            factor = Window.MIN_ZOOM

        self.zoom_factor = factor
        self.width = self.initial_width* factor
        self.height = self.initial_height * factor

    def zoom_in(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor - selected_zoom_factor/100)

    def zoom_out(self, selected_zoom_factor):
        self.set_zoom(self.zoom_factor + selected_zoom_factor/100)

    def move_up(self):
        offset = self.vpu * 5
        self.increase_offset(offset)

    def move_down(self):
        offset = -self.vpu * 5
        self.increase_offset(offset)

    def move_left(self):
        offset = -self.vpr * 5
        self.increase_offset(offset)

    def move_right(self):
        offset = self.vpr * 5
        self.increase_offset(offset)

    def move_forward(self):
        offset = -self.vpn * 5
        self.increase_offset(offset)

    def move_backward(self):
        offset = self.vpn * 5
        self.increase_offset(offset)

    def rotate(self, v, angle, axis):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        ux, uy, uz = axis
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        one_minus_cos = 1 - cos_angle

        rotation_matrix = np.array([
            [cos_angle + ux**2 * one_minus_cos, ux * uy * one_minus_cos - uz * sin_angle, ux * uz * one_minus_cos + uy * sin_angle],
            [uy * ux * one_minus_cos + uz * sin_angle, cos_angle + uy**2 * one_minus_cos, uy * uz * one_minus_cos - ux * sin_angle],
            [uz * ux * one_minus_cos - uy * sin_angle, uz * uy * one_minus_cos + ux * sin_angle, cos_angle + uz**2 * one_minus_cos]
        ], dtype=np.float64)

        return rotation_matrix @ v
    
    def rotate_right(self, angle):
        self.vpn = self.rotate(self.vpn, angle, self.vpu)
        self.vpr = self.rotate(self.vpr, angle, self.vpu)

    def rotate_left(self, angle):
        self.vpn = self.rotate(self.vpn, -angle, self.vpu)
        self.vpr = self.rotate(self.vpr, -angle, self.vpu)

    def rotate_up(self, angle):
        self.vpn = self.rotate(self.vpn, angle, self.vpr)
        self.vpu = self.rotate(self.vpu, angle, self.vpr)

    def rotate_down(self, angle):
        self.vpn = self.rotate(self.vpn, -angle, self.vpr)
        self.vpu = self.rotate(self.vpu, -angle, self.vpr)

    def rotate_clockwise(self, angle):
        self.vpr = self.rotate(self.vpr, angle, self.vpn)
        self.vpu = self.rotate(self.vpu, angle, self.vpn)

    def rotate_counterclockwise(self, angle):
        self.vpr = self.rotate(self.vpr, -angle, self.vpn)
        self.vpu = self.rotate(self.vpu, -angle, self.vpn)

    def get_vpn_angles(self):
        vpn_norm = self.vpn / np.linalg.norm(self.vpn)
        theta_x = np.arctan2(vpn_norm[1], vpn_norm[2])
        theta_y = np.arctan2(vpn_norm[0], np.sqrt(vpn_norm[1]**2 + vpn_norm[2]**2))

        return theta_x, theta_y

    def set_aspect_ratio(self, aspect_ratio):
        self.initial_width = aspect_ratio[0]
        self.initial_height = aspect_ratio[1]

        self.width = aspect_ratio[0]
        self.height = aspect_ratio[1]
    
    def reset(self):
        self.initial_width = 200.0
        self.initial_height = 200.0
        self.width = self.initial_width
        self.height = self.initial_height

        self.zoom_factor = Window.INITIAL_ZOOM_FACTOR
        self.offset = Window.INITIAL_OFFSET
        self.angle = Window.INITIAL_ANGLE
    