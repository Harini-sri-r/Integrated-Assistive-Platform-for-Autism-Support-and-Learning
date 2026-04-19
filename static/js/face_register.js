const video = document.getElementById('video');
const statusMessage = document.getElementById('status-message');
const startBtn = document.getElementById('start-btn');
const captureBtn = document.getElementById('capture-btn');
const videoContainer = document.getElementById('video-container');
const progressFill = document.getElementById('progress-fill');
const captureItems = document.querySelectorAll('.capture-item');

let capturedSamples = 0;
const totalSamples = 5;

// Initialize
startBtn.disabled = false;
statusMessage.innerHTML = `<i class="fas fa-camera"></i> Ready! Press 'Start Registration'`;
statusMessage.style.color = "#4ade80";

startBtn.addEventListener('click', startVideo);
captureBtn.addEventListener('click', captureFace);

function startVideo() {
    startBtn.style.display = 'none';
    videoContainer.style.display = 'block';
    statusMessage.innerText = "Starting Camera...";

    navigator.mediaDevices.getUserMedia({ video: {} })
        .then(stream => {
            video.srcObject = stream;
            video.addEventListener('play', onVideoPlay);
        })
        .catch(err => {
            console.error(err);
            statusMessage.innerText = "Camera Error: " + err.message;
            statusMessage.style.color = "#f87171";
            startBtn.style.display = 'inline-block';
            videoContainer.style.display = 'none';
        });
}

function onVideoPlay() {
    statusMessage.innerText = `Get ready to capture (${capturedSamples}/${totalSamples} samples)`;
    statusMessage.style.color = "#22c55e";
    captureBtn.style.display = 'inline-block';
}

async function captureFace() {
    if (capturedSamples >= totalSamples) return;

    captureBtn.disabled = true;
    statusMessage.innerText = "Capturing face...";
    statusMessage.style.color = "#22c55e";

    // Create canvas to capture frame
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');

    try {
        // Send to backend
        const response = await fetch('/api/face/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                label: `Sample ${capturedSamples + 1}`
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            capturedSamples++;

            // Update UI with animation
            if (captureItems[capturedSamples - 1]) {
                const item = captureItems[capturedSamples - 1];
                item.classList.remove('pending');
                item.innerHTML = '<i class="fas fa-check" style="animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);"></i>';
                item.style.borderColor = '#4ade80';
                item.style.background = 'rgba(74, 222, 128, 0.1)';
            }

            const progress = (capturedSamples / totalSamples) * 100;
            progressFill.style.width = progress + '%';

            if (capturedSamples >= totalSamples) {
                statusMessage.innerHTML = '<i class="fas fa-check-circle"></i> Registration Complete! Redirecting...';
                statusMessage.style.color = "#4ade80";
                captureBtn.style.display = 'none';

                // Add success effect to video container
                videoContainer.style.border = '2px solid #4ade80';

                // Stop video stream
                const stream = video.srcObject;
                if (stream) {
                    const tracks = stream.getTracks();
                    tracks.forEach(track => track.stop());
                }

                // Redirect to dashboard after 2 seconds
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } else {
                statusMessage.innerHTML = `<i class="fas fa-camera"></i> Success! Capture ${totalSamples - capturedSamples} more sample(s)`;
                statusMessage.style.color = "#4ade80";
                captureBtn.disabled = false;

                // Temporary flash effect
                videoContainer.style.boxShadow = '0 0 20px rgba(74, 222, 128, 0.5)';
                setTimeout(() => {
                    videoContainer.style.boxShadow = 'none';
                }, 300);
            }
        } else {
            statusMessage.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${result.error || "Could not process face"}. Try again.`;
            statusMessage.style.color = "#f87171";
            captureBtn.disabled = false;

            // Shake effect
            videoContainer.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => videoContainer.style.animation = '', 500);
        }

    } catch (error) {
        console.error(error);
        statusMessage.innerText = "Error: " + error.message;
        statusMessage.style.color = "#f87171";
        captureBtn.disabled = false;
    }
}

// Add styles for animations if not present
const style = document.createElement('style');
style.textContent = `
    @keyframes popIn {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);
