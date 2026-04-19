const levels = [
    {
        name: "Level 1: Food Court",
        instruction: "Sort Healthy vs Unhealthy Food",
        categories: [
            { id: "healthy", name: "Healthy", icon: "fas fa-apple-alt", color: "#4ade80" },
            { id: "unhealthy", name: "Unhealthy", icon: "fas fa-cookie-bite", color: "#f87171" }
        ],
        items: [
            { icon: "🍎", cat: "healthy" }, { icon: "🥦", cat: "healthy" }, { icon: "🥕", cat: "healthy" },
            { icon: "🍔", cat: "unhealthy" }, { icon: "🍟", cat: "unhealthy" }, { icon: "🍦", cat: "unhealthy" }
        ],
        time: 30
    },
    {
        name: "Level 2: Eco Warrior",
        instruction: "Sort Trash vs Recycling",
        categories: [
            { id: "trash", name: "Trash", icon: "fas fa-trash", color: "#94a3b8" },
            { id: "recycle", name: "Recycle", icon: "fas fa-recycle", color: "#22c55e" }
        ],
        items: [
            { icon: "🍌", cat: "trash" }, { icon: "🦴", cat: "trash" }, { icon: "🚬", cat: "trash" },
            { icon: "📰", cat: "recycle" }, { icon: "🍾", cat: "recycle" }, { icon: "🥫", cat: "recycle" }
        ],
        time: 25
    }
];

let currentLevel = 0;
let timeLeft = 30;
let timerInterval;
let draggedItem = null;

function initLevel() {
    const level = levels[currentLevel];
    document.querySelector('h1').innerText = "Sorting Master: " + level.name;
    document.querySelector('p').innerText = level.instruction;

    // Setup Zones
    const zonesContainer = document.querySelector('.grid-2');
    zonesContainer.innerHTML = level.categories.map(cat => `
        <div class="drop-zone glass-card" data-category="${cat.id}"
            style="border: 2px dashed ${cat.color}; min-height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <i class="${cat.icon}" style="font-size: 3rem; color: ${cat.color}; margin-bottom: 1rem;"></i>
            <h3>${cat.name}</h3>
        </div>
    `).join('');

    // Setup Items
    const container = document.getElementById('items-container');
    container.innerHTML = '';
    level.items.sort(() => Math.random() - 0.5).forEach(item => {
        const el = document.createElement('div');
        el.className = 'draggable-item';
        el.draggable = true;
        el.innerText = item.icon;
        el.dataset.category = item.cat;

        el.addEventListener('dragstart', (e) => {
            draggedItem = el;
            el.style.opacity = '0.5';
        });
        el.addEventListener('dragend', () => {
            el.style.opacity = '1';
            draggedItem = null;
        });
        container.appendChild(el);
    });

    // Re-bind listeners
    bindZoneListeners();

    // Timer
    timeLeft = level.time;
    document.getElementById('timer-val').innerText = timeLeft;
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        document.getElementById('timer-val').innerText = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            gameOver(false);
        }
    }, 1000);
}

function bindZoneListeners() {
    document.querySelectorAll('.drop-zone').forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            if (draggedItem && draggedItem.dataset.category === zone.dataset.category) {
                zone.appendChild(draggedItem);
                draggedItem.draggable = false;
                checkWin();
            } else if (draggedItem) {
                draggedItem.style.animation = "shake 0.5s";
                setTimeout(() => draggedItem.style.animation = "", 500);
            }
        });
    });
}

function checkWin() {
    const container = document.getElementById('items-container');
    if (container.children.length === 0) {
        clearInterval(timerInterval);
        if (currentLevel < levels.length - 1) {
            currentLevel++;
            setTimeout(initLevel, 1000);
        } else {
            gameOver(true);
        }
    }
}

async function gameOver(success) {
    const msg = document.getElementById('success-msg');
    msg.style.display = 'block';
    if (success) {
        msg.innerHTML = `🎉 Champion! You sorted everything! <br> <button onclick="location.reload()" class="btn-primary mt-2">Replay</button>`;
        await fetch('/api/log_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'Memory / Logic', score: 100, details: 'Mastered all levels of Sorting Master.' })
        });
    } else {
        msg.innerHTML = `⏰ Time's Up! Try again! <br> <button onclick="location.reload()" class="btn-primary mt-2">Try Again</button>`;
    }
}

// Add Timer UI to page dynamically or update template
document.addEventListener('DOMContentLoaded', () => {
    const timerDiv = document.createElement('div');
    timerDiv.style = "font-size: 1.5rem; font-weight: bold; color: #fb7185; margin-bottom: 1rem;";
    timerDiv.innerHTML = `⏱️ Time: <span id="timer-val">30</span>s`;
    document.querySelector('.text-center').appendChild(timerDiv);

    initLevel();
});

const style = document.createElement('style');
style.innerHTML = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    75% { transform: translateX(10px); }
}
`;
document.head.appendChild(style);
