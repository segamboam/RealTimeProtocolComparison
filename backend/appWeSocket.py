import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket
from .server.websocket_handler import WebSocketManager
from fastapi.websockets import WebSocketDisconnect

import cv2
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import numpy as np
import base64

from fastapi.middleware.cors import CORSMiddleware

from backend.video.track import VideoTransformTrack
from backend.video.VideoTransform import CartoonTransform, EdgesTransform, RotateTransform, GrayscaleTransform, InvertTransform, BlurTransform



# Configuración de logging para registrar información y errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocket")


app = FastAPI()

# Configurar CORS para permitir conexiones WebSocket desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes, se puede restringir a una lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario de transformaciones de imagen disponibles
TRANSFORMS = {
    "cartoon": CartoonTransform(),
    "edges": EdgesTransform(),
    #"rotate": RotateTransform(),  # Transformación de rotación comentada
    "grayscale": GrayscaleTransform(),
    "invert": InvertTransform(),
    "blur": BlurTransform(),
}

# Instancia global para gestionar las conexiones WebSocket
websocket_manager = WebSocketManager()

# Ruta para servir archivos estáticos (CSS, JS, imágenes, etc.)
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "frontend")), name="static")

# Ruta principal que retorna el HTML para la interfaz de usuario
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/indexWebSocket.html", "r") as f:
        return HTMLResponse(content=f.read())

# Ruta WebSocket para manejar las conexiones de los clientes
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)  # Conectar el WebSocket
    current_transform = "edges"  # Transformación inicial establecida

    try:
        while True:
            # Esperar mensajes del cliente
            message = await websocket.receive()

            if "text" in message:
                # Si el mensaje es texto, actualizar la transformación
                data = json.loads(message["text"])
                if "transform" in data and data["transform"] in TRANSFORMS:
                    current_transform = data["transform"]  # Cambiar la transformación actual
                    logger.info(f"Transformación cambiada a: {current_transform}")
            elif "bytes" in message:
                # Si el mensaje contiene datos binarios, procesar el frame
                frame_data = np.frombuffer(message["bytes"], dtype=np.uint8)  # Convertir los bytes a un array numpy
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)  # Decodificar el frame

                # Aplicar la transformación seleccionada al frame
                transformed_frame = TRANSFORMS[current_transform].apply(frame)
                
                # Codificar el frame transformado como JPEG
                _, buffer = cv2.imencode(".jpg", transformed_frame)
                frame_bytes = buffer.tobytes()  # Convertir el buffer a bytes
                frame_bytes64 = base64.b64encode(frame_bytes).decode('utf-8')  # Codificar a base64
                frame_base64 = f"data:image/jpeg;base64,{frame_bytes64}"  # Formato de imagen base64

                # Enviar el frame transformado al cliente
                try:
                    await websocket_manager.send_frame(websocket, frame_base64)
                except RuntimeError as e:
                    logger.warning(f"No se pudo enviar frame: {e}")  # Advertencia si no se puede enviar el frame
                    break

            # Controlar el frame rate, aproximadamente 30 FPS
            await asyncio.sleep(0.03)  
    except WebSocketDisconnect:
        logger.info("Cliente desconectado")  # Registro de desconexión del cliente
        websocket_manager.disconnect(websocket)  # Desconectar el WebSocket
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")  # Registro de errores en el WebSocket
    finally:
        logger.info("Cerrando conexión")  # Registro de cierre de conexión