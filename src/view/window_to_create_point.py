import re
import tkinter as tk

from view.attached_window import AttachedWindow


class WindowToCreatePoint(AttachedWindow):

    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="Color:").grid(row=0, column=2)
        self.color_entry = tk.Entry(self)
        self.color_entry.grid(row=0, column=3)

        tk.Label(self, text="x:").grid(row=1, column=0)
        self.x_entry = tk.Entry(self)
        self.x_entry.grid(row=1, column=1)

        tk.Label(self, text="y:").grid(row=1, column=2)
        self.y_entry = tk.Entry(self)
        self.y_entry.grid(row=1, column=3)

        self.create_button = tk.Button(self, text="Create")
        self.create_button.grid(row=2, column=0, columnspan=4, pady=5)

    def register_events(self):
        self.create_button.config(command=self.create_point_from_dialog)
    
    def create_point_from_dialog(self):
        try:
            name = self.name.get()
            color = self.color_entry.get()
            
            x = self.x_entry.get()
            y = self.y_entry.get()
            x = float(x)
            y = float(y)

            hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
            if not bool(hex_pattern.match(color)):
                raise TypeError("Invalid hexadecimal value for color. Expected format #RRGGBB or #RGB")

            self.controller.create_point(name, x, y, color)
            self.view.draw_canvas()
            self.view.update_objects_list()
            self.view.log_message(f"Creating Point called {name} at point {(x, y)}")
        except ValueError:
            self.view.log_message(f"Failed to convert coordinates to float: {(x, y)}")
        except TypeError as te:
            self.view.log_message(te)
        except Exception as e:
            self.view.log_message(f"Unexpected failure: {e}")
        finally:
            self.on_close()