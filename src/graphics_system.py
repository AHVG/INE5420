import tkinter as tk

from controller.controller import Controller
from view.view import View


class GraphicsSystem:

    """
    -> Canvas
    -> Menu
        -> Lista de objetos
            -> Janela de transformação
        -> Window
            -> Navegação
            -> manipulação
                -> Janela de criação de ponto
                -> Janela de criação de linha
                -> Janela de criação de poligono
                -> Janela de aplicar transformação
    -> Log
    """

    def __init__(self):
        self.root = tk.Tk()
        self.controller = Controller()
        self.view = View(self.root, self.controller)

    def run(self):
        self.root.mainloop()
