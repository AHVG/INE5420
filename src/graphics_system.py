import tkinter as tk

from  window import Window
from display_file import DisplayFile
from constants import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, INITIAL_VIEWPORT, INITIAL_WINDOW


class GraphicsSystem:

    def __init__(self):
        self.root = tk.Tk()
        
        self.viewport = INITIAL_VIEWPORT
        self.window = [-100, 100, -100, 100]

        self.window = Window()

        self.last_mouse_position = None
        
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT, bg="white")
        self.canvas.pack()
        self.display_file = DisplayFile(self.canvas, self.window, self.viewport)

        self.menu_frame = tk.LabelFrame(self.main_frame, text="Menu", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.create_objects_list()
        self.create_nav_buttons()
        self.create_manipulation_buttons()
    
    def create_objects_list(self):
        self.objects_frame = tk.Frame(self.menu_frame, bg="lightgray", padx=5, pady=5)
        self.objects_frame.pack(side=tk.TOP)

        self.objects_listbox = tk.Listbox(self.objects_frame)
        self.objects_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_objects_list()

    def update_objects_list(self):
        self.objects_listbox.delete(0, tk.END)  # Limpa a lista
        for o in self.display_file.objects:
            self.objects_listbox.insert(tk.END, o.name)

    def create_nav_buttons(self):
        self.nav_frame = tk.LabelFrame(self.menu_frame, text="Navigation", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14,))
        self.nav_frame.pack(side=tk.TOP, padx=5, pady=5)

        self.zoom_buttons = tk.Frame(self.nav_frame, bg="lightgray")
        self.zoom_buttons.grid(row=0, column=0, padx=10, pady=10)

        self.zoom_in_button = tk.Button(self.zoom_buttons, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=0, padx=5, pady=5)

        self.zoom_out_button = tk.Button(self.zoom_buttons, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.grid(row=0, column=1, padx=5, pady=5)

        self.directions_buttons = tk.Frame(self.nav_frame, bg="lightgray")
        self.directions_buttons.grid(row=2, column=0, padx=5, pady=5)

        self.up_button = tk.Button(self.directions_buttons, text="Up", width=7, command=self.move_up)
        self.up_button.grid(row=0, column=1, padx=5, pady=5)

        self.left_button = tk.Button(self.directions_buttons, text="Left", width=7, command=self.move_left)
        self.left_button.grid(row=1, column=0, padx=5, pady=5)

        self.right_button = tk.Button(self.directions_buttons, text="Right", width=7, command=self.move_right)
        self.right_button.grid(row=1, column=2, padx=5, pady=5)

        self.down_button = tk.Button(self.directions_buttons, text="Down", width=7, command=self.move_down)
        self.down_button.grid(row=2, column=1, padx=5, pady=5)

        self.canvas.bind("<Shift-B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.reset_move)

        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows somente?
        self.canvas.bind("<Button-4>", lambda _: self.zoom_out())  # Linux (scroll up)
        self.canvas.bind("<Button-5>", lambda _: self.zoom_in())  # Linux (scroll down)

    def create_manipulation_buttons(self):
        self.manipulation_frame = tk.LabelFrame(self.menu_frame, text="Manipulation", bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14,))
        self.manipulation_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.point_create_button = tk.Button(self.manipulation_frame, text="Create Point", command=lambda: None)
        self.point_create_button.grid(row=0, column=0, padx=5, pady=5)

        self.line_create_button = tk.Button(self.manipulation_frame, text="Create Line", command=lambda: None)
        self.line_create_button.grid(row=0, column=1, padx=5, pady=5)

        self.wireframe_create_button = tk.Button(self.manipulation_frame, text="Create Wireframe", command=lambda: None)
        self.wireframe_create_button.grid(row=0, column=2, padx=5, pady=5)
    
    def zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()

    def zoom_out(self):
        self.window.zoom_out()
        self.display_file.draw()

    def zoom_in(self):
        self.window.zoom_in()
        self.display_file.draw()
    
    def move(self, event):
        if self.last_mouse_position is None:
            self.last_mouse_position = (event.x, event.y)

        dx = event.x - self.last_mouse_position[0]
        dy = event.y - self.last_mouse_position[1]
        self.last_mouse_position = (event.x, event.y)

        self.window.increase_offset([-dx, dy])
        self.display_file.draw()
    
    def reset_move(self, event):
        self.last_mouse_position = None
    
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
