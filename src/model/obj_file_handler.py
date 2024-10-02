import os


class Exportable:
    def export_to_file(self, offset):
        pass


class Importable:
    def import_from_file(self):
        pass


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
        pass
