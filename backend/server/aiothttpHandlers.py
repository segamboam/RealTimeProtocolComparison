import os
from aiohttp import web

# Define la ruta del directorio actual donde se encuentra este archivo
ROOT = os.path.dirname(__file__)

# Construye la ruta hacia el directorio del frontend, asumiendo que está dos niveles arriba del directorio actual
ROOT_FRONTEND = "/".join(ROOT.split("/")[:-2]) + '/frontend/'

# Maneja las solicitudes a la ruta raíz ("/") y devuelve el contenido del archivo index.html
async def index(request):
    # Abre y lee el contenido del archivo index.html
    content = open(os.path.join(ROOT_FRONTEND, "indexWebRTC.html"), "r").read()
    # Devuelve una respuesta web con el tipo de contenido HTML
    return web.Response(content_type="text/html", text=content)

# Maneja las solicitudes a la ruta "/script.js" y devuelve el contenido del archivo script.js
async def javascript(request):
    # Abre y lee el contenido del archivo script.js
    content = open(os.path.join(ROOT_FRONTEND, "scriptWebRTC.js"), "r").read()
    # Devuelve una respuesta web con el tipo de contenido JavaScript
    return web.Response(content_type="application/javascript", text=content)

# Maneja las solicitudes a la ruta "/styles.css" y devuelve el contenido del archivo styles.css
async def css(request):
    # Abre y lee el contenido del archivo styles.css
    content = open(os.path.join(ROOT_FRONTEND, "styles.css"), "r").read()
    # Devuelve una respuesta web con el tipo de contenido CSS
    return web.Response(content_type="text/css", text=content)