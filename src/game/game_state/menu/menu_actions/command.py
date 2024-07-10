"""
Command pattern for the menu actions
"""
from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract class for command pattern
    """
    @abstractmethod
    def execute(self):
        """
        Execute the command
        Must be implemented by the subclasses
        :return:
        """
        pass
