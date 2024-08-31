import tkinter as tk

from view.attached_window import AttachedWindow


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
            self.view.log_message(f"Creating Wireframe called {name} and with points {points}")
        finally:
            self.on_close()
