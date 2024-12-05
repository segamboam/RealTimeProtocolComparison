from aiortc import MediaStreamTrack
from av import VideoFrame
import numpy as np
from .VideoTransformProtocol import VideoTransform

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track: MediaStreamTrack, transform: VideoTransform):
        """
        Inicializa la clase VideoTransformTrack.

        :param track: Una instancia de MediaStreamTrack que representa la pista de video original.
        :param transform: Una instancia de VideoTransform que define la transformación a aplicar al video.
        """
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        """
        Recibe el siguiente cuadro de video de la pista original, aplica la transformación y devuelve el nuevo cuadro.

        :return: Un nuevo VideoFrame que contiene el cuadro transformado.
        """
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        if self.transform:
            img = self.transform.apply(img)

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame
