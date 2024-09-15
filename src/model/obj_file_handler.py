from tkinter import filedialog

class ObjFileHandler:

    @staticmethod
    def export_file(objects, file_name="object_file.obj"):
        file_path = filedialog.askdirectory() + '/' + file_name
        with open(file_path, 'w') as file:
            for object in objects:
                file.write(f"o {object.name}\n")
                for vertex in object.points:
                    file.write(f"v {vertex[0]} {vertex[1]}\n")
        return file_path

    @staticmethod
    def import_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            objects = {}
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('o '):
                        current_object = line.split(' ', 1)[1]
                        objects[current_object] = []
                    elif line.startswith('v '):
                        vertex = tuple(map(float, line.split()[1:3]))
                        if current_object:
                            objects[current_object].append(vertex)
            return file_path, objects
        return None, None
        