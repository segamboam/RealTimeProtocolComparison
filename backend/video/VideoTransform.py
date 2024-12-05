import cv2
import numpy as np
from .VideoTransformProtocol import VideoTransform

class CartoonTransform(VideoTransform):
    """
    Clase que aplica un efecto de cartoon a un marco de video.
    Hereda de la clase VideoTransform.
    """
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Aplica el efecto de cartoon al marco dado.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco transformado con efecto de cartoon.
        """
        # Reduce la resolución de la imagen para suavizar los colores
        img_color = cv2.pyrDown(cv2.pyrDown(frame))
        # Aplica un filtro bilateral varias veces para suavizar la imagen
        for _ in range(6):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
        # Restaura la resolución original
        img_color = cv2.pyrUp(cv2.pyrUp(img_color))

        # Convierte el marco a escala de grises y aplica un umbral adaptativo
        img_edges = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        img_edges = cv2.adaptiveThreshold(
            cv2.medianBlur(img_edges, 7),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        # Convierte los bordes de nuevo a RGB
        img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

        # Combina la imagen de color suavizada con los bordes detectados
        return cv2.bitwise_and(img_color, img_edges)

class EdgesTransform(VideoTransform):
    """
    Clase que detecta bordes en un marco de video.
    Hereda de la clase VideoTransform.
    """
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Aplica detección de bordes al marco dado.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco transformado con bordes detectados.
        """
        # Aplica el detector de bordes Canny y convierte a BGR
        return cv2.cvtColor(cv2.Canny(frame, 100, 200), cv2.COLOR_GRAY2BGR)

class RotateTransform(VideoTransform):
    """
    Clase que rota un marco de video en un ángulo específico.
    Hereda de la clase VideoTransform.
    """
    def __init__(self, angle: float):
        """
        Inicializa la clase con un ángulo de rotación.

        :param angle: Ángulo en grados para rotar el marco.
        """
        self.angle = angle

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Rota el marco dado en el ángulo especificado.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco rotado.
        """
        rows, cols, _ = frame.shape
        # Calcula la matriz de rotación
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), self.angle, 1)
        # Aplica la transformación afín
        return cv2.warpAffine(frame, M, (cols, rows))

class GrayscaleTransform(VideoTransform):
    """
    Clase que convierte un marco de video a escala de grises.
    Hereda de la clase VideoTransform.
    """
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Convierte el marco dado a escala de grises.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco transformado en escala de grises.
        """
        # Convierte a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
        # Convierte de vuelta a 3 canales
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Convertir de vuelta a 3 canales

class InvertTransform(VideoTransform):
    """
    Clase que invierte los colores de un marco de video.
    Hereda de la clase VideoTransform.
    """
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Invierte los colores del marco dado.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco con colores invertidos.
        """
        return cv2.bitwise_not(frame)

class BlurTransform(VideoTransform):
    """
    Clase que aplica un desenfoque gaussiano a un marco de video.
    Hereda de la clase VideoTransform.
    """
    def __init__(self, kernel_size=15):
        """
        Inicializa la clase con un tamaño de kernel para el desenfoque.

        :param kernel_size: Tamaño del kernel para el desenfoque (debe ser impar).
        """
        self.kernel_size = kernel_size

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Aplica desenfoque gaussiano al marco dado.

        :param frame: Un marco de video en formato numpy.ndarray.
        :return: Un marco desenfocado.
        """
        return cv2.GaussianBlur(frame, (self.kernel_size, self.kernel_size), 0)
