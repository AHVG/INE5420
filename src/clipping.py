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