import tkinter as tk

from view.attached_window import AttachedWindow


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
            self.view.log_message(f"Creating Point called {name} at point {(x, y)}")
        finally:
            self.on_close()