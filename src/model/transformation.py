import numpy as np


class Transformation:

    def translation(self, displacement):
        pass

    def rotation(self, angle, reference):
        pass

    def escalation(self, factor):
        pass

    def apply(self):
        pass

    def get_center(self, drawable):
        return np.mean(drawable.points, axis=0)


class Transformation2D(Transformation):
    
    def __init__(self, drawable):
        self.matrix = np.matrix([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=np.float64)
        self.drawable = drawable

    def translation(self, displacement):
        translation_matrix = np.matrix([
            [1, 0, 0],
            [0, 1, 0],
            [displacement[0], displacement[1], 1]
        ], dtype=np.float64)

        self.matrix = self.matrix @ translation_matrix

        return self

    def rotation(self, angle, reference=None):
        angle = -angle
        rotation_matrix = np.matrix([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ], dtype=np.float64)
        center = self.drawable.get_center()
        reference = center if reference is None else reference
        reference = np.array([reference[0], reference[1], 1], dtype=np.float64)

        self.translation(-reference)
        self.matrix = self.matrix @ rotation_matrix
        self.translation(reference)

        return self

    def escalation(self, factor):
        center = self.drawable.get_center()
        return self.escalation_relative_to_a_point(factor, center)
    
    def escalation_relative_to_a_point(self, factor, point):
        escalation_matrix = np.matrix([
            [factor[0], 0, 0],
            [0, factor[1], 0],
            [0, 0, 1]
        ], dtype=np.float64)

        self.translation(-point)
        self.matrix = self.matrix @ escalation_matrix
        self.translation(point)

        return self
    
    def apply(self):
        return self.drawable @ self.matrix


class Transformation3D(Transformation):
    
    def __init__(self, object3d):
        self.matrix = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
        self.object3d = object3d

    def translation(self, displacement):
        translation_matrix = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [displacement[0], displacement[1], displacement[2], 1]
        ], dtype=np.float64)

        self.matrix = self.matrix @ translation_matrix

        return self


    def rotation(self, angle, reference=None):
        def x_rotation(matrix, angle):
            rx = np.matrix([
            [1, 0, 0, 0],
            [0, np.cos(angle), np.sin(angle), 0],
            [0, -np.sin(angle), np.cos(angle), 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
            return matrix @ rx
        
        def y_rotation(matrix, angle):
            ry = np.matrix([
            [1, 0, 0, 0],
            [0, np.cos(angle), np.sin(angle), 0],
            [0, -np.sin(angle), np.cos(angle), 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
            return matrix @ ry
        
        def z_rotation(matrix, angle):
            rz = np.matrix([
            [np.cos(angle), np.sin(angle), 0, 0],
            [-np.sin(angle), np.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
            return matrix @ rz
        
        center = self.object3d.get_center()
        reference = center if reference is None else reference
        reference = np.array([reference[0], reference[1], reference[2], 1], dtype=np.float64)
        self.translation(-reference)
        
        axl_angle = 54.74   #axl_angle é 54.74 pois o eixo de rotação possui o mesmo valor em todas as coordenadas
        rotation_matrix = x_rotation(self.matrix, axl_angle)
        rotation_matrix = y_rotation(rotation_matrix, axl_angle)
        rotation_matrix = z_rotation(rotation_matrix, axl_angle)
        rotation_matrix = y_rotation(rotation_matrix, angle)
        rotation_matrix = z_rotation(rotation_matrix, -axl_angle)
        rotation_matrix = x_rotation(self.matrix, -axl_angle)

        self.matrix = self.matrix @ rotation_matrix
        self.translation(reference)

        return self

    def escalation(self, factor):
        center = self.object3d.get_center()
        return self.escalation_relative_to_a_point(factor, center)
    
    def escalation_relative_to_a_point(self, factor, point):
        escalation_matrix = np.matrix([
            [factor[0], 0, 0, 0],
            [0, factor[1], 0, 0],
            [0, 0, 0, factor[3], 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)

        self.translation(-point)
        self.matrix = self.matrix @ escalation_matrix
        self.translation(point)

        return self
    
    def apply(self):
        return self.object3d @ self.matrix