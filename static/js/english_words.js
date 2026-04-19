// english_words.js

const vocabularyData = [
    { word: "Courage", definition: "Strength in the face of pain or grief.", example: "It takes courage to try something new." },
    { word: "Kindness", definition: "The quality of being friendly, generous, and considerate.", example: "A small act of kindness can change someone's day." },
    { word: "Patience", definition: "The capacity to accept or tolerate delay, trouble, or suffering without getting angry.", example: "Learning a new skill takes time and patience." },
    { word: "Honesty", definition: "The quality of being truthful and sincere.", example: "Honesty is the foundation of a good friendship." },
    { word: "Respect", definition: "Deep admiration for someone or something elicited by their abilities, qualities, or achievements.", example: "We should show respect to all people." },
    { word: "Grateful", definition: "Feeling or showing an appreciation of kindness; thankful.", example: "I am grateful for my family and friends." },
    { word: "Friendship", definition: "A relationship between people who like and trust each other.", example: "Friendship makes our lives much happier." },
    { word: "Listen", definition: "Give one's attention to a sound.", example: "Good learners always listen carefully." }
];

let currentIndex = 0;
let quizMode = false;
let score = 0;

function updateWordCard() {
    const item = vocabularyData[currentIndex];
    document.getElementById('current-word').textContent = item.word;
    document.getElementById('current-definition').textContent = item.definition;
    document.getElementById('current-example').textContent = `"${item.example}"`;
}

function nextWord() {
    currentIndex = (currentIndex + 1) % vocabularyData.length;
    updateWordCard();
}

function prevWord() {
    currentIndex = (currentIndex - 1 + vocabularyData.length) % vocabularyData.length;
    updateWordCard();
}

function startQuiz() {
    quizMode = true;
    score = 0;
    document.getElementById('learning-section').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    showQuizQuestion();
}

let quizCount = 0;
const MAX_QUESTIONS = 5;

function showQuizQuestion() {
    const item = vocabularyData[currentIndex];
    document.getElementById('quiz-question').textContent = `Definition: "${item.definition}"`;
    document.getElementById('quiz-answer').value = '';
    document.getElementById('quiz-feedback').textContent = '';
}

function checkAnswer() {
    const userAns = document.getElementById('quiz-answer').value.trim().toLowerCase();
    const corectWord = vocabularyData[currentIndex].word.toLowerCase();

    if (userAns === corectWord) {
        document.getElementById('quiz-feedback').textContent = 'Correct! Excellence! ✨';
        document.getElementById('quiz-feedback').style.color = '#4ade80';
        score++;
        quizCount++;

        setTimeout(() => {
            currentIndex++;
            if (quizCount < MAX_QUESTIONS && currentIndex < vocabularyData.length) {
                showQuizQuestion();
            } else {
                finishQuiz();
            }
        }, 1500);
    } else {
        document.getElementById('quiz-feedback').textContent = 'Not quite. Try again!';
        document.getElementById('quiz-feedback').style.color = '#f87171';
    }
}

async function finishQuiz() {
    document.getElementById('quiz-question').textContent = `Quiz Completed! Your Score: ${score}/${MAX_QUESTIONS}`;
    document.getElementById('quiz-answer').style.display = 'none';
    document.getElementById('quiz-feedback').textContent = 'Saving your progress...';

    // Log to DB
    try {
        await fetch('/api/log_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'English Word Mastery',
                score: score,
                details: `Completed vocabulary quiz with score ${score}`
            })
        });
        document.getElementById('quiz-feedback').textContent = 'Progress saved! Redirecting...';
    } catch (e) {
        console.error("Failed to log activity", e);
    }

    setTimeout(() => {
        window.location.reload();
    }, 2000);
}

// Initialize
document.addEventListener('DOMContentLoaded', updateWordCard);
