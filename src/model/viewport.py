from model.transformation import Transformation3D
import numpy as np

class Viewport:

    def __init__(self, window):
        self.window = window
        self.line_clipping_method = 'liang-barsky'

    def transform(self, drawable):
        drawable = drawable.copy()

        cop = self.window.get_cop()
        offset = self.window.get_offset() - np.array(cop)
        transformation = Transformation3D(drawable)
        transformation.translation(-(offset))

        def calculate_angle(vpn, axis):
            """
            Calcula o ângulo entre o vetor normal (VPN) e um eixo dado (X ou Y).

            Args:
            - vpn: Vetor normal (lista ou numpy array).
            - axis: Vetor do eixo (lista ou numpy array), por exemplo, [1, 0, 0] para o eixo X.

            Returns:
            - Ângulo em radianos entre o vetor normal e o eixo fornecido.
            """
            # Converter para numpy arrays
            vpn = np.array(vpn)
            axis = np.array(axis)

            # Normalizar os vetores
            vpn_norm = vpn / np.linalg.norm(vpn)
            axis_norm = axis / np.linalg.norm(axis)

            # Calcular o ângulo usando arctan2
            cross_product = np.cross(vpn_norm, axis_norm)  # Produto vetorial
            dot_product = np.dot(vpn_norm, axis_norm)      # Produto escalar

            theta = np.arctan2(np.linalg.norm(cross_product), dot_product)  # Ângulo em radianos

            return theta

        # Exemplo de uso:
        vpn = self.window.vpn
        axis_x = [1, 0, 0]  # Vetor do eixo X
        axis_y = [0, 1, 0]  # Vetor do eixo Y

        angle_vpn_x = calculate_angle(vpn, axis_x)
        angle_vpn_y = calculate_angle(vpn, axis_y)
        
        
        print()
        print("angle vpn x: ", np.degrees(angle_vpn_x))
        print("angle vpn y: ", np.degrees(angle_vpn_y))
        
        # angle_vpn_x = np.arctan2(vpn[1], vpn[2])
        # angle_vpn_y = np.arctan2(vpn[0], vpn[2])

        transformation.rotation_relative_to_axis(angle_vpn_y - np.pi / 2, [1, 0, 0], self.window.get_cop())
        transformation.rotation_relative_to_axis(angle_vpn_x - np.pi / 2, [0, 1, 0], self.window.get_cop())
        transformation = transformation.escalation_relative_to_a_point([1/(self.window.width/2), 1/(self.window.height/2), 1], self.window.get_cop())

        drawable = transformation.apply()

        def perspective_projection(point):
            d = -cop[2]
            x_p = (d * point[0]) / (d + point[2])
            y_p = (d * point[1]) / (d + point[2])
            return [x_p, y_p, point[2]]

        points = np.array([perspective_projection(p) for p in drawable.points])
        drawable = drawable.copy(points=points)

        # drawable = drawable.clip((self.window.get_bounds()[0] + 1/15, self.window.get_bounds()[2] + 1/15, self.window.get_bounds()[1] - 1/15, self.window.get_bounds()[3] - 1/15))

        if not drawable or Transformation3D(drawable).get_center(drawable)[2] <= cop[2]:
            return None

        def transform(drawable, window, viewport):
            points = []
            for point in drawable.points:
                window_bounds = window.get_bounds()
                x_viewport = ((point[0] - window_bounds[0]) / (window_bounds[1] - window_bounds[0])) * (viewport.bounds[1] - viewport.bounds[0])
                y_viewport = (1 - (point[1] - window_bounds[2]) / (window_bounds[3] - window_bounds[2])) * (viewport.bounds[3] - viewport.bounds[2])
                points.append([x_viewport, y_viewport])        

            return drawable.copy(points=points)

        drawable = transform(drawable, self.window, self)

        return drawable

    def set_window(self, window):
        self.window = window
    
    def set_aspect_ratio(self, aspect_ratio):
        self.width = aspect_ratio[0]
        self.height = aspect_ratio[1]
        self.bounds = (0, self.width, 0, self.height)