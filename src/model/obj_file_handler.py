
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
        for obj in objects:
            v, o, mtl, offset = obj.export_to_file(offset)

    @staticmethod
    def import_file(path):
        pass
