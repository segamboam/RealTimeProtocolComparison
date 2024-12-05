from abc import ABC, abstractmethod
import numpy as np

class VideoTransform(ABC):
    @abstractmethod
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Aplica la transformación al frame de video.

        :param frame: Un arreglo de NumPy que representa un frame de video.
        :return: Un nuevo arreglo de NumPy que representa el frame transformado.
        """
        pass
