import tkinter as tk

from view.attached_window import AttachedWindow


class WindowToApplyTransformations(AttachedWindow):

    def on_open(self):
        try:
            indexes = self.view.objects_listbox.curselection()
            self.controller.setup_transformation(indexes[0])
        except:
            self.on_close()

    def configure(self):
        self.rotation_frame = tk.LabelFrame(self, text="Rotation", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.rotation_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.translation_frame = tk.LabelFrame(self, text="Translation", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.translation_frame.grid(row=1, column=0, padx=10, pady=10)

        self.scaling_frame = tk.LabelFrame(self, text="Scaling", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.scaling_frame.grid(row=1, column=1, padx=10, pady=10)

        self.history_frame = tk.LabelFrame(self, text="Transformations", width=200, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.history_frame.grid(row=1, column=2, padx=10, pady=10)

        self.transformation_list = tk.Text(self.history_frame, height=15, width=60)
        self.transformation_list.pack(padx=10, pady=10)

        self.apply_button = tk.Button(self, text="Apply transformations", bg="lightgray")
        self.apply_button.grid(row=2, column=2, padx=10, pady=10)

        self.configure_rotation_frame()
        self.configure_translation_frame()
        self.configure_scaling_frame()

    def register_events(self):
        self.angle_relative_to_origin_button.config(command=self.rotate_relative_to_origin)
        self.angle_relative_to_center_of_object_button.config(command=self.rotate_relative_to_center_of_object)
        self.rotation_relative_to_point_button.config(command=self.rotate_relative_to_point)

        self.translate_button.config(command=self.translate)
        self.scale_button.config(command=self.scale)

        self.apply_button.config(command=self.apply)

    def configure_rotation_frame(self):
        self.rotation_relative_to_origin_frame = tk.LabelFrame(self.rotation_frame, text="Rotation relative to origin", width=400, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.rotation_relative_to_origin_frame.grid(row=0, column=0, padx=10, pady=10)

        self.angle_relative_to_origin_label = tk.Label(self.rotation_relative_to_origin_frame, text="Angle:", bg="lightgray")
        self.angle_relative_to_origin_label.grid(row=0, column=0, padx=10, pady=10)

        self.angle_relative_to_origin_entry = tk.Entry(self.rotation_relative_to_origin_frame)
        self.angle_relative_to_origin_entry.grid(row=0, column=1, padx=10, pady=10)

        label = tk.Label(self.rotation_relative_to_origin_frame, text="degrees", bg="lightgray")
        label.grid(row=0, column=2, padx=10, pady=10)

        self.angle_relative_to_origin_button = tk.Button(self.rotation_relative_to_origin_frame, text="Add", bg="lightgray")
        self.angle_relative_to_origin_button.grid(row=1, column=1, padx=10, pady=10)


        self.rotation_relative_to_center_of_object_frame = tk.LabelFrame(self.rotation_frame, text="Rotation relative to center of object", width=400, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.rotation_relative_to_center_of_object_frame.grid(row=0, column=1, padx=10, pady=10)

        self.angle_relative_to_center_of_object_label = tk.Label(self.rotation_relative_to_center_of_object_frame, text="Angle:", bg="lightgray")
        self.angle_relative_to_center_of_object_label.grid(row=0, column=0, padx=10, pady=10)

        self.angle_relative_to_center_of_object_entry = tk.Entry(self.rotation_relative_to_center_of_object_frame)
        self.angle_relative_to_center_of_object_entry.grid(row=0, column=1, padx=10, pady=10)

        label = tk.Label(self.rotation_relative_to_center_of_object_frame, text="degrees", bg="lightgray")
        label.grid(row=0, column=2, padx=10, pady=10)

        self.angle_relative_to_center_of_object_button = tk.Button(self.rotation_relative_to_center_of_object_frame, text="Add", bg="lightgray")
        self.angle_relative_to_center_of_object_button.grid(row=1, column=1, padx=10, pady=10)


        self.rotation_relative_to_point_frame = tk.LabelFrame(self.rotation_frame, text="Rotation relative to a point", width=400, bg="lightgray", relief="groove", borderwidth=2, font=("Arial", 14, "bold"))
        self.rotation_relative_to_point_frame.grid(row=0, column=2, padx=10, pady=10)

        self.angle_relative_to_point_label = tk.Label(self.rotation_relative_to_point_frame, text="Angle:", bg="lightgray")
        self.angle_relative_to_point_label.grid(row=0, column=0, padx=10, pady=10)

        self.angle_relative_to_point_entry = tk.Entry(self.rotation_relative_to_point_frame)
        self.angle_relative_to_point_entry.grid(row=0, column=1, padx=10, pady=10)

        label = tk.Label(self.rotation_relative_to_point_frame, text="degrees", bg="lightgray")
        label.grid(row=0, column=2, padx=10, pady=10)

        self.x_label = tk.Label(self.rotation_relative_to_point_frame, text="X:", bg="lightgray")
        self.x_label.grid(row=1, column=0, padx=10, pady=10)

        self.x_entry = tk.Entry(self.rotation_relative_to_point_frame)
        self.x_entry.grid(row=1, column=1, padx=10, pady=10)

        self.y_label = tk.Label(self.rotation_relative_to_point_frame, text="Y:", bg="lightgray")
        self.y_label.grid(row=2, column=0, padx=10, pady=10)

        self.y_entry = tk.Entry(self.rotation_relative_to_point_frame)
        self.y_entry.grid(row=2, column=1, padx=10, pady=10)

        self.rotation_relative_to_point_button = tk.Button(self.rotation_relative_to_point_frame, text="Add")
        self.rotation_relative_to_point_button.grid(row=3, column=1, padx=10, pady=10)

    def configure_translation_frame(self):
        self.dx_label = tk.Label(self.translation_frame, text="Displacement in X:", bg="lightgray")
        self.dx_label.grid(row=0, column=0, padx=10, pady=10)

        self.dx_entry = tk.Entry(self.translation_frame)
        self.dx_entry.grid(row=0, column=1, padx=10, pady=10)

        self.dy_label = tk.Label(self.translation_frame, text="Displacement in Y:", bg="lightgray")
        self.dy_label.grid(row=1, column=0, padx=10, pady=10)

        self.dy_entry = tk.Entry(self.translation_frame)
        self.dy_entry.grid(row=1, column=1, padx=10, pady=10)

        self.translate_button = tk.Button(self.translation_frame, text="Add")
        self.translate_button.grid(row=2, column=1, padx=10, pady=10)

    def configure_scaling_frame(self):
        self.sx_label = tk.Label(self.scaling_frame, text="Scale factor in X:", bg="lightgray")
        self.sx_label.grid(row=0, column=0, padx=10, pady=10)

        self.sx_entry = tk.Entry(self.scaling_frame)
        self.sx_entry.grid(row=0, column=1, padx=10, pady=10)

        self.sy_label = tk.Label(self.scaling_frame, text="Scale factor in Y:", bg="lightgray")
        self.sy_label.grid(row=1, column=0, padx=10, pady=10)

        self.sy_entry = tk.Entry(self.scaling_frame)
        self.sy_entry.grid(row=1, column=1, padx=10, pady=10)

        self.scale_button = tk.Button(self.scaling_frame, text="Add")
        self.scale_button.grid(row=2, column=1, padx=10, pady=10)

    def add_to_history(self, transformation):
        self.transformation_list.insert(tk.END, "- " + transformation + "\n")
        self.transformation_list.see(tk.END)

    def rotate_relative_to_origin(self):
        try:
            angle = float(self.angle_relative_to_origin_entry.get())
        except:
            self.add_to_history("Failed to rotate relative to origin")
        else:
            self.add_to_history(f"Rotate {angle}º relative to origin")
            self.controller.rotate_relative_to_origin(angle)
        finally:
            self.angle_relative_to_origin_entry.delete(0, tk.END)
            self.angle_relative_to_origin_entry.insert(0, "")

    def rotate_relative_to_center_of_object(self):
        try:
            angle = float(self.angle_relative_to_center_of_object_entry.get())
        except:
            self.add_to_history("Failed to rotate relative to center of object")
        else:
            self.add_to_history(f"Rotate {angle}º relative to center of object")
            self.controller.rotate_relative_to_center_of_object(angle)
        finally:
            self.angle_relative_to_center_of_object_entry.delete(0, tk.END)
            self.angle_relative_to_center_of_object_entry.insert(0, "")

    def rotate_relative_to_point(self):
        try:
            angle = float(self.angle_relative_to_point_entry.get())
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
        except:
            self.add_to_history("Failed to rotate relative to point")
        else:
            self.add_to_history(f"Rotate {angle}º relative to point {(x, y)}")
            self.controller.rotate_relative_to_point(angle, (x, y))
        finally:
            self.angle_relative_to_point_entry.delete(0, tk.END)
            self.angle_relative_to_point_entry.insert(0, "")

            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, "")

            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, "")

    def translate(self):
        try:
            dx = float(self.dx_entry.get())
            dy = float(self.dy_entry.get())
        except:
            self.add_to_history("Failed to translate")
        else:
            self.add_to_history(f"Translate {(dx, dy)}")
            self.controller.translate((dx, dy))
        finally:
            self.dx_entry.delete(0, tk.END)
            self.dx_entry.insert(0, "")

            self.dy_entry.delete(0, tk.END)
            self.dy_entry.insert(0, "")

    def scale(self):
        try:
            sx = float(self.sx_entry.get())
            sy = float(self.sy_entry.get())
        except:
            self.add_to_history("Failed to scale")
        else:
            self.add_to_history(f"Scale {(sx, sy)}")
            self.controller.scale((sx, sy))
        finally:
            self.sx_entry.delete(0, tk.END)
            self.sx_entry.insert(0, "")

            self.sy_entry.delete(0, tk.END)
            self.sy_entry.insert(0, "")

    def apply(self):
        try:
            self.controller.apply()
            self.view.draw_canvas()
        except:
            pass
        finally:
            self.on_close()
