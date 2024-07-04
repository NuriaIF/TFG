
class FileLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    @staticmethod
    def load(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        # Here, do something with the content
        return content
