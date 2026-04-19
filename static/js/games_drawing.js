const canvas = document.getElementById('drawing-canvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let currentColor = '#000000';
let currentLineWidth = 5;

// Set initial styles
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.lineWidth = currentLineWidth;

// Functions
function draw(e) {
    if (!isDrawing) return;

    // Get mouse pos relative to canvas
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches[0].clientX) - rect.left;
    const y = (e.clientY || e.touches[0].clientY) - rect.top;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();

    [lastX, lastY] = [x, y];
}

canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    [lastX, lastY] = [e.clientX - rect.left, e.clientY - rect.top];
});
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', () => isDrawing = false);
canvas.addEventListener('mouseout', () => isDrawing = false);

// Touch support
canvas.addEventListener('touchstart', (e) => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    [lastX, lastY] = [touch.clientX - rect.left, touch.clientY - rect.top];
    e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchmove', (e) => {
    draw(e);
    e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchend', () => isDrawing = false);


// Tools
document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Remove active class from all
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        // Logic
        currentColor = getComputedStyle(e.target).backgroundColor;
        ctx.strokeStyle = currentColor;
        ctx.globalCompositeOperation = 'source-over';
        ctx.lineWidth = 5;
    });
});

document.getElementById('btn-eraser').addEventListener('click', () => {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.lineWidth = 20;
});

document.getElementById('btn-clear').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

document.getElementById('btn-save').addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'my-drawing.png';
    link.href = canvas.toDataURL();
    link.click();

    // Log activity
    fetch('/api/log_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'Creative Studio', score: 10, details: 'Saved a drawing' })
    });
});

// Tracing Logic
const overlay = document.getElementById('overlay-letter');
document.querySelectorAll('.trace-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        overlay.innerText = e.target.dataset.char;
        overlay.style.display = 'block';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
});
document.getElementById('btn-free').addEventListener('click', () => {
    overlay.style.display = 'none';
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});
