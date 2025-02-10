from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.context import TestContext


class BaseTools(ABC):
    """Base class for all tools"""

    def __init__(self, context: 'TestContext'):
        self._context: 'TestContext' = context

    @abstractmethod
    def validate(self):
        """Validate tool configuration"""
        pass
