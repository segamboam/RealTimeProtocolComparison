from aiohttp import web  # Importa el módulo web de aiohttp para crear aplicaciones web
from .server.aiothttpHandlers import index, javascript, css  # Importa manejadores para rutas estáticas
from .server.aiothttpConfiguration import get_server_config  # Importa la función para obtener la configuración del servidor
from .server.webrtc_handler import offer, on_shutdown  # Importa manejadores para WebRTC y eventos de cierre

if __name__ == "__main__":  # Verifica si el script se está ejecutando directamente
    args, ssl_context = get_server_config()  # Obtiene los argumentos y el contexto SSL de la configuración del servidor

    app = web.Application()  # Crea una nueva aplicación web
    app["record_to"] = args.record_to  # Opción para grabar medios, almacenando la ruta en el diccionario de la aplicación

    # Rutas estáticas
    app.router.add_get("/", index)  # Ruta para la página principal, manejada por la función index
    app.router.add_get("/scriptWebRTC.js", javascript)  # Ruta para el script JavaScript, manejada por la función javascript
    app.router.add_get("/styles.css", css)  # Ruta para la hoja de estilos CSS, manejada por la función css

    # Rutas dinámicas
    app.router.add_post("/offer", offer)  # Ruta para manejar ofertas WebRTC, manejada por la función offer

    # Evento de cierre
    app.on_shutdown.append(on_shutdown)  # Registra la función on_shutdown para ejecutar al cerrar el servidor

    # Iniciar el servidor
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)  # Inicia la aplicación web en el host y puerto especificados, con el contexto SSL
