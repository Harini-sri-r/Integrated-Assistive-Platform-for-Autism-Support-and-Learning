const emojis = ['😊', '😊', '😢', '😢', '😠', '😠', '😂', '😂', '😱', '😱', '😴', '😴', '😎', '😎', '🤢', '🤢'];
let shimmerCards = emojis.sort(() => 0.5 - Math.random());

const grid = document.getElementById('game-grid');
const scoreDisplay = document.getElementById('score');
const movesDisplay = document.getElementById('moves');
const gameOverScreen = document.getElementById('game-over');

let cardsChosen = [];
let cardsChosenId = [];
let cardsWon = [];
let moves = 0;

function createBoard() {
    for (let i = 0; i < shimmerCards.length; i++) {
        const card = document.createElement('div');
        card.setAttribute('class', 'card');
        card.setAttribute('data-id', i);

        const faceBack = document.createElement('div');
        faceBack.classList.add('card-face', 'card-back');
        faceBack.innerHTML = '<i class="fas fa-question"></i>';

        const faceFront = document.createElement('div');
        faceFront.classList.add('card-face', 'card-front');
        faceFront.innerHTML = shimmerCards[i];

        card.appendChild(faceBack);
        card.appendChild(faceFront);

        card.addEventListener('click', flipCard);
        grid.appendChild(card);
    }
}

function checkForMatch() {
    const cards = document.querySelectorAll('.card');
    const optionOneId = cardsChosenId[0];
    const optionTwoId = cardsChosenId[1];

    if (optionOneId == optionTwoId) {
        cards[optionOneId].classList.remove('flipped');
        // alert('You clicked the same image!');
    } else if (cardsChosen[0] === cardsChosen[1]) {
        // Match found
        cardsWon.push(cardsChosen);
        // Disable clicking them again? They are already flipped.
        // Optional: add a "matched" glow
        cards[optionOneId].style.boxShadow = "0 0 15px #4ade80";
        cards[optionTwoId].style.boxShadow = "0 0 15px #4ade80";
    } else {
        cards[optionOneId].classList.remove('flipped');
        cards[optionTwoId].classList.remove('flipped');
    }

    cardsChosen = [];
    cardsChosenId = [];
    scoreDisplay.textContent = cardsWon.length;

    if (cardsWon.length === emojis.length / 2) {
        gameOverScreen.style.display = 'block';
        saveScore('Emotion Matcher', cardsWon.length * 10); // 10 points per pair
    }
}

function flipCard() {
    let cardId = this.getAttribute('data-id');
    if (cardsChosenId.length < 2 && !cardsChosenId.includes(cardId)) {
        if (!this.classList.contains('flipped')) {
            cardsChosen.push(shimmerCards[cardId]);
            cardsChosenId.push(cardId);
            this.classList.add('flipped');

            if (cardsChosen.length === 2) {
                moves++;
                movesDisplay.textContent = moves;
                setTimeout(checkForMatch, 500);
            }
        }
    }
}

function saveScore(game, score) {
    fetch('/api/log_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            type: game,
            score: score,
            details: `Completed in ${moves} moves`
        })
    });
}

createBoard();
