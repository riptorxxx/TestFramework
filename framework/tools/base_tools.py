from abc import ABC, abstractmethod


class BaseTools(ABC):
    """Base class for all tools"""

    def __init__(self, context):
        self._context = context

    @abstractmethod
    def validate(self):
        """Validate tool configuration"""
        pass
