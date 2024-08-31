import tkinter as tk

from datetime import datetime

from model.viewport import Viewport

from view.base_ui_component import BaseUIComponent

from view.window_to_apply_transformations import WindowToApplyTransformations
from view.window_to_create_point import WindowToCreatePoint
from view.window_to_create_line import WindowToCreateLine
from view.window_to_create_wireframe import WindowToCreateWireframe
from view.canvas import Canvas


class View(BaseUIComponent):

    def __init__(self, root, controller):
        self.root = root
        super().__init__(controller)
    
    def configure(self):
        self.last_mouse_position = None

        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.transcript_frame = tk.Text(self.main_frame, width=125, height = 10, bg="white", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.transcript_frame.pack(side=tk.BOTTOM, expand=True, padx=10, pady=10)

        self.canvas_frame = tk.LabelFrame(self.main_frame, text="Viewport", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = Canvas(self.canvas_frame, width=800, height=600, margin_size=20, bg="white")
        self.canvas.pack()
        self.controller.set_aspect_ratio(self.canvas.get_aspect_ratio())

        self.menu_frame = tk.LabelFrame(self.main_frame, text="Menu", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.create_objects_list_section()
        self.window_frame = tk.LabelFrame(self.menu_frame, text="Window", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.window_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.create_navigation_section()
        self.create_manipulation_section()

        self.draw_canvas()
    
    def register_events(self):
        self.canvas.bind("<Shift-B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.reset_move)

        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows somente?
        self.canvas.bind("<Button-4>", lambda _: self.zoom_in())  # Linux (scroll up)
        self.canvas.bind("<Button-5>", lambda _: self.zoom_out())  # Linux (scroll down)
    
        self.zoom_in_button.config(command=self.zoom_in)
        self.zoom_out_button.config(command=self.zoom_out)
        
        self.up_button.config(command=self.move_up)
        self.left_button.config(command=self.move_left)
        self.right_button.config(command=self.move_right)
        self.down_button.config(command=self.move_down)
        
        self.point_create_button.config(command=lambda: WindowToCreatePoint(self, self.controller, self.canvas))
        self.line_create_button.config(command=lambda: WindowToCreateLine(self, self.controller, self.canvas))
        self.wireframe_create_button.config(command=lambda: WindowToCreateWireframe(self, self.controller, self.canvas))
        self.objects_remove_button.config(command=self.remove_objects)

        self.apply_transformation.config(command=lambda: WindowToApplyTransformations(self, self.controller, self.canvas))
    
    def log_message(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.transcript_frame.insert(tk.END, log_entry)
        self.transcript_frame.see(tk.END)

        current_lines = int(self.transcript_frame.index('end-1c').split('.')[0])
        if current_lines > 50:
            self.transcript_frame.delete(1.0, f"{current_lines - 50}.0")

    def create_objects_list_section(self):
        self.objects_frame = tk.LabelFrame(self.menu_frame, text="Objects", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.objects_frame.pack(side=tk.TOP, padx=5, pady=5)
        self.objects_listbox = tk.Listbox(self.objects_frame, selectmode=tk.SINGLE)
        self.objects_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_objects_list()

    def update_objects_list(self):
        self.objects_listbox.delete(0, tk.END)
        for o in self.controller.display_file.objects:
            self.objects_listbox.insert(tk.END, o.name)

    def create_navigation_section(self):
        self.nav_frame = tk.LabelFrame(self.window_frame, text="Navigation", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14,))
        self.nav_frame.pack(side=tk.TOP, padx=5, pady=5)

        self.zoom_buttons = tk.Frame(self.nav_frame, bg="lightgray")
        self.zoom_buttons.grid(row=0, column=0, padx=10, pady=10)

        self.zoom_in_button = tk.Button(self.zoom_buttons, text="Zoom In")
        self.zoom_in_button.grid(row=0, column=0, padx=5, pady=5)

        self.zoom_out_button = tk.Button(self.zoom_buttons, text="Zoom Out")
        self.zoom_out_button.grid(row=0, column=1, padx=5, pady=5)

        self.zoom_factor_entry_label = tk.Label(self.zoom_buttons, text="Passo:")
        self.zoom_factor_entry_label.grid(row=0, column=2, padx=5, pady=5)

        self.zoom_factor_entry_value = tk.Entry(self.zoom_buttons, width=5)
        self.zoom_factor_entry_value.grid(row=0, column=3, padx=5, pady=5) 
        self.zoom_factor_entry_value.insert(0, "5") 

        self.label_percent = tk.Label(self.zoom_buttons, text="%")
        self.label_percent.grid(row=0, column=4, padx=5, pady=5)

        self.directions_buttons = tk.Frame(self.nav_frame, bg="lightgray")
        self.directions_buttons.grid(row=2, column=0, padx=5, pady=5)

        self.up_button = tk.Button(self.directions_buttons, text="Up", width=7)
        self.up_button.grid(row=0, column=1, padx=5, pady=5)

        self.left_button = tk.Button(self.directions_buttons, text="Left", width=7)
        self.left_button.grid(row=1, column=0, padx=5, pady=5)

        self.right_button = tk.Button(self.directions_buttons, text="Right", width=7)
        self.right_button.grid(row=1, column=2, padx=5, pady=5)

        self.down_button = tk.Button(self.directions_buttons, text="Down", width=7)
        self.down_button.grid(row=2, column=1, padx=5, pady=5)

    def create_manipulation_section(self):
        self.manipulation_frame = tk.LabelFrame(self.window_frame, text="Manipulation", bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14,))
        self.manipulation_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.point_create_button = tk.Button(self.manipulation_frame, text="Create Point")
        self.point_create_button.grid(row=0, column=0, padx=5, pady=5)

        self.line_create_button = tk.Button(self.manipulation_frame, text="Create Line")
        self.line_create_button.grid(row=0, column=1, padx=5, pady=5)

        self.wireframe_create_button = tk.Button(self.manipulation_frame, text="Create Wireframe",)
        self.wireframe_create_button.grid(row=0, column=2, padx=5, pady=5)
    
        self.objects_remove_button = tk.Button(self.manipulation_frame, text="Remove selected object",)
        self.objects_remove_button.grid(row=1, column=0, padx=5, pady=5)

        self.apply_transformation = tk.Button(self.manipulation_frame, text="Apply transformation",)
        self.apply_transformation.grid(row=1, column=1, padx=5, pady=5)
    
    def remove_objects(self):
        index = self.objects_listbox.curselection()
        if len(index):
            index = index[0]
            element = self.objects_listbox.get(0, tk.END)[index]
            self.log_message(f"Removing element called {element}")
        else:
            self.log_message("No element was selected")
            return
        self.controller.remove_objects(index)
        self.draw_canvas()
        self.update_objects_list()
    
    def move(self, event):
        if self.last_mouse_position is None:
            self.last_mouse_position = (event.x, event.y)

        dx = event.x - self.last_mouse_position[0]
        dy = event.y - self.last_mouse_position[1]
        self.last_mouse_position = (event.x, event.y)

        if dx > 0:
            self.move_left()
        elif dx < 0:
            self.move_right()

        if dy > 0:
            self.move_up()
        elif dy < 0:
            self.move_down()

    def reset_move(self, _):
        self.last_mouse_position = None
    
    def move_up(self):
        self.log_message("Moving window up")
        self.controller.move_up()
        self.draw_canvas()

    def move_down(self):
        self.log_message("Moving window down")
        self.controller.move_down()
        self.draw_canvas()

    def move_left(self):
        self.log_message("Moving window left")
        self.controller.move_left()
        self.draw_canvas()

    def move_right(self):
        self.log_message("Moving window right")
        self.controller.move_right()
        self.draw_canvas()

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()

    def zoom_in(self):
        try:
            factor = float(self.zoom_factor_entry_value.get())
        except:
            self.log_message("Invalid zoom factor, try float values")
            self.zoom_factor_entry_value.delete(0, tk.END)
            self.zoom_factor_entry_value.insert(0, "5")
        else:
            self.log_message(f"Zoom in using {factor}% zoom factor")
            self.controller.zoom_in(factor)
            self.draw_canvas()

    def zoom_out(self):
        try:
            factor = float(self.zoom_factor_entry_value.get())
        except:
            self.log_message("Invalid zoom factor, try float values")
            self.zoom_factor_entry_value.delete(0, tk.END)
            self.zoom_factor_entry_value.insert(0, "5")
        else:
            self.log_message(f"Zoom out using {factor}% zoom factor")
            self.controller.zoom_out(factor)
            self.draw_canvas()

    def draw_canvas(self):
        self.canvas.setup()
        for o in self.controller.display_file.objects:
            o = self.controller.viewport.transform(o)
            o.draw(self.canvas)
