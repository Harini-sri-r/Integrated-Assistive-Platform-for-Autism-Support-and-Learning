const video = document.getElementById('video');
const emotionLabel = document.getElementById('emotion-label');
const startBtn = document.getElementById('start-btn');
let isModelLoaded = false;

// Load models
// Using local models for maximum stability
// Standard face-api.js models path:
// const MODEL_URL = 'https://justadudewhohacks.github.io/face-api.js/models';

// LOCAL PATH
const MODEL_URL = '/static/models';

Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
    faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
    faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
]).then(() => {
    isModelLoaded = true;
    emotionLabel.innerText = "AI Models Ready! Click 'Start Camera'.";
    emotionLabel.style.color = "#4ade80";
    startBtn.disabled = false;
    startBtn.style.display = "inline-block";
    console.log("Models loaded successfully");
}).catch(err => {
    console.error("Error loading models:", err);
    emotionLabel.innerText = "Error loading AI models. Check console/internet.";
    emotionLabel.style.color = "#f87171";
});

startBtn.addEventListener('click', startVideo);

function startVideo() {
    if (!isModelLoaded) return;

    startBtn.style.display = 'none';
    emotionLabel.innerText = "Starting Camera...";

    navigator.mediaDevices.getUserMedia({ video: {} })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error(err);
            emotionLabel.innerText = "Camera Error: " + err.message;
            emotionLabel.style.color = "#f87171";
            startBtn.style.display = 'inline-block';
        });
}

video.addEventListener('play', () => {
    const canvas = faceapi.createCanvasFromMedia(video);
    document.getElementById('video-container').append(canvas);
    const displaySize = { width: video.width, height: video.height };
    faceapi.matchDimensions(canvas, displaySize);

    setInterval(async () => {
        if (video.paused || video.ended || !isModelLoaded) return;

        try {
            const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();

            const resizedDetections = faceapi.resizeResults(detections, displaySize);
            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

            faceapi.draw.drawDetections(canvas, resizedDetections);
            faceapi.draw.drawFaceExpressions(canvas, resizedDetections);

            if (detections.length > 0) {
                const expressions = detections[0].expressions;
                const maxEmotion = Object.keys(expressions).reduce((a, b) => expressions[a] > expressions[b] ? a : b);
                emotionLabel.innerText = `You look ${maxEmotion}!`;
                emotionLabel.style.color = "#fff";
            } else {
                emotionLabel.innerText = "Looking for a face...";
                emotionLabel.style.color = "#cbd5e1";
            }
        } catch (error) {
            console.error(error);
        }
    }, 100);
});
