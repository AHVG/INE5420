import tkinter as tk

from ast import literal_eval

from view.base_ui_component import BaseUIComponent


class AttachedWindow(tk.Toplevel, BaseUIComponent):
    
    def __init__(self, view, controller, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        BaseUIComponent.__init__(self, controller)
        self.view = view
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.on_open()

    def on_open(self):
        pass

    def on_close(self):
        self.destroy()
