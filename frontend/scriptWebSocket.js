let ws; // WebSocket para la comunicación
let videoElement = document.getElementById("video"); // Elemento de video en el DOM
let startButton = document.getElementById("start"); // Botón para iniciar la transmisión
let stopButton = document.getElementById("stop"); // Botón para detener la transmisión
let wsStateElement = document.getElementById("ws-state"); // Elemento para mostrar el estado del WebSocket
let transformSelect = document.getElementById("video-transform"); // Selector para transformaciones de video
let mediaStream; // Stream de la cámara
let videoStreamInterval; // Intervalo para capturar frames de video

function start() {
    // Establece la conexión WebSocket
    ws = new WebSocket("ws://localhost:8000/ws");

    // Manejar la conexión WebSocket
    ws.onopen = () => {
        wsStateElement.textContent = "Connected"; // Actualiza el estado a "Conectado"
        console.log("WebSocket conectado");

        // Inicia la cámara
        navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                mediaStream = stream; // Guarda el stream de video
                const videoTracks = mediaStream.getVideoTracks(); // Obtiene las pistas de video
                console.log("Usando cámara:", videoTracks[0].label); // Muestra el nombre de la cámara

                // Captura frames a intervalos regulares
                const videoCapture = new ImageCapture(videoTracks[0]); // Crea un objeto ImageCapture para la pista de video
                videoStreamInterval = setInterval(async () => {
                    const frame = await videoCapture.grabFrame(); // Captura un frame
                    const canvas = document.createElement("canvas"); // Crea un canvas para procesar el frame
                    canvas.width = frame.width; // Establece el ancho del canvas
                    canvas.height = frame.height; // Establece la altura del canvas
                    const ctx = canvas.getContext("2d"); // Obtiene el contexto 2D del canvas
                    ctx.drawImage(frame, 0, 0); // Dibuja el frame en el canvas
                    const blob = await new Promise((resolve) =>
                        canvas.toBlob(resolve, "image/jpeg") // Convierte el canvas a un blob JPEG
                    );
                    ws.send(blob); // Envía el frame como datos binarios a través del WebSocket
                }, 30); // Aproximadamente 30 FPS
            })
            .catch((err) => {
                console.error("Error accediendo a la cámara:", err); // Maneja errores al acceder a la cámara
            });
    };

    // Manejo de mensajes recibidos (frames transformados)
    ws.onmessage = (event) => {
        if (event.data) {
            try {
                const base64String = event.data; // Obtiene los datos del mensaje

                // Verificar si la cadena base64 es válida
                if (base64String.startsWith("data:image/jpeg;base64,")) {
                    // Crear la URL de datos con la cadena base64
                    const imageUrl = base64String;

                    // Obtener el elemento de imagen
                    const imgElement = document.getElementById('image'); // Elemento de imagen en el DOM

                    // Asignar la URL de la imagen base64
                    imgElement.src = imageUrl;

                    // Manejar la carga exitosa
                    imgElement.onload = () => {
                        // Aquí se puede agregar lógica adicional si es necesario
                    };

                    // Manejar el error de carga
                    imgElement.onerror = (error) => {
                        console.error("Error al cargar el frame:", error); // Muestra el error en la consola
                        alert("Error al cargar el frame en la imagen."); // Alerta al usuario
                    };
                } else {
                    console.error("Cadena base64 recibida no es válida."); // Maneja cadenas base64 no válidas
                }
            } catch (error) {
                console.error("Error procesando el frame:", error); // Maneja errores al procesar el frame
            }
        } else {
            console.error("Datos recibidos del backend están vacíos."); // Maneja datos vacíos
        }
    };

    // Manejo de errores y cierre
    ws.onerror = (error) => {
        console.error("WebSocket Error:", error); // Muestra el error en la consola
        wsStateElement.textContent = "Error"; // Actualiza el estado a "Error"
    };

    ws.onclose = () => {
        console.log("WebSocket desconectado"); // Muestra mensaje de desconexión
        wsStateElement.textContent = "Disconnected"; // Actualiza el estado a "Desconectado"
    };

    // Actualiza botones
    startButton.style.display = "none"; // Oculta el botón de inicio
    stopButton.style.display = "inline-block"; // Muestra el botón de detener
}

function stop() {
    // Detiene la captura de video y cierra el WebSocket
    if (ws) {
        ws.close(); // Cierra la conexión WebSocket
        ws = null; // Limpia la variable ws
    }
    if (mediaStream) {
        const tracks = mediaStream.getTracks(); // Obtiene las pistas del stream
        tracks.forEach((track) => track.stop()); // Detiene cada pista
        mediaStream = null; // Limpia la variable mediaStream
    }
    if (videoStreamInterval) {
        clearInterval(videoStreamInterval); // Detiene el intervalo de captura de video
        videoStreamInterval = null; // Limpia la variable videoStreamInterval
    }

    // Actualiza botones
    startButton.style.display = "inline-block"; // Muestra el botón de inicio
    stopButton.style.display = "none"; // Oculta el botón de detener
}

// Manejo de cambios en la selección de transformación
transformSelect.addEventListener("change", () => {
    // Envía el cambio de transformación al backend
    console.log("cambios"); // Muestra un mensaje en la consola
    if (ws && ws.readyState === WebSocket.OPEN) {
        const transform = transformSelect.value; // Obtiene el valor de la transformación seleccionada
        ws.send(JSON.stringify({ transform })); // Envía la transformación al backend como JSON
        console.log("Cambio de transformación enviado:", transform); // Muestra el cambio en la consola
    }
});
