const steps = [
    { id: 1, text: "Wake Up", icon: "☀️" },
    { id: 2, text: "Brush Teeth", icon: "🪥" },
    { id: 3, text: "Eat Breakfast", icon: "🥣" },
    { id: 4, text: "Pack Bag", icon: "🎒" },
    { id: 5, text: "Go to School", icon: "🚌" }
];

// Shuffle for display
let shuffledSteps = [...steps].sort(() => 0.5 - Math.random());

const sourceList = document.getElementById('source-list');
const targetList = document.getElementById('target-list');
const checkBtn = document.getElementById('check-btn');
const messageArea = document.getElementById('message-area');
const placeholder = document.getElementById('placeholder-text');

function renderSource() {
    sourceList.innerHTML = '';
    shuffledSteps.forEach((step, index) => {
        if (!step.selected) {
            const btn = document.createElement('div');
            btn.className = 'glass-card';
            btn.style.cursor = 'pointer';
            btn.style.display = 'flex';
            btn.style.alignItems = 'center';
            btn.style.gap = '1rem';
            btn.innerHTML = `<span style="font-size: 1.5rem;">${step.icon}</span> <span>${step.text}</span>`;

            btn.onclick = () => selectStep(step.id);
            sourceList.appendChild(btn);
        }
    });
}

let usersRoutine = [];

function selectStep(id) {
    const stepDef = steps.find(s => s.id === id);
    // Remove from shuffle view logic (visually)
    // We'll just maintain a 'selected' state in a separate array or map
    // Simpler: rebuild standard lists

    const index = shuffledSteps.findIndex(s => s.id === id);
    if (index > -1) {
        shuffledSteps[index].selected = true;
        usersRoutine.push(stepDef);
        render();
    }
}

function deselectStep(index) {
    const step = usersRoutine[index];
    usersRoutine.splice(index, 1);

    // Find in shuffled and unmark
    const sIndex = shuffledSteps.findIndex(s => s.id === step.id);
    shuffledSteps[sIndex].selected = false;
    render();
}

function render() {
    // Render Source
    sourceList.innerHTML = '';
    shuffledSteps.forEach(step => {
        if (!step.selected) {
            const el = document.createElement('div');
            el.className = 'glass-card';
            el.style.cursor = 'pointer';
            el.style.padding = '1rem';
            el.innerHTML = `<span style="font-size: 1.5rem;">${step.icon}</span> ${step.text}`;
            el.onclick = () => selectStep(step.id);
            sourceList.appendChild(el);
        }
    });

    // Render Target
    targetList.innerHTML = '';
    if (usersRoutine.length === 0) {
        targetList.appendChild(placeholder);
        checkBtn.style.display = 'none';
    } else {
        usersRoutine.forEach((step, idx) => {
            const el = document.createElement('div');
            el.className = 'glass-card';
            el.style.cursor = 'pointer';
            el.style.background = 'rgba(74, 222, 128, 0.2)'; // Greenish tint
            el.innerHTML = `<strong>${idx + 1}.</strong> <span style="font-size: 1.5rem;">${step.icon}</span> ${step.text}`;
            el.onclick = () => deselectStep(idx);
            targetList.appendChild(el);
        });
        checkBtn.style.display = 'block';
    }
}

checkBtn.onclick = () => {
    // Check order
    let isCorrect = true;
    for (let i = 0; i < usersRoutine.length; i++) {
        if (usersRoutine[i].id !== (i + 1)) {
            isCorrect = false;
            break;
        }
    }

    if (isCorrect && usersRoutine.length === steps.length) {
        messageArea.innerHTML = '<span style="color: #4ade80; font-size: 1.5rem;">Correct! Good Job! 🎉</span>';
        saveScore();
    } else {
        messageArea.innerHTML = '<span style="color: #f87171;">Not quite right. Try again!</span>';
    }
};

function saveScore() {
    fetch('/api/log_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            type: 'Routine Builder',
            score: 100,
            details: 'Completed Morning Routine'
        })
    });
}

render();
