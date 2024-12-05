import argparse  # Importa el módulo argparse para manejar argumentos de línea de comandos
import logging   # Importa el módulo logging para registrar mensajes de log
import ssl       # Importa el módulo ssl para manejar conexiones seguras

def get_server_config():
    """
    Configura y devuelve los parámetros del servidor a partir de los argumentos de línea de comandos.

    Returns:
        tuple: Un tuple que contiene los argumentos parseados y el contexto SSL (si se proporciona).
    """
    # Crea un parser para los argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    
    # Agrega argumentos que el usuario puede proporcionar al ejecutar el script
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--record-to", help="Write received media to a file.")
    parser.add_argument("--verbose", "-v", action="count")  # Permite aumentar el nivel de verbosidad en los logs
    
    # Analiza los argumentos proporcionados por el usuario
    args = parser.parse_args()
    
    # Configura el nivel de logging basado en el argumento de verbosidad
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)  # Muestra mensajes de debug si se especifica
    else:
        logging.basicConfig(level=logging.INFO)   # Muestra mensajes informativos por defecto

    ssl_context = None  # Inicializa el contexto SSL como None
    # Si se proporciona un archivo de certificado, configura el contexto SSL
    if args.cert_file:
        ssl_context = ssl.SSLContext()  # Crea un nuevo contexto SSL
        ssl_context.load_cert_chain(args.cert_file, args.key_file)  # Carga el certificado y la clave

    # Devuelve los argumentos y el contexto SSL
    return args, ssl_context