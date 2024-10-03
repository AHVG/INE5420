import os

from model.drawable import Point, Line, Wireframe


class ObjFileHandler:

    @staticmethod
    def export_file(objects, path):
        offset = 0
        all_v = ""
        all_o = ""
        all_mtl = ""

        for obj in objects:
            v, o, mtl, offset = obj.export_to_file(offset)
            all_v += v
            all_o += o
            all_mtl += mtl

        obj_path = f"{path}.obj"
        mtl_path = f"{path}.mtl"

        with open(obj_path, 'w') as obj_file:
            obj_file.write(all_v)
            obj_file.write("mtllib " + os.path.basename(mtl_path) + "\n")
            obj_file.write(all_o)

        with open(mtl_path, 'w') as mtl_file:
            mtl_file.write(all_mtl)


    @staticmethod
    def import_file(path):
        def read_vertices(path):
            vertices = []
            
            with open(path, 'r') as obj_file:
                for line in obj_file:
                    parts = line.strip().split()
                    
                    if parts and parts[0] == 'v':
                        vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            
            return vertices

        def read_objs(path):
            objects = {}
            with open(path, 'r') as obj_file:
                lines = obj_file.readlines()
                for i, line in enumerate(lines):
                    parts = line.strip().split()
                    name = " ".join(parts[1:])
                    if parts[0] == 'o':
                        objects[name] = {'vertices': [], 'type': None, "material": ""}
                        parts = lines[i + 1].strip().split()

                        if parts[0] == 'usemtl':
                            objects[name]["material"] = name
                        
                        parts = lines[i + 2].strip().split()
                        if parts[0] in ("l", "f", "p"):
                            objects[name]["type"] = parts[0]
                            objects[name]["vertices"] = [int(v) for v in parts[1:]]

            return objects
        
        def read_mtl(path):
            mtl = {}
            with open(path, 'r') as obj_file:
                lines = obj_file.readlines()
                for i, line in enumerate(lines):
                    parts = line.strip().split()

                    if parts[0] == 'newmtl':
                        name = " ".join(parts[1:])
                        mtl[name] = {}
                        
                        parts = lines[i + 1].strip().split()

                        if parts[0] == 'Kd':
                            mtl[name]["color"] = [float(c) for c in parts[1:]]

            return mtl
    
        def convert_rgb_to_hex(kd_color):
            return "#{:02x}{:02x}{:02x}".format(
                int(kd_color[0] * 255),
                int(kd_color[1] * 255),
                int(kd_color[2] * 255)
            )

        
        path_mtl = f"{path}.mtl"
        path_obj = f"{path}.obj"

        vertices = read_vertices(path_obj)
        objs = read_objs(path_obj)
        mtl = read_mtl(path_mtl)

        new_objects = []
        for obj, attr in objs.items():
            name = obj
            points = [vertices[v - 1][:2] for v in attr["vertices"]]
            color = convert_rgb_to_hex(mtl[name]["color"])
            
            if len(points) == 1:
                new_object = Point(name, points, color)
            elif len(points) == 2:
                new_object = Line(name, points, color)
            elif len(points) > 2:
                if attr["type"] == "f":
                    new_object = Wireframe(name, points, color, is_solid=True)
                else:
                    new_object = Wireframe(name, points, color)
            
            new_objects.append(new_object)
        
        return new_objects
           
