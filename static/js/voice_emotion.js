const startBtn = document.getElementById('start-audio-btn');
const stopBtn = document.getElementById('stop-audio-btn');
const visualizer = document.getElementById('visualizer');
const statusDiv = document.getElementById('emotion-status');
const volumeDiv = document.getElementById('volume-level');

let audioContext;
let analyser;
let microphone;
let javascriptNode;
let isRunning = false;
let canvasContext = visualizer.getContext('2d');

startBtn.addEventListener('click', startAudio);
stopBtn.addEventListener('click', stopAudio);

function startAudio() {
    if (isRunning) return;

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            microphone = audioContext.createMediaStreamSource(stream);
            javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);

            analyser.smoothingTimeConstant = 0.8;
            analyser.fftSize = 1024;

            microphone.connect(analyser);
            analyser.connect(javascriptNode);
            javascriptNode.connect(audioContext.destination);

            javascriptNode.onaudioprocess = function () {
                const array = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(array);

                let values = 0;
                let length = array.length;
                for (let i = 0; i < length; i++) {
                    values += array[i];
                }
                const average = values / length;

                // Simple Stress Logic: High volume/intensity = "Stressed" (Approximation)
                updateUI(average, array);
            };

            isRunning = true;
            resizeCanvas();
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
        })
        .catch(err => {
            console.error(err);
            statusDiv.innerText = "Error accessing mic";
        });
}

function stopAudio() {
    if (!isRunning) return;
    microphone.disconnect();
    javascriptNode.disconnect();
    audioContext.close();
    isRunning = false;
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    statusDiv.innerText = "Waiting...";
    statusDiv.className = "status-indicator status-neutral";
}

function updateUI(volume, frequencyData) {
    volumeDiv.innerText = `Volume: ${Math.round(volume)}`;

    // Draw Visualizer
    canvasContext.clearRect(0, 0, visualizer.width, visualizer.height);
    canvasContext.fillStyle = 'rgba(34, 197, 94, 0.5)'; // Primary green color
    const barWidth = (visualizer.width / frequencyData.length) * 2.5;
    let barHeight;
    let x = 0;

    for (let i = 0; i < frequencyData.length; i++) {
        barHeight = frequencyData[i] / 2;
        canvasContext.fillRect(x, visualizer.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
    }

    // Heuristics for Emotion
    if (volume > 45) {
        statusDiv.innerText = "High Energy / Stressed";
        statusDiv.className = "status-indicator status-stressed";
        // logEmotionToServer('Stressed');
    } else if (volume > 10) {
        statusDiv.innerText = "Calm / Normal";
        statusDiv.className = "status-indicator status-calm";
    } else {
        statusDiv.innerText = "Silent";
        statusDiv.className = "status-indicator status-neutral";
    }
}

// Handle resize
window.addEventListener('resize', resizeCanvas);
function resizeCanvas() {
    visualizer.width = visualizer.offsetWidth;
    visualizer.height = visualizer.offsetHeight;
}

// Logging
let lastLog = 0;
function logEmotionToServer(state) {
    const now = Date.now();
    if (now - lastLog > 5000) {
        // Send to API
        lastLog = now;
    }
}
