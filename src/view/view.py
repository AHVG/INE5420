import os
import tkinter as tk

from tkinter import filedialog
from datetime import datetime

from view.base_ui_component import BaseUIComponent

from view.window_to_apply_transformations import WindowToApplyTransformations
from view.window_to_create_point import WindowToCreatePoint
from view.window_to_create_line import WindowToCreateLine
from view.window_to_create_wireframe import WindowToCreateWireframe
from view.window_to_create_bezier import WindowToCreateBezier
from view.window_to_create_bspline import WindowToCreateBSpline
from view.canvas import Canvas


class View(BaseUIComponent):

    def __init__(self, root, controller):
        self.root = root
        super().__init__(controller)
    
    def configure(self):
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.transcript_frame = tk.Text(self.main_frame, width=125, height = 10, bg="white", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.transcript_frame.pack(side=tk.BOTTOM, expand=True, padx=10, pady=10)

        self.canvas_frame = tk.LabelFrame(self.main_frame, text="Viewport", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = Canvas(self.canvas_frame, width=600, height=600, margin_size=20, bg="white")
        self.canvas.pack()
        self.controller.set_aspect_ratio(self.canvas.get_aspect_ratio())

        self.menu_frame = tk.LabelFrame(self.main_frame, text="Menu", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.menu_bar = tk.Menu(self.root)

        #self.create_file_section()
        self.create_objects_list_section()
        self.window_frame = tk.LabelFrame(self.menu_frame, text="Window", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.window_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.create_navigation_section()
        self.create_clipping_section()
        self.create_manipulation_section()

        self.draw_canvas()
    
    def register_events(self):

        self.root.bind("<Delete>", lambda _: self.remove_objects())
        
        self.root.config(menu=self.menu_bar)
        
        self.menu_bar.add_command(label="Import File", command=self.import_world)
        self.menu_bar.add_command(label="Export File", command=self.export_world)

        self.zoom_in_button.config(command=self.zoom_in)
        self.zoom_out_button.config(command=self.zoom_out)

        self.radio_button.config(command=self.toggle_line_clipping_method)
        self.radio_button_entry_value.config(state='readonly')
        
        self.up_button.config(command=self.move_up)
        self.left_button.config(command=self.move_left)
        self.right_button.config(command=self.move_right)
        self.down_button.config(command=self.move_down)
        self.forward_button.config(command=self.move_forward)
        self.backward_button.config(command=self.move_backward)

        self.rotate_left_button.config(command=self.rotate_left)
        self.rotate_right_button.config(command=self.rotate_right)
        self.rotate_up_button.config(command=self.rotate_up)
        self.rotate_down_button.config(command=self.rotate_down)
        self.rotate_clockwise_button.config(command=self.rotate_clockwise)
        self.rotate_counterclockwise_button.config(command=self.rotate_counterclockwise)

        self.point_create_button.config(command=lambda: WindowToCreatePoint(self, self.controller, self.canvas))
        self.line_create_button.config(command=lambda: WindowToCreateLine(self, self.controller, self.canvas))
        self.wireframe_create_button.config(command=lambda: WindowToCreateWireframe(self, self.controller, self.canvas))
        self.bezier_create_button.config(command=lambda: WindowToCreateBezier(self, self.controller, self.canvas))
        self.bspline_create_button.config(command=lambda: WindowToCreateBSpline(self, self.controller, self.canvas))
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

    def create_file_section(self):
        self.arquivo_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.arquivo_menu)
        self.arquivo_menu.add_separator()
    
    def create_clipping_section(self):
        self.clipping_frame = tk.Frame(self.window_frame, bg="lightgray")
        self.clipping_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.radio_button = tk.Button(self.clipping_frame, text="radio")
        self.radio_button.grid(row=0, column= 0, padx=10, pady=10)
        self.radio_button_entry_value = tk.Entry(self.clipping_frame, width=15)
        self.radio_button_entry_value.grid(row=0, column = 1, padx=5, pady=5) 
        self.radio_button_entry_value.insert(0, 'liang-barsky')

    def create_objects_list_section(self):
        self.objects_frame = tk.LabelFrame(self.menu_frame, text="Objects", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.objects_frame.pack(side=tk.LEFT, padx=5, pady=5)
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

        self.zoom_factor_entry_label = tk.Label(self.zoom_buttons, bg="lightgray", text="Step:")
        self.zoom_factor_entry_label.grid(row=0, column=2, padx=5, pady=5)

        self.zoom_factor_entry_value = tk.Entry(self.zoom_buttons, width=5)
        self.zoom_factor_entry_value.grid(row=0, column=3, padx=5, pady=5) 
        self.zoom_factor_entry_value.insert(0, "5") 

        self.label_percent = tk.Label(self.zoom_buttons, bg="lightgray", text="%")
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
        
        self.forward_button = tk.Button(self.directions_buttons, text="forward", width=7)
        self.forward_button.grid(row=3, column=0, padx=5, pady=5)

        self.backward_button = tk.Button(self.directions_buttons, text="backward", width=7)
        self.backward_button.grid(row=3, column=2, padx=5, pady=5)

        self.window_rotation_buttons = tk.Frame(self.nav_frame, bg="lightgray")
        self.window_rotation_buttons.grid(row=4, column=0, padx=10, pady=10)

        self.rotate_left_button = tk.Button(self.window_rotation_buttons, text="Rotate Left")
        self.rotate_left_button.grid(row=0, column=0, padx=5, pady=10)

        self.rotate_right_button = tk.Button(self.window_rotation_buttons, text="Rotate Right")
        self.rotate_right_button.grid(row=0, column=1, padx=5, pady=10)

        self.rotate_up_button = tk.Button(self.window_rotation_buttons, text="Rotate Up")
        self.rotate_up_button.grid(row=1, column=0, padx=5, pady=10)

        self.rotate_down_button = tk.Button(self.window_rotation_buttons, text="Rotate Down")
        self.rotate_down_button.grid(row=1, column=1, padx=5, pady=10)

        self.rotate_clockwise_button = tk.Button(self.window_rotation_buttons, text="Rotate Clockwise")
        self.rotate_clockwise_button.grid(row=2, column=0, padx=5, pady=10)

        self.rotate_counterclockwise_button = tk.Button(self.window_rotation_buttons, text="Rotate Counterclockwise")
        self.rotate_counterclockwise_button.grid(row=2, column=1, padx=5, pady=10)

        self.rotation_angle = tk.Label(self.window_rotation_buttons, bg="lightgray", text="Angle:")
        self.rotation_angle.grid(row=0, column=3, padx=5, pady=5)

        self.rotation_angle_entry_value = tk.Entry(self.window_rotation_buttons, width=5)
        self.rotation_angle_entry_value.grid(row=0, column=4, padx=5, pady=5) 
        self.rotation_angle_entry_value.insert(0, "5")

        self.label_degree = tk.Label(self.window_rotation_buttons, bg="lightgray", text="°")
        self.label_degree.grid(row=0, column=5, padx=5, pady=5)

    def create_manipulation_section(self):
        self.manipulation_frame = tk.LabelFrame(self.window_frame, text="Manipulation", bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14,))
        self.manipulation_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.point_create_button = tk.Button(self.manipulation_frame, text="Create Point")
        self.point_create_button.grid(row=0, column=0, padx=5, pady=5)

        self.line_create_button = tk.Button(self.manipulation_frame, text="Create Line")
        self.line_create_button.grid(row=0, column=1, padx=5, pady=5)

        self.wireframe_create_button = tk.Button(self.manipulation_frame, text="Create Wireframe",)
        self.wireframe_create_button.grid(row=1, column=0, padx=5, pady=5)
    
        self.bezier_create_button = tk.Button(self.manipulation_frame, text="Create Bezier",)
        self.bezier_create_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.bspline_create_button = tk.Button(self.manipulation_frame, text="Create BSpline",)
        self.bspline_create_button.grid(row=2, column=0, padx=5, pady=5)
    
        self.objects_remove_button = tk.Button(self.manipulation_frame, text="Remove selected object",)
        self.objects_remove_button.grid(row=3, column=0, padx=5, pady=5)

        self.apply_transformation = tk.Button(self.manipulation_frame, text="Apply transformation",)
        self.apply_transformation.grid(row=3, column=1, padx=5, pady=5)
    
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
    
    def move_forward(self):
        self.log_message("Moving window forward")
        self.controller.move_forward()
        self.draw_canvas()
    
    def move_backward(self):
        self.log_message("Moving window backward")
        self.controller.move_backward()
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

    def rotate_left(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Left rotation using {angle}° angle")
            self.controller.rotate_left(angle)
            self.draw_canvas()
    
    def rotate_right(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Right rotation using {angle}° angle")
            self.controller.rotate_right(angle)
            self.draw_canvas()

    def rotate_up(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Up rotation using {angle}° angle")
            self.controller.rotate_up(angle)
            self.draw_canvas()
    
    def rotate_down(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Down rotation using {angle}° angle")
            self.controller.rotate_down(angle)
            self.draw_canvas()

    def rotate_clockwise(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Clockwise rotation using {angle}° angle")
            self.controller.rotate_clockwise(angle)
            self.draw_canvas()
    
    def rotate_counterclockwise(self):
        try:
            angle = float(self.rotation_angle_entry_value.get())
        except:
            self.log_message("Invalid angle, try float values")
            self.rotation_angle_entry_value.delete(0, tk.END)
            self.rotation_angle_entry_value.insert(0, "5")
        else:
            self.log_message(f"Counterclockwise rotation using {angle}° angle")
            self.controller.rotate_counterclockwise(angle)
            self.draw_canvas()

    def import_world(self):
        file_path = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj")])
        if file_path:
            path_without_extension = file_path[:-4]
            self.controller.import_world(path_without_extension)
            
            self.log_message(f"Importing world from {file_path}")
            self.draw_canvas()
            self.update_objects_list()

    def export_world(self):
        default_filename = "world"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            title="Salvar Mundo Como",
            defaultextension="",
            filetypes=[("OBJ and MTL files", "*.obj;*.mtl"),]
        )

        if file_path:
            base_path = os.path.splitext(file_path)[0]
            self.controller.export_world(base_path)
            self.log_message(f"Exporting world to {base_path}")

    def toggle_line_clipping_method(self):
        self.radio_button_entry_value.config(state='normal')
        method = self.radio_button_entry_value.get()
        self.radio_button_entry_value.delete(0, tk.END)

        if method == 'liang-barsky':
            self.radio_button_entry_value.insert(0, 'nicholl-lee-nicholl')
        else:
            self.radio_button_entry_value.insert(0, 'liang-barsky')
        
        self.radio_button_entry_value.config(state='readonly')
        self.controller.set_line_clipping_method(self.radio_button_entry_value.get())
    
    def draw_canvas(self):
        print()
        print("Offset: ", self.controller.window.offset)
        print("VPN: ", self.controller.window.vpn)
        print("VPR: ", self.controller.window.vpr)
        print("VPU: ", self.controller.window.vpu)
    
        self.canvas.setup()
        for o in self.controller.display_file.objects:
            o = self.controller.viewport.transform(o)
            if o:
                o.draw(self.canvas)
    
        self.canvas.debug()
