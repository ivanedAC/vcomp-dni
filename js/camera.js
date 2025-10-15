// This file handles camera management and automatic detection, providing functionality to access and control the camera.

const video = document.createElement('video');
const constraints = {
    video: {
        facingMode: 'environment', // Use the rear camera
        width: { ideal: 1280 },
        height: { ideal: 720 }
    }
};

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        video.setAttribute('playsinline', true); // Required to tell iOS safari we don't want fullscreen
        video.play();
    } catch (error) {
        console.error("Error accessing the camera: ", error);
    }
}

function stopCamera() {
    const stream = video.srcObject;
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }
    video.srcObject = null;
}

function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
}

export { startCamera, stopCamera, captureImage };