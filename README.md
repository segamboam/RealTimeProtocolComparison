# RealTimeProtocolComparison

### Descripción de la Ejecución de `appWebRTC`

Para ejecutar la aplicación `appWebRTC`, utiliza el siguiente comando en la consola:
```bash
    python3 -m backend.appWebRTC
```
### Funcionamiento de la Aplicación

1. **Inicio del Servidor**: Al ejecutar el comando, se inicia un servidor web que escucha en el host y puerto especificados en la configuración. Este servidor maneja las conexiones WebRTC y las solicitudes HTTP.

2. **Interacción con el Frontend**: La aplicación permite que el frontend acceda a la cámara del usuario. Cuando el usuario inicia la aplicación en su navegador, se establece una conexión WebRTC entre el cliente (frontend) y el servidor (backend).

3. **Captura de Video**: El frontend utiliza la API `getUserMedia` para acceder a la cámara y captura el video en tiempo real. Este video se envía al backend a través de la conexión WebRTC.

4. **Transformación de Video**: En el backend, el video recibido se procesa utilizando diferentes transformaciones (como efectos de cartoon, detección de bordes, etc.) según la selección del usuario en la interfaz.

5. **Retorno del Video Transformado**: Una vez que el video ha sido transformado, se envía de vuelta al frontend, donde se muestra al usuario en tiempo real.

### Ejecución de `appWebSocket`

Para ejecutar la aplicación `appWebSocket`, utiliza el siguiente comando en la consola:

```bash
    uvicorn backend.appWeSocket:app --reload --port 8000
```
Una vez que la aplicación esté en funcionamiento, puedes acceder a la interfaz de usuario en tu navegador a través del siguiente enlace:[http://localhost:8000/static/indexWebSocket.html](http://localhost:8000/static/indexWebSocket.html)

### Descripción de la Aplicación
Esta aplicación permite que el frontend acceda a la cámara del usuario, envíe el video al backend a través de WebSocket, donde se transforma y se retorna al frontend. Esto permite aplicar diferentes efectos de video en tiempo real, como detección de bordes o efectos de cartoon, y visualizar el resultado en el navegador.