import re
import tkinter as tk

from ast import literal_eval

from view.attached_window import AttachedWindow


class WindowToCreateWireframe(AttachedWindow):
    
    def configure(self):
        tk.Label(self, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self)
        self.name.grid(row=0, column=1)

        tk.Label(self, text="Color:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self)
        self.color_entry.grid(row=1, column=1)

        tk.Label(self, text="points like (x1,y1),(x2,y2)...:").grid(row=2, column=0)
        self.points_entry = tk.Entry(self)
        self.points_entry.grid(row=2, column=1)

        tk.Label(self, text="Wireframe Type:").grid(row=3, column=0)

        self.wireframe_type = tk.StringVar(value="solid")

        self.solid_radio = tk.Radiobutton(self, text="Solid", variable=self.wireframe_type, value="solid")
        self.solid_radio.grid(row=3, column=1, sticky="w")

        self.grade_radio = tk.Radiobutton(self, text="Grade", variable=self.wireframe_type, value="grade")
        self.grade_radio.grid(row=3, column=2, sticky="w")

        self.create_button = tk.Button(self, text="Create")
        self.create_button.grid(row=4, column=0, columnspan=2, pady=5)
    
    def register_events(self):
        self.create_button.configure(command=self.create_wireframe_from_dialog)

    def create_wireframe_from_dialog(self):
        try:
            name = self.name.get()
            color = self.color_entry.get()
            points = self.points_entry.get()
            points = list(literal_eval(points))
            is_solid = True if self.wireframe_type.get() == "solid" else False

            hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
            if not bool(hex_pattern.match(color)):
                raise TypeError("Invalid hexadecimal value for color. Expected format #RRGGBB or #RGB")
            
            self.controller.create_wireframe(name, points, color, is_solid)
            self.view.draw_canvas()
            self.view.update_objects_list()
            self.view.log_message(f"Creating Wireframe called {name} and with points {points}")
        except ValueError:
            self.view.log_message(f"Failed to convert coordinates to float: {points}")
        except TypeError as te:
            self.view.log_message(te)
        except Exception as e:
            self.view.log_message(f"Unexpected failure: {e}")
        finally:
            self.on_close()
