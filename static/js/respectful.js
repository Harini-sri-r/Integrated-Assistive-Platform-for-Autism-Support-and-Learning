// respectful.js

const scenarios = [
    {
        text: "A friend is telling you a story about their weekend, but you are excited to talk about your new toy. What do you do?",
        options: [
            { text: "Interrupt them to talk about your toy.", correct: false, feedback: "It's better to wait until they finish their story." },
            { text: "Listen carefully and wait for them to finish.", correct: true, feedback: "Great! Listening shows you value what they have to say." },
            { text: "Look away and wait for them to stop talking.", correct: false, feedback: "Looking away can seem like you aren't interested." }
        ]
    },
    {
        text: "Your teacher is explaining a new game, but you already know how to play. What is the respectful choice?",
        options: [
            { text: "Shout out that you already know it.", correct: false, feedback: "Others might be learning for the first time." },
            { text: "Talk to your neighbor while the teacher is talking.", correct: false, feedback: "This can be distracting for the teacher and others." },
            { text: "Listen quietly so others can learn too.", correct: true, feedback: "Perfect! Being patient helps everyone learn." }
        ]
    },
    {
        text: "You accidentally bumped into someone in the hallway. What should you say?",
        options: [
            { text: "Ignore them and keep walking.", correct: false, feedback: "Ignoring it might make them feel bad." },
            { text: "Say 'Excuse me' or 'I'm sorry'.", correct: true, feedback: "Yes! Simple polite words show you care about others." },
            { text: "Tell them to watch where they are going.", correct: false, feedback: "Being unkind usually makes the situation worse." }
        ]
    },
    {
        text: "Your classmate is struggling to tie their shoes. What do you do?",
        options: [
            { text: "Laugh at them for not knowing how.", correct: false, feedback: "Everyone learns at different speeds. Kindness is key." },
            { text: "Ask if they would like some help.", correct: true, feedback: "Excellent! Offering help is a very respectful thing to do." },
            { text: "Walk past them without saying anything.", correct: false, feedback: "You could have offered a helping hand." }
        ]
    },
    {
        text: "You want to play with a toy that someone else is using. What should you do?",
        options: [
            { text: "Grab it from their hands.", correct: false, feedback: "Grabbing is unkind. Always ask first!" },
            { text: "Ask 'Can I have a turn when you are finished?'", correct: true, feedback: "Yes! Waiting and asking politely is very respectful." },
            { text: "Wait for them to drop it and then take it.", correct: false, feedback: "It's better to talk to them and ask for a turn." }
        ]
    },
    {
        text: "You feel frustrated because a game is hard. How should you act?",
        options: [
            { text: "Throw the game pieces on the floor.", correct: false, feedback: "Throwing things can be dangerous and unkind." },
            { text: "Take a deep breath and ask for help.", correct: true, feedback: "That's a great strategy! Asking for help is a brave and respectful choice." },
            { text: "Shout at the person playing with you.", correct: false, feedback: "Using a soft voice is much better when you feel frustrated." }
        ]
    }
];

let currentScenarioIndex = 0;
let score = 0;

function loadScenario() {
    const scenario = scenarios[currentScenarioIndex];
    const scenarioText = document.getElementById('scenario-text');
    const optionsContainer = document.getElementById('options-container');

    scenarioText.textContent = scenario.text;
    optionsContainer.innerHTML = '';

    scenario.options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'btn-secondary';
        btn.style.textAlign = 'left';
        btn.style.padding = '1rem';
        btn.style.width = '100%';
        btn.textContent = option.text;
        btn.onclick = () => handleOptionClick(option);
        optionsContainer.appendChild(btn);
    });
}

function handleOptionClick(option) {
    if (option.correct) {
        score++;
        alert("Correct! " + option.feedback);
    } else {
        alert("Not quite. " + option.feedback);
    }

    currentScenarioIndex++;
    if (currentScenarioIndex < scenarios.length) {
        loadScenario();
    } else {
        finishChallenge();
    }
}

async function finishChallenge() {
    document.getElementById('scenario-section').style.display = 'none';
    const resultContainer = document.getElementById('result-container');
    resultContainer.style.display = 'block';

    document.getElementById('result-text').textContent = `You completed the Respectful Learner challenge with a score of ${score}/${scenarios.length}!`;

    try {
        await fetch('/api/log_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'Respectful Learner',
                score: score,
                details: `Completed social skills scenarios with score ${score}/${scenarios.length}`
            })
        });
    } catch (e) {
        console.error("Failed to log activity", e);
    }
}

document.addEventListener('DOMContentLoaded', loadScenario);
