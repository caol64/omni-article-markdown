from abc import ABC, abstractmethod

class Extractor(ABC):

    @abstractmethod
    def extract(self) -> tuple:
        """
        Return the tag of article container.
        """
        ...
