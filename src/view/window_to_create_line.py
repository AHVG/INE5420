import tkinter as tk

from view.attached_window import AttachedWindow


class WindowToCreateLine(AttachedWindow):
    
    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="Color:").grid(row=0, column=2)
        self.color_entry = tk.Entry(self)
        self.color_entry.grid(row=0, column=3)

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
        self.create_button.grid(row=3, column=0, columnspan=4, pady=5)
    
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
            self.view.log_message(f"Creating Line called {name} and with points {[(x1, y1), (x2, y2)]}")
        finally:
            self.on_close()