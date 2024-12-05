import uuid
import json
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder, MediaRelay, MediaBlackhole
from backend.video.track import VideoTransformTrack
from backend.video.VideoTransform import CartoonTransform, EdgesTransform, RotateTransform, GrayscaleTransform, InvertTransform,  BlurTransform
import asyncio

# Configuración del logger para registrar información sobre las conexiones WebRTC
logger = logging.getLogger("pc")
# Conjunto para almacenar las conexiones de pares activas
pcs = set()
# Instancia de MediaRelay para gestionar el flujo de medios
relay = MediaRelay()

def get_transform(transform_name, **kwargs):
    """
    Devuelve la transformación correspondiente según el nombre proporcionado.
    
    Args:
        transform_name (str): Nombre de la transformación deseada.
        **kwargs: Argumentos adicionales para las transformaciones que lo requieran.
    
    Returns:
        Transform: Instancia de la transformación correspondiente o None si no se encuentra.
    """
    if transform_name == "cartoon":
        return CartoonTransform()
    elif transform_name == "edges":
        return EdgesTransform()
    elif transform_name == "rotate":
        angle = kwargs.get("angle", 45)  # Valor por defecto de 45 grados
        return RotateTransform(angle=angle)
    elif transform_name == "grayscale":
        return GrayscaleTransform()
    elif transform_name == "invert":
        return InvertTransform()
    elif transform_name == "blur":
        kernel_size = kwargs.get("kernel_size", 15)  # Valor por defecto de tamaño de kernel
        return BlurTransform(kernel_size=kernel_size)
    else:
        return None  # Retorna None si no se encuentra la transformación

async def offer(request):
    """
    Maneja la recepción de la oferta y responde con la respuesta de WebRTC.
    
    Args:
        request (aiohttp.web.Request): La solicitud HTTP que contiene la oferta.
    
    Returns:
        aiohttp.web.Response: Respuesta con la descripción de la sesión WebRTC.
    """
    params = await request.json()  # Obtiene los parámetros de la solicitud en formato JSON
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])  # Crea una descripción de sesión a partir de la oferta

    pc = RTCPeerConnection()  # Crea una nueva conexión de par
    pc_id = f"PeerConnection({uuid.uuid4()})"  # Genera un ID único para la conexión
    pcs.add(pc)  # Agrega la conexión al conjunto de conexiones activas

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)  # Función para registrar información con el ID de conexión

    log_info("Created for %s", request.remote)  # Registra la creación de la conexión

    # Configuración de grabación
    if request.app["record_to"]:
        recorder = MediaRecorder(request.app["record_to"])  # Crea un grabador si se especifica la ruta
    else:
        recorder = MediaBlackhole()  # Si no, utiliza un "agujero negro" que descarta los medios

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)  # Registra el estado de la conexión
        if pc.connectionState in ["failed", "closed"]:
            await pc.close()  # Cierra la conexión si ha fallado o se ha cerrado
            pcs.discard(pc)  # Elimina la conexión del conjunto de conexiones activas

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)  # Registra la recepción de una pista

        if track.kind == "video":
            transform = get_transform(params.get("video_transform", ""), **params)  # Obtiene la transformación de video
            pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track),  # Suscribe la pista al relay
                    transform=transform,  # Aplica la transformación
                )
            )
            if request.app["record_to"]:
                recorder.addTrack(relay.subscribe(track))  # Agrega la pista al grabador si se especifica

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)  # Registra el final de la pista
            await recorder.stop()  # Detiene la grabación

    # Manejo de la oferta
    await pc.setRemoteDescription(offer)  # Establece la descripción remota
    await recorder.start()  # Inicia la grabación

    # Generar respuesta
    answer = await pc.createAnswer()  # Crea una respuesta a la oferta
    await pc.setLocalDescription(answer)  # Establece la descripción local

    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),  # Devuelve la respuesta en formato JSON
    )

async def on_shutdown(app):
    """
    Cierra todas las conexiones activas al apagar la aplicación.
    
    Args:
        app (aiohttp.web.Application): La aplicación que se está cerrando.
    """
    coros = [pc.close() for pc in pcs]  # Crea una lista de corutinas para cerrar cada conexión
    await asyncio.gather(*coros)  # Espera a que todas las conexiones se cierren
    pcs.clear()  # Limpia el conjunto de conexiones activas