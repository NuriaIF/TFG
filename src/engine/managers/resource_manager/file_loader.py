"""
This module contains the FileLoader class
"""


class FileLoader:
    """
    This class is responsible for loading files from the disk.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    @staticmethod
    def load(file_path: str) -> str:
        """
        Load the content of a file from the disk and return it as a string.
        :param file_path:
        :return:
        """
        with open(file_path) as file:
            content = file.read()
        # Here, do something with the content
        return content
