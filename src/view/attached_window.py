import tkinter as tk

from ast import literal_eval

from view.base_ui_component import BaseUIComponent


class AttachedWindow(tk.Toplevel, BaseUIComponent):
    
    def __init__(self, view, controller, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        BaseUIComponent.__init__(self, controller)
        self.view = view
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.destroy()


class WindowToCreatePoint(AttachedWindow):

    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="x:").grid(row=1, column=0)
        self.x_entry = tk.Entry(self)
        self.x_entry.grid(row=1, column=1)

        tk.Label(self, text="y:").grid(row=2, column=0)
        self.y_entry = tk.Entry(self)
        self.y_entry.grid(row=2, column=1)

        self.create_button = tk.Button(self, text="Create")
        self.create_button.grid(row=3, column=0, columnspan=2, pady=5)

    def register_events(self):
        self.create_button.config(command=self.create_point_from_dialog)
    
    def create_point_from_dialog(self):
        try:
            name = self.name.get()
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())

            self.controller.create_point(name, x, y)
            self.view.draw_canvas()
            self.view.update_objects_list()
            self.view.log_message("Criando um Point com nome de %s no ponto %s", name, (x, y))
        finally:
            self.on_close()


class WindowToCreateLine(AttachedWindow):
    
    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="x1:").grid(row=1, column=0)
        self.x1_entry = tk.Entry(self)
        self.x1_entry.grid(row=1, column=1)

        tk.Label(self, text="y1:").grid(row=1, column=2)
        self.y1_entry = tk.Entry(self)
        self.y1_entry.grid(row=1, column=3)

        tk.Label(self, text="x2:").grid(row=2, column=0)
        self.x2_entry = tk.Entry(self)
        self.x2_entry.grid(row=2, column=1)

        tk.Label(self, text="y2:").grid(row=2, column=2)
        self.y2_entry = tk.Entry(self)
        self.y2_entry.grid(row=2, column=3)

        self.create_button = tk.Button(self, text="Create")
        self.create_button.grid(row=3, column=0, columnspan=2, pady=5)
    
    def register_events(self):
        self.create_button.configure(command=self.create_line_from_dialog)

    def create_line_from_dialog(self):
        try:
            name = self.name.get()
            x1 = float(self.x1_entry.get())
            y1 = float(self.y1_entry.get())
            x2 = float(self.x2_entry.get())
            y2 = float(self.y2_entry.get())
            
            self.controller.create_line(name, x1, y1, x2, y2)
            self.view.draw_canvas()
            self.view.update_objects_list()
            self.view.log_message("Criando uma Line com nome de %s e com os pontos de %s", name, [(x1, y1), (x2, y2)])
        finally:
            self.on_close()


class WindowToCreateWireframe(AttachedWindow):
    
    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="points like (x1,y1),(x2,y2)...:").grid(row=1, column=0)
        self.points_entry = tk.Entry(self)
        self.points_entry.grid(row=1, column=1)

        self.create_button = tk.Button(self, text="Create")
        self.create_button.grid(row=4, column=0, columnspan=2, pady=5)
    
    def register_events(self):
        self.create_button.configure(command=self.create_wireframe_from_dialog)

    def create_wireframe_from_dialog(self):
        try:
            name = self.name.get()
            points = list(literal_eval(self.points_entry.get()))
            
            self.controller.create_wireframe(name, points)
            self.view.draw_canvas()
            self.view.update_objects_list()
            self.view.log_message("Criando um Wireframe com nome de %s e com os pontos de %s", name, points)
        finally:
            self.on_close()
