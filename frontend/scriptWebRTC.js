// Obtener elementos del DOM
var dataChannelLog = document.getElementById('data-channel'),
    iceConnectionLog = document.getElementById('ice-connection-state'),
    iceGatheringLog = document.getElementById('ice-gathering-state'),
    signalingLog = document.getElementById('signaling-state');

// Inicializar la conexión peer y el canal de datos
var pc = null; // Conexión peer
var dc = null, dcInterval = null; // Canal de datos y su intervalo

// Función para crear una conexión peer
function createPeerConnection() {
    var config = {
        sdpSemantics: 'unified-plan' // Configuración para el plan unificado de SDP
    };

    // Si se selecciona usar STUN, se agrega el servidor STUN
    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
    }

    // Crear la conexión peer
    pc = new RTCPeerConnection(config);

    // Registrar oyentes para ayudar en la depuración
    pc.addEventListener('icegatheringstatechange', () => {
        iceGatheringLog.textContent += ' -> ' + pc.iceGatheringState; // Actualizar el estado de recolección ICE
    }, false);
    iceGatheringLog.textContent = pc.iceGatheringState; // Mostrar el estado inicial

    pc.addEventListener('iceconnectionstatechange', () => {
        iceConnectionLog.textContent += ' -> ' + pc.iceConnectionState; // Actualizar el estado de conexión ICE
    }, false);
    iceConnectionLog.textContent = pc.iceConnectionState; // Mostrar el estado inicial

    pc.addEventListener('signalingstatechange', () => {
        signalingLog.textContent += ' -> ' + pc.signalingState; // Actualizar el estado de señalización
    }, false);
    signalingLog.textContent = pc.signalingState; // Mostrar el estado inicial

    // Conectar audio / video
    pc.addEventListener('track', (evt) => {
        document.getElementById('video').srcObject = evt.streams[0]; // Asignar el stream de video al elemento de video
    });

    return pc; // Retornar la conexión peer
}

// Función para enumerar dispositivos de entrada
function enumerateInputDevices() {
    const populateSelect = (select, devices) => {
        // Limpiar las opciones anteriores
        select.innerHTML = '';

        // Agregar las opciones de dispositivos
        let counter = 1;
        devices.forEach((device) => {
            const option = document.createElement('option');
            option.value = device.deviceId; // ID del dispositivo
            option.text = device.label || ('Device #' + counter); // Nombre del dispositivo o número
            select.appendChild(option); // Agregar opción al select
            counter += 1;
        });
    };

    // Enumerar dispositivos de medios
    navigator.mediaDevices.enumerateDevices().then((devices) => {
        // Población de select para dispositivos de video
        populateSelect(
            document.getElementById('video-input'),
            devices.filter((device) => device.kind == 'videoinput') // Filtrar solo dispositivos de video
        );
    }).catch((e) => {
        alert(e); // Manejo de errores
    });
}

// Función para negociar la conexión
function negotiate() {
    return pc.createOffer().then((offer) => {
        return pc.setLocalDescription(offer); // Establecer la descripción local
    }).then(() => {
        // Esperar a que la recolección ICE se complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve(); // Resolver si ya está completo
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState); // Remover el oyente
                        resolve(); // Resolver
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState); // Agregar oyente para cambios en el estado
            }
        });
    }).then(() => {
        var offer = pc.localDescription; // Obtener la oferta local
        var codec;

        // Filtrar códec de audio
        codec = document.getElementById('audio-codec').value;
        if (codec !== 'default') {
            offer.sdp = sdpFilterCodec('audio', codec, offer.sdp);
        }

        // Filtrar códec de video
        codec = document.getElementById('video-codec').value;
        if (codec !== 'default') {
            offer.sdp = sdpFilterCodec('video', codec, offer.sdp);
        }

        document.getElementById('offer-sdp').textContent = offer.sdp; // Mostrar la oferta SDP
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
                video_transform: document.getElementById('video-transform').value // Transformación de video
            }),
            headers: {
                'Content-Type': 'application/json' // Tipo de contenido
            },
            method: 'POST' // Método POST para enviar la oferta
        });
    }).then((response) => {
        return response.json(); // Convertir la respuesta a JSON
    }).then((answer) => {
        document.getElementById('answer-sdp').textContent = answer.sdp; // Mostrar la respuesta SDP
        return pc.setRemoteDescription(answer); // Establecer la descripción remota
    }).catch((e) => {
        alert(e); // Manejo de errores
    });
}

