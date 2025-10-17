// camara.js - Script exclusivo para la página de cámara
document.addEventListener('DOMContentLoaded', function() {

    // Variables globales
    let stream = null;
    let detectionInterval = null;
    let isDetecting = false;
    let detectionStableFrames = 0;
    const FRAMES_TO_CONFIRM = 10;

    // Elementos del DOM
    const btnActivateCamera = document.getElementById('btnActivateCamera');
    const btnCloseCamera = document.getElementById('btnCloseCamera');
    const cameraModal = document.getElementById('cameraModal');
    const cameraVideo = document.getElementById('cameraVideo');
    const detectionCanvas = document.getElementById('detectionCanvas');
    const captureCanvas = document.getElementById('captureCanvas');
    const cameraFrame = document.getElementById('cameraFrame');
    const cameraStatus = document.getElementById('cameraStatus');
    const processingOverlay = document.getElementById('processingOverlay');
    const processingText = document.getElementById('processingText');
    const progressFill = document.getElementById('progressFill');

    // Activar cámara
    btnActivateCamera.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment'
                } 
            });
            cameraVideo.srcObject = stream;
            cameraModal.classList.add('active');
            
            // Esperar a que el video esté listo
            cameraVideo.onloadedmetadata = () => {
                // Configurar canvas de detección
                detectionCanvas.width = cameraVideo.videoWidth;
                detectionCanvas.height = cameraVideo.videoHeight;
                
                // Iniciar detección automática
                iniciarDeteccion();
            };
        } catch (error) {
            alert('Error al acceder a la cámara: ' + error.message);
        }
    });

    // Cerrar cámara
    btnCloseCamera.addEventListener('click', () => {
        cerrarCamara();
    });

    function cerrarCamara() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        if (detectionInterval) {
            clearInterval(detectionInterval);
            detectionInterval = null;
        }
        cameraModal.classList.remove('active');
        cameraFrame.classList.remove('detected');
        isDetecting = false;
        detectionStableFrames = 0;
    }

    // Detectar DNI en el video
    function iniciarDeteccion() {
        isDetecting = true;
        cameraStatus.textContent = '⬤ BUSCANDO DOCUMENTO';
        cameraStatus.style.color = '#ff0000';
        
        // Analizar frames cada 200ms
        detectionInterval = setInterval(() => {
            detectarDocumento();
        }, 200);
    }

    function detectarDocumento() {
        if (!isDetecting) return;

        const ctx = detectionCanvas.getContext('2d');
        ctx.drawImage(cameraVideo, 0, 0, detectionCanvas.width, detectionCanvas.height);
        
        const imageData = ctx.getImageData(0, 0, detectionCanvas.width, detectionCanvas.height);
        const detected = analizarImagen(imageData);
        
        if (detected) {
            detectionStableFrames++;
            
            // Pintar marco verde cuando detecta
            cameraFrame.classList.add('detected');
            
            if (detectionStableFrames >= FRAMES_TO_CONFIRM) {
                // DNI detectado de forma estable
                documentoDetectado();
            } else {
                cameraStatus.textContent = `⬤ ESTABILIZANDO... ${detectionStableFrames}/${FRAMES_TO_CONFIRM}`;
                cameraStatus.style.color = '#ffa500';
            }
        } else {
            detectionStableFrames = 0;
            // Pintar marco rojo cuando no detecta
            cameraFrame.classList.remove('detected');
            cameraStatus.classList.remove('detected');
            cameraStatus.textContent = '⬤ BUSCANDO DOCUMENTO';
            cameraStatus.style.color = '#ff0000';
        }
    }

    function analizarImagen(imageData) {
        const data = imageData.data;
        let edgeCount = 0;
        const threshold = 50;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            const nextR = data[i + 4] || 0;
            const nextG = data[i + 5] || 0;
            const nextB = data[i + 6] || 0;
            
            const diff = Math.abs(r - nextR) + Math.abs(g - nextG) + Math.abs(b - nextB);
            
            if (diff > threshold) {
                edgeCount++;
            }
        }
        
        const edgeRatio = edgeCount / (data.length / 4);
        return edgeRatio > 0.02 && edgeRatio < 0.35;
    }

    function documentoDetectado() {
        if (!isDetecting) return;
        
        isDetecting = false;
        clearInterval(detectionInterval);
        
        cameraFrame.classList.add('detected');
        cameraStatus.textContent = '⬤ DOCUMENTO DETECTADO';
        cameraStatus.classList.add('detected');
        cameraStatus.style.color = '#00ff00';
        
        // Capturar y procesar después de 1 segundo
        setTimeout(() => {
            capturarYEnviar();
        }, 1000);
    }

    // Capturar imagen y enviar al backend
    async function capturarYEnviar() {
        // Capturar frame actual
        const ctx = captureCanvas.getContext('2d');
        captureCanvas.width = cameraVideo.videoWidth;
        captureCanvas.height = cameraVideo.videoHeight;
        ctx.drawImage(cameraVideo, 0, 0);
        
        // Cerrar cámara
        cerrarCamara();
        
        // Mostrar overlay de procesamiento
        processingOverlay.classList.add('active');
        processingText.textContent = 'Enviando imagen al servidor...';
        progressFill.style.width = '10%';
        
        // Convertir canvas a blob
        captureCanvas.toBlob(async (blob) => {
            await enviarImagenAlBackend(blob);
        }, 'image/jpeg', 0.95);
    }

    // Enviar imagen al backend
    async function enviarImagenAlBackend(blob) {
        try {
            processingText.textContent = 'Procesando imagen con IA...';
            progressFill.style.width = '30%';
            
            // Crear FormData para enviar la imagen
            const formData = new FormData();
            formData.append('imagen', blob, 'dni.jpg');
            
            // Simular progreso mientras se procesa
            const progressInterval = setInterval(() => {
                const currentWidth = parseInt(progressFill.style.width);
                if (currentWidth < 90) {
                    progressFill.style.width = (currentWidth + 5) + '%';
                }
            }, 300);
            
            // Enviar al backend
            const response = await fetch('/api/leer-dni', {
                method: 'POST',
                body: formData
            });
            
            clearInterval(progressInterval);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al procesar la imagen');
            }
            
            const resultado = await response.json();
            
            processingText.textContent = 'Extrayendo datos...';
            progressFill.style.width = '95%';
            
            console.log('Respuesta del backend:', resultado);
            
            // Verificar si hay datos
            if (!resultado.exito || !resultado.datos) {
                throw new Error('No se pudieron extraer datos del DNI');
            }
            
            progressFill.style.width = '100%';
            processingText.textContent = '¡Completado!';
            
            // Guardar datos en sessionStorage para pasarlos a la siguiente página
            sessionStorage.setItem('datosExtraidos', JSON.stringify(resultado.datos));
            
            // Redirigir a la página del formulario
            setTimeout(() => {
                window.location.href = '/formulario';
            }, 500);
            
        } catch (error) {
            console.error('Error al procesar:', error);
            processingOverlay.classList.remove('active');
            
            // Mensajes de error personalizados
            let mensajeError = 'Error al procesar el documento.';
            
            if (error.message.includes('DNI_NOT_DETECTED')) {
                mensajeError = 'No se detectó el DNI en la imagen.\nAsegúrate de que el documento sea visible y esté bien iluminado.';
            } else if (error.message.includes('INSUFFICIENT_DATA')) {
                mensajeError = 'No se pudieron extraer suficientes datos.\nIntenta capturar la imagen con mejor calidad e iluminación.';
            } else if (error.message.includes('Failed to fetch')) {
                mensajeError = 'Error de conexión con el servidor.\nVerifica que el servidor esté en funcionamiento.';
            } else {
                mensajeError = error.message;
            }
            
            alert('❌ ' + mensajeError + '\n\nPor favor, inténtelo nuevamente.');
        }
    }

}); // Fin del DOMContentLoaded