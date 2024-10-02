import tkinter as tk


class Canvas(tk.Canvas):
    def __init__(self, parent, width, height, margin_size=10, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        self.width = width
        self.height = height
        self.margin_size = margin_size
    
    def setup(self):
        self.delete("all")
    
    def debug(self):
        self.create_line(self.width / 2.0, 0.0, self.width / 2.0, self.height)
        self.create_line(0.0, self.height / 2.0, self.width, self.height / 2.0)
        self.create_rectangle(self.margin_size, self.margin_size, self.width - self.margin_size, self.height - self.margin_size, outline="red")

    def get_aspect_ratio(self):
        return (self.width, self.height)
