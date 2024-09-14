class ObjFileHandler:

    @staticmethod
    def export_file(objects, file_name="object_file.obj"):
        with open(file_name, 'w') as file:
            for object in objects:
                file.write(f"{object.kind} {object.name}\n")
                for vertex in object.points:
                    file.write(f"v {vertex[0]} {vertex[1]}\n")
