from abc import ABC, abstractmethod


class AbstractFieldExtractor(ABC):
    def __init__(self, field_name):
        self._field_name = field_name

    @property
    def field_name(self):
        """Return the name of the field this provider extracts."""
        return self._field_name

    @abstractmethod
    def extract_field(self, text):
        """Extract field data from the text."""
        pass
