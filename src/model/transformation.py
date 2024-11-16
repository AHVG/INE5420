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
        center = self.get_center(self.drawable)
        reference = center if reference is None else reference
        reference = np.array([reference[0], reference[1], 1], dtype=np.float64)

        self.translation(-reference)
        self.matrix = self.matrix @ rotation_matrix
        self.translation(reference)

        return self

    def escalation(self, factor):
        center = self.get_center(self.drawable)
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
    
    def __init__(self, drawable):
        self.matrix = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
        self.drawable = drawable

    def translation(self, displacement):
        translation_matrix = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [displacement[0], displacement[1], displacement[2], 1]
        ], dtype=np.float64)

        self.matrix = self.matrix @ translation_matrix

        return self

    def rotation(self, angles, reference=None):
        rx, ry, rz = angles
        center = self.get_center(self.drawable)
        reference = center if reference is None else reference
        reference = np.array([reference[0], reference[1], reference[2], 1], dtype=np.float64)

        # Translada o ponto de referência para a origem
        self.translation(-reference[:3])
        
        # Rotação em torno do eixo X
        rotation_x = np.matrix([
            [1, 0, 0, 0],
            [0, np.cos(rx), -np.sin(rx), 0],
            [0, np.sin(rx), np.cos(rx), 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
        
        # Rotação em torno do eixo Y
        rotation_y = np.matrix([
            [np.cos(ry), 0, np.sin(ry), 0],
            [0, 1, 0, 0],
            [-np.sin(ry), 0, np.cos(ry), 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)
        
        # Rotação em torno do eixo Z
        rotation_z = np.matrix([
            [np.cos(rz), -np.sin(rz), 0, 0],
            [np.sin(rz), np.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)

        # Aplicar as rotações acumulativamente
        self.matrix = self.matrix @ rotation_x @ rotation_y @ rotation_z

        # Translada o ponto de referência de volta à posição original
        self.translation(reference[:3])

        return self
    
    def rotation_relative_to_axis(self, angle, axis, reference=None):
        angle = -angle
        # Normalizar o vetor eixo
        axis = np.array(axis, dtype=np.float64)
        axis = axis / np.linalg.norm(axis)  # Normaliza para garantir que o eixo seja unitário
        ux, uy, uz = axis

        # Determinar o ponto de referência (default é o centro do objeto)
        center = self.get_center(self.drawable)
        reference = center if reference is None else reference
        reference = np.array([reference[0], reference[1], reference[2], 1], dtype=np.float64)

        # Translada o ponto de referência para a origem
        self.translation(-reference[:3])

        # Matriz de rotação usando a fórmula de Rodrigues para um eixo arbitrário
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        one_minus_cos = 1 - cos_angle

        rotation_matrix = np.matrix([
            [cos_angle + ux**2 * one_minus_cos, ux * uy * one_minus_cos - uz * sin_angle, ux * uz * one_minus_cos + uy * sin_angle, 0],
            [uy * ux * one_minus_cos + uz * sin_angle, cos_angle + uy**2 * one_minus_cos, uy * uz * one_minus_cos - ux * sin_angle, 0],
            [uz * ux * one_minus_cos - uy * sin_angle, uz * uy * one_minus_cos + ux * sin_angle, cos_angle + uz**2 * one_minus_cos, 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)

        # Aplicar a rotação
        self.matrix = self.matrix @ rotation_matrix

        # Translada o ponto de referência de volta à posição original
        self.translation(reference[:3])

        return self

    def escalation(self, factor):
        center = self.get_center(self.drawable)
        return self.escalation_relative_to_a_point(factor, center)
    
    def escalation_relative_to_a_point(self, factor, point):
        escalation_matrix = np.matrix([
            [factor[0], 0, 0, 0],
            [0, factor[1], 0, 0],
            [0, 0, factor[2], 0],
            [0, 0, 0, 1]
        ], dtype=np.float64)

        # Transladar o ponto de referência para a origem
        self.translation(-point[:3])

        # Aplicar a matriz de escalonamento
        self.matrix = self.matrix @ escalation_matrix

        # Transladar de volta para o ponto de referência
        self.translation(point[:3])

        return self
    
    def apply(self):
        """
        Aplica a matriz de transformação acumulada ao drawable.
        """
        return self.drawable @ self.matrix