// Función para iniciar la conexión
function start() {
    document.getElementById('start').style.display = 'none'; // Ocultar botón de inicio

    pc = createPeerConnection(); // Crear conexión peer

    var time_start = null; // Inicializar tiempo de inicio

    const current_stamp = () => {
        if (time_start === null) {
            time_start = new Date().getTime(); // Guardar tiempo de inicio
            return 0;
        } else {
            return new Date().getTime() - time_start; // Calcular tiempo transcurrido
        }
    };

    // Construir restricciones de medios
    const constraints = {
        audio: false,
        video: false
    };

    // Si se selecciona usar video, configurar restricciones
    if (document.getElementById('use-video').checked) {
        const videoConstraints = {};

        const device = document.getElementById('video-input').value; // Obtener dispositivo de video
        if (device) {
            videoConstraints.deviceId = { exact: device }; // Establecer ID del dispositivo
        }

        const resolution = document.getElementById('video-resolution').value; // Obtener resolución
        if (resolution) {
            const dimensions = resolution.split('x'); // Dividir dimensiones
            videoConstraints.width = parseInt(dimensions[0], 0); // Ancho
            videoConstraints.height = parseInt(dimensions[1], 0); // Alto
        }

        constraints.video = Object.keys(videoConstraints).length ? videoConstraints : true; // Establecer restricciones de video
    }

    // Adquirir medios y comenzar la negociación
    if (constraints.audio || constraints.video) {
        if (constraints.video) {
            document.getElementById('media').style.display = 'block'; // Mostrar medios si hay video
        }
        navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
            stream.getTracks().forEach((track) => {
                pc.addTrack(track, stream); // Agregar pistas a la conexión peer
            });
            return negotiate(); // Iniciar negociación
        }, (err) => {
            alert('Could not acquire media: ' + err); // Manejo de errores
        });
    } else {
        negotiate(); // Negociar si no hay medios
    }

    document.getElementById('stop').style.display = 'inline-block'; // Mostrar botón de detener
}

// Función para detener la conexión
function stop() {
    document.getElementById('stop').style.display = 'none'; // Ocultar botón de detener
    document.getElementById('start').style.display = 'inline-block'; // Mostrar botón de inicio

    // Cerrar canal de datos
    if (dc) {
        dc.close();
    }

    // Cerrar transceptores
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach((transceiver) => {
            if (transceiver.stop) {
                transceiver.stop(); // Detener transceptor
            }
        });
    }

    // Cerrar audio / video local
    pc.getSenders().forEach((sender) => {
        sender.track.stop(); // Detener pista
    });

    // Cerrar conexión peer
    setTimeout(() => {
        pc.close(); // Cerrar conexión después de un breve retraso
    }, 500);
}

// Función para filtrar códecs en SDP
function sdpFilterCodec(kind, codec, realSdp) {
    var allowed = [] // Lista de códecs permitidos
    var rtxRegex = new RegExp('a=fmtp:(\\d+) apt=(\\d+)\r$'); // Expresión regular para RTX
    var codecRegex = new RegExp('a=rtpmap:([0-9]+) ' + escapeRegExp(codec)); // Expresión regular para códec
    var videoRegex = new RegExp('(m=' + kind + ' .*?)( ([0-9]+))*\\s*$'); // Expresión regular para video

    var lines = realSdp.split('\n'); // Dividir SDP en líneas

    var isKind = false; // Indicar si se está en la sección del tipo de códec
    for (var i = 0; i < lines.length; i++) {
        if (lines[i].startsWith('m=' + kind + ' ')) {
            isKind = true; // Entrar en la sección del tipo de códec
        } else if (lines[i].startsWith('m=')) {
            isKind = false; // Salir de la sección
        }

        if (isKind) {
            var match = lines[i].match(codecRegex); // Buscar códec
            if (match) {
                allowed.push(parseInt(match[1])); // Agregar códec permitido
            }

            match = lines[i].match(rtxRegex); // Buscar RTX
            if (match && allowed.includes(parseInt(match[2]))) {
                allowed.push(parseInt(match[1])); // Agregar códec RTX permitido
            }
        }
    }

    var skipRegex = 'a=(fmtp|rtcp-fb|rtpmap):([0-9]+)'; // Expresión regular para omitir códecs
    var sdp = ''; // SDP filtrado

    isKind = false; // Reiniciar indicador
    for (var i = 0; i < lines.length; i++) {
        if (lines[i].startsWith('m=' + kind + ' ')) {
            isKind = true; // Entrar en la sección del tipo de códec
        } else if (lines[i].startsWith('m=')) {
            isKind = false; // Salir de la sección
        }

        if (isKind) {
            var skipMatch = lines[i].match(skipRegex); // Buscar coincidencias para omitir
            if (skipMatch && !allowed.includes(parseInt(skipMatch[2]))) {
                continue; // Omitir si no está permitido
            } else if (lines[i].match(videoRegex)) {
                sdp += lines[i].replace(videoRegex, '$1 ' + allowed.join(' ')) + '\n'; // Reemplazar códecs en video
            } else {
                sdp += lines[i] + '\n'; // Agregar línea sin cambios
            }
        } else {
            sdp += lines[i] + '\n'; // Agregar línea sin cambios
        }
    }

    return sdp; // Retornar SDP filtrado
}

// Función para escapar caracteres especiales en expresiones regulares
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escapar caracteres especiales
}

// Enumerar dispositivos de entrada al cargar el script
enumerateInputDevices();