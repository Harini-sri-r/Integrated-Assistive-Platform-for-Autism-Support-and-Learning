const scenarios = [
    {
        question: "You see your friend crying at the park. What should you do?",
        icon: "😢",
        options: [
            { text: "Laugh at them", correct: false, feedback: "Laughing might make them feel worse." },
            { text: "Ask 'Are you okay?'", correct: true, feedback: "That's very kind! Checking on friends is good." },
            { text: "Ignore them", correct: false, feedback: "It's better to show you care." }
        ]
    },
    {
        question: "You accidentally bumped into someone. What do you say?",
        icon: "💥",
        options: [
            { text: "Say 'Watch out!'", correct: false, feedback: "That sounds a bit rude." },
            { text: "Say 'Sorry!'", correct: true, feedback: "Perfect! Saying sorry shows good manners." },
            { text: "Run away", correct: false, feedback: "Running away isn't polite." }
        ]
    },
    {
        question: "Someone gives you a gift you don't like. What do you do?",
        icon: "🎁",
        options: [
            { text: "Throw it away", correct: false, feedback: "That would hurt their feelings." },
            { text: "Say 'I hate this'", correct: false, feedback: "That's not very nice." },
            { text: "Say 'Thank you'", correct: true, feedback: "Yes! Always say thank you for the gesture." }
        ]
    },
    {
        question: "The teacher is talking, but you have something to say. What do you do?",
        icon: "🏫",
        options: [
            { text: "Shout it out", correct: false, feedback: "Interrupting isn't polite." },
            { text: "Raise your hand", correct: true, feedback: "Great! Raising your hand waits for your turn." },
            { text: "Whisper to a friend", correct: false, feedback: "It's better to listen to the teacher." }
        ]
    }
];

let currentScenarioIndex = 0;
let score = 0;
const questionEl = document.getElementById('scenario-question');
const iconEl = document.getElementById('scenario-icon');
const optionsGrid = document.getElementById('options-grid');
const feedbackEl = document.getElementById('feedback-area');
const nextBtn = document.getElementById('next-scenario-btn');
const scoreEl = document.getElementById('scenario-score');

function loadScenario() {
    const data = scenarios[currentScenarioIndex];
    questionEl.innerText = data.question;
    iconEl.innerText = data.icon;
    feedbackEl.innerText = '';
    feedbackEl.className = '';
    nextBtn.style.display = 'none';
    optionsGrid.innerHTML = '';

    data.options.sort(() => Math.random() - 0.5).forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'btn-secondary';
        btn.style.padding = '1rem';
        btn.style.fontSize = '1.1rem';
        btn.style.cursor = 'pointer';
        btn.style.width = '100%';
        btn.innerText = opt.text;

        btn.onclick = () => checkAnswer(opt, btn);
        optionsGrid.appendChild(btn);
    });
}

function checkAnswer(option, btnElement) {
    // Disable all buttons
    Array.from(optionsGrid.children).forEach(b => b.disabled = true);

    if (option.correct) {
        feedbackEl.innerHTML = `<span style="color: #4ade80"><i class="fas fa-check"></i> ${option.feedback}</span>`;
        btnElement.style.background = 'rgba(74, 222, 128, 0.2)';
        btnElement.style.borderColor = '#4ade80';
        score += 10;
        scoreEl.innerText = score;

        // Log
        fetch('/api/log_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'Social Adventure', score: 10, details: 'Correct answer' })
        });
    } else {
        feedbackEl.innerHTML = `<span style="color: #f87171"><i class="fas fa-times"></i> ${option.feedback}</span>`;
        btnElement.style.background = 'rgba(248, 113, 113, 0.2)';
        btnElement.style.borderColor = '#f87171';
    }

    nextBtn.style.display = 'inline-block';
}

nextBtn.addEventListener('click', () => {
    currentScenarioIndex = (currentScenarioIndex + 1) % scenarios.length;
    loadScenario();
});

loadScenario();
