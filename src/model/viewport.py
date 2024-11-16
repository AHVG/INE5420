from model.transformation import Transformation3D
import numpy as np

class Viewport:

    def __init__(self, window):
        self.window = window
        self.line_clipping_method = 'liang-barsky'

    def transform(self, drawable):
        drawable = drawable.copy()

        transformation = Transformation3D(drawable)
        vrp_offset = self.window.get_offset()
        transformation = transformation.translation(-vrp_offset)

        angle_vpn_x, angle_vpn_y = self.window.get_vpn_angles()
        t = self.window.rotate(self.window.vpn.copy(), angle_vpn_x, [1,0,0])
        t = self.window.rotate(t, angle_vpn_y, [0,1,0])

        transformation = transformation.rotation_relative_to_axis(angle_vpn_x, [1,0,0], reference=vrp_offset)
        transformation = transformation.rotation_relative_to_axis(angle_vpn_y, [0,1,0], reference=vrp_offset)
        transformation = transformation.escalation_relative_to_a_point([1/(self.window.width/2), 1/(self.window.height/2), 1], self.window.get_offset())

        drawable = transformation.apply()
        
        # print()
        # print("Offset: ", vrp_offset)
        # print("UP: ", self.window.vpu)
        # print("Right: ", self.window.vpr)
        # print("VPN: ", self.window.vpn)
        # print("VPN arrumado: ", t)
        # print("theta_x: ", np.degrees(angle_vpn_x))
        # print("theta_y: ", np.degrees(angle_vpn_y))

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