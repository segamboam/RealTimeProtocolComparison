from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import cv2
import numpy as np
from backend.video.track import VideoTransformTrack
from backend.video.VideoTransform import CartoonTransform, EdgesTransform, RotateTransform, GrayscaleTransform, InvertTransform, BlurTransform


class WebSocketManager:
    """
    Clase que gestiona las conexiones WebSocket.
    Permite aceptar nuevas conexiones, desconectar clientes y enviar frames a través de WebSocket.
    """
    
    def __init__(self):
        """
        Inicializa el WebSocketManager con una lista vacía de conexiones activas.
        """
        self.active_connections: list[WebSocket] = []  # Lista de conexiones activas

    async def connect(self, websocket: WebSocket):
        """
        Acepta una nueva conexión WebSocket y la añade a la lista de conexiones activas.

        Args:
            websocket (WebSocket): La conexión WebSocket que se va a aceptar.
        """
        await websocket.accept()  # Acepta la conexión WebSocket
        self.active_connections.append(websocket)  # Añade la conexión a la lista

    def disconnect(self, websocket: WebSocket):
        """
        Desconecta un WebSocket y lo elimina de la lista de conexiones activas.

        Args:
            websocket (WebSocket): La conexión WebSocket que se va a desconectar.
        """
        self.active_connections.remove(websocket)  # Elimina la conexión de la lista

    async def send_frame(self, websocket: WebSocket, frame: bytes):
        """
        Envía un frame de bytes a través de la conexión WebSocket.

        Args:
            websocket (WebSocket): La conexión WebSocket a la que se enviará el frame.
            frame (bytes): El frame que se enviará.

        Raises:
            WebSocketDisconnect: Si la conexión se desconecta durante el envío.
        """
        try:
            await websocket.send_bytes(frame)  # Envía el frame a través del WebSocket
        except WebSocketDisconnect:
            self.disconnect(websocket)  # Desconecta si hay un error de desconexión



