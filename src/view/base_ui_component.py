

class BaseUIComponent:
    
    def __init__(self, controller) -> None:
        self.controller = controller
        self.configure()
        self.register_events()

    def configure(self):
        pass
    
    def register_events(self):
        pass
