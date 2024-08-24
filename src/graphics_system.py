import tkinter as tk

from  window import Window
from display_file import DisplayFile
from constants import INITIAL_VIEWPORT, INITIAL_WINDOW


class GraphicsSystem:

    def __init__(self):
        self.root = tk.Tk()
        
        self.viewport = INITIAL_VIEWPORT
        self.window = [-100, 100, -100, 100]

        self.window = Window()
        
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.grid(column=1, rowspan=7, padx=10, pady=10)

        # TODO: DANDO ERRADO O ZOOM
        self.zoom_in_button = tk.Button(self.root, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=0, padx=5, pady=5)

        self.zoom_out_button = tk.Button(self.root, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.grid(row=1, column=0, padx=5, pady=5)

        self.left_button = tk.Button(self.root, text="Esquerda", command=self.move_left)
        self.left_button.grid(row=3, column=0, padx=5, pady=5)

        self.right_button = tk.Button(self.root, text="Direita", command=self.move_right)
        self.right_button.grid(row=4, column=0, padx=5, pady=5)

        self.up_button = tk.Button(self.root, text="Cima", command=self.move_up)
        self.up_button.grid(row=5, column=0, padx=5, pady=5)

        self.down_button = tk.Button(self.root, text="Baixo", command=self.move_down)
        self.down_button.grid(row=6, column=0, padx=5, pady=5)
        
        self.display_file = DisplayFile(self.canvas, self.window, self.viewport)
        
        self.display_file.draw()
    
    def zoom_out(self):
        self.window.zoom_out()
        self.display_file.draw()

    def zoom_in(self):
        self.window.zoom_in()
        self.display_file.draw()
    
    def move_up(self):
        self.window.move_up()
        self.display_file.draw()

    def move_down(self):
        self.window.move_down()
        self.display_file.draw()

    def move_left(self):
        self.window.move_left()
        self.display_file.draw()

    def move_right(self):
        self.window.move_right()
        self.display_file.draw()

    def run(self):
        self.root.mainloop()
