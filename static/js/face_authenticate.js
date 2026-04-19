const video = document.getElementById('video');
const authStatus = document.getElementById('auth-status');
const startBtn = document.getElementById('start-btn');
const videoContainer = document.getElementById('video-container');

let isAuthenticating = false;

// Initialize
startBtn.disabled = false;
authStatus.innerHTML = `<i class="fas fa-video"></i> Ready! Press 'Start Camera'`;
authStatus.className = 'auth-status';

startBtn.addEventListener('click', startVideo);

function startVideo() {
    startBtn.style.display = 'none';
    videoContainer.style.display = 'block';
    authStatus.innerText = "Starting Camera...";
    authStatus.className = 'auth-status status-scanning';

    navigator.mediaDevices.getUserMedia({ video: {} })
        .then(stream => {
            video.srcObject = stream;
            video.addEventListener('play', onVideoPlay);
        })
        .catch(err => {
            console.error(err);
            authStatus.innerText = "Camera Error: " + err.message;
            authStatus.className = 'auth-status status-error';
            startBtn.style.display = 'inline-block';
            videoContainer.style.display = 'none';
        });
}

function onVideoPlay() {
    authStatus.innerText = "Scanning for faces...";
    authStatus.className = 'auth-status status-scanning';

    // Create a hidden canvas to capture frames
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    // Continuous face recognition interval
    const intervalId = setInterval(async () => {
        if (video.paused || video.ended || isAuthenticating) return;

        // Capture frame
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg');

        // Attempt authentication
        await authenticateWithFace(imageData, intervalId);

    }, 2000); // Check every 2 seconds to avoid overloading server
}

async function authenticateWithFace(imageData, intervalId) {
    if (isAuthenticating) return;

    isAuthenticating = true;
    authStatus.innerText = "Recognizing...";
    // authStatus.className = 'auth-status status-scanning'; // Keep scanning style

    try {
        const response = await fetch('/api/face/authenticate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData
            })
        });

        const result = await response.json();

        if (result.success) {
            clearInterval(intervalId); // Stop checking
            authStatus.innerHTML = `<i class="fas fa-check-circle"></i> Welcome, ${result.username}!`;
            authStatus.className = 'auth-status status-success';

            // Visual success indicator
            videoContainer.style.border = '3px solid #4ade80';
            videoContainer.style.boxShadow = '0 0 30px rgba(74, 222, 128, 0.4)';

            // Stop video stream
            const stream = video.srcObject;
            if (stream) {
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
            }

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = result.redirect;
            }, 1000);
        } else {
            console.log("Auth failed:", result.message);

            // Update UI only if status message needs refreshing (avoid flickering)
            if (authStatus.innerText !== "Scanning...") {
                authStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
                // Add subtle pulse effect
                videoContainer.classList.add('scanning-pulse');
            }

            // If debugging or explicit failure needed:
            // authStatus.innerText = "Face not recognized. Scanning...";

            isAuthenticating = false;
        }

    } catch (error) {
        console.error(error);
        authStatus.innerText = "Connection error. Retrying...";
        authStatus.className = 'auth-status status-error';
        isAuthenticating = false;
    }
}
