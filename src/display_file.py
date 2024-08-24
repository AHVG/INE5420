from drawable import Point, Line, Wireframe


def pan(window, dx, dy):
    window[0] += dx
    window[1] += dx
    window[2] += dy
    window[3] += dy


def zoom(window, factor):
    cx = (window[0] + window[1]) / 2
    cy = (window[2] + window[3]) / 2
    width = (window[1] - window[0]) * factor
    height = (window[3] - window[2]) * factor
    window[0] = cx - width / 2
    window[1] = cx + width / 2
    window[2] = cy - height / 2
    window[3] = cy + height / 2


class DisplayFile:

    def __init__(self, canvas, window, viewport):
        self.canvas = canvas
        self.window = window
        self.viewport = viewport
        self.objects = [Point("First", [(-25, 50)]), Line("Second", [(-40, -32), (10, 90)]), Wireframe("Third", [(-15, 15), (0, 20), (15, 15), (20, 0), (15, -15), (0, -20), (-15, -15), (-20, 0)])]

    def draw(self):
        self.canvas.delete("all")
        for o in self.objects:
            o.draw(self.canvas, self.window, self.viewport)
