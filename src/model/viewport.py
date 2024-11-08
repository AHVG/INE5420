from model.transformation import Transformation3D
import numpy as np

class Viewport:

    def __init__(self, window):
        self.window = window
        self.line_clipping_method = 'liang-barsky'

    def transform(self, drawable):
        drawable = drawable.copy()

        # Substitua a linha de baixo pelo algoritmo dele (o mundo é cada um dos drawables)
        # drawable = Transformation3D(drawable).rotation_relative_to_axis(\
        #            self.window.get_angle_vpu_to_yz(), [0, 0, 1], self.window.get_offset()).escalation_relative_to_a_point(\
        #            [1/(self.window.width/2), 1/(self.window.height/2), 1], self.window.get_offset()).apply()

        print(drawable.points)

        transformation = Transformation3D(drawable)
        vrp_offset = self.window.get_offset()
        transformation = transformation.translation(-vrp_offset)

        # Passo 2: Determine os ângulos entre o VPN e os eixos X e Y
        angle_vpn_x, angle_vpn_y = self.window.get_vpn_angles()
        print(angle_vpn_x)
        print(angle_vpn_y)
        transformation = transformation.rotation_relative_to_axis(-angle_vpn_x, [1, 0, 0])  # Rotação em torno do X
        transformation = transformation.rotation_relative_to_axis(-angle_vpn_y, [0, 1, 0])  # Rotação em torno do Y
        transformation = transformation.escalation_relative_to_a_point([1/(self.window.width/2), 1/(self.window.height/2), 1], self.window.get_offset())

        drawable = transformation.apply()
        
        print(drawable.points)

        drawable = drawable.clip((self.window.get_bounds()[0] + 1/15, self.window.get_bounds()[2] + 1/15, self.window.get_bounds()[1] - 1/15, self.window.get_bounds()[3] - 1/15))

        if not drawable:
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