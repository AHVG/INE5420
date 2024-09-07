import tkinter as tk


class MyCanvas(tk.Canvas):
    def __init__(self, parent, width, height, margin_size=20, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        self.width = width
        self.height = height
        self.margin_size = margin_size
    
    def setup(self):
        self.delete("all")
        self.create_rectangle(self.margin_size, self.margin_size, self.width - self.margin_size, self.height - self.margin_size, outline="red")

    def get_aspect_ratio(self):
        return (self.width, self.height)
