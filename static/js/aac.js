const synth = window.speechSynthesis;
const sentenceStrip = document.getElementById('sentence-strip');
const btnPlay = document.getElementById('btn-play-sentence');
const btnClear = document.getElementById('btn-clear-sentence');
const btnSave = document.getElementById('btn-save-favorite');
const gridFavorites = document.getElementById('grid-favorites');
const favSection = document.getElementById('favorites-section');

let sentence = [];

// Data
const aacData = {
    basics: [
        { icon: "👍", text: "Yes" }, { icon: "👎", text: "No" }, { icon: "👋", text: "Hello" },
        { icon: "🙏", text: "Thank You" }, { icon: "🚽", text: "Toilet" }, { icon: "💧", text: "Water" },
        { icon: "🍽️", text: "Food" }, { icon: "🛑", text: "Stop" }, { icon: "❔", text: "Help" },
        { icon: "💡", text: "Idea" }, { icon: "👂", text: "Listen" }, { icon: "👀", text: "Look" }
    ],
    people: [
        { icon: "👩", text: "Mom" }, { icon: "👨", text: "Dad" }, { icon: "👵", text: "Grandma" },
        { icon: "👴", text: "Grandpa" }, { icon: "🧑‍🤝‍🧑", text: "Friend" }, { icon: "👩‍🏫", text: "Teacher" }
    ],
    feelings: [
        { icon: "😊", text: "Happy" }, { icon: "😢", text: "Sad" }, { icon: "😠", text: "Angry" },
        { icon: "😨", text: "Scared" }, { icon: "😴", text: "Tired" }, { icon: "🤒", text: "Sick" },
        { icon: "😋", text: "Hungry" }, { icon: "🥳", text: "Excited" }, { icon: "🤫", text: "Quiet" }
    ],
    food: [
        { icon: "🍎", text: "Apple" }, { icon: "🍌", text: "Banana" }, { icon: "🥛", text: "Milk" },
        { icon: "🍕", text: "Pizza" }, { icon: "🍪", text: "Cookie" }, { icon: "🍦", text: "Ice Cream" },
        { icon: "🥪", text: "Sandwich" }, { icon: "🥤", text: "Juice" }
    ],
    places: [
        { icon: "🏠", text: "Home" }, { icon: "🏫", text: "School" }, { icon: "🌳", text: "Park" },
        { icon: "🛒", text: "Shop" }, { icon: "🏥", text: "Hospital" }, { icon: "🛀", text: "Bathroom" }
    ],
    activities: [
        { icon: "🎮", text: "Play" }, { icon: "📖", text: "Read" }, { icon: "🎨", text: "Draw" },
        { icon: "💤", text: "Sleep" }, { icon: "🚶", text: "Walk" }, { icon: "📺", text: "Watch TV" },
        { icon: "🎵", text: "Music" }, { icon: "🌳", text: "Outside" }
    ],
    social: [
        { icon: "🤝", text: "Share" }, { icon: "🫂", text: "Hug" }, { icon: "✋", text: "Wait" },
        { icon: "👄", text: "My Turn" }, { icon: "👈", text: "Your Turn" }, { icon: "🤫", text: "Soft Voice" }
    ]
};

let voices = [];
function loadVoices() {
    voices = synth.getVoices();
}
loadVoices();
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
}

function speak(text) {
    if (!text) return;

    // Cancel any ongoing speech to prevent queueing/freezing
    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Select a friendly English voice if available
    const preferredVoice = voices.find(v => v.lang.includes('en-') && v.name.includes('Google')) || voices.find(v => v.lang.includes('en-'));
    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;

    synth.speak(utterance);
}

function addToSentence(text) {
    const placeholder = document.getElementById('strip-placeholder');
    if (placeholder) placeholder.remove();

    sentence.push(text);

    const chip = document.createElement('span');
    chip.className = 'sentence-chip';
    chip.innerText = text;
    sentenceStrip.appendChild(chip);

    // Auto-speak individual click
    speak(text);
}

btnPlay.onclick = () => {
    const fullText = sentence.join(' ');
    if (fullText) {
        speak(fullText);
        logActivity('AAC Usage', 1, `Said: "${fullText}"`);
    }
};

btnClear.onclick = () => {
    sentence = [];
    sentenceStrip.innerHTML = '<span class="text-muted" id="strip-placeholder">Tap icons below to build a sentence...</span>';
};

btnSave.onclick = () => {
    const fullText = sentence.join(' ');
    if (!fullText) return;

    let favorites = JSON.parse(localStorage.getItem('aac_favorites') || '[]');
    if (!favorites.includes(fullText)) {
        favorites.push(fullText);
        localStorage.setItem('aac_favorites', JSON.stringify(favorites));
        renderFavorites();
        alert('Saved to favorites!');
    }
};

function renderCategory(catName, containerId) {
    const grid = document.getElementById(containerId);
    if (!grid || !aacData[catName]) return;

    grid.innerHTML = '';
    aacData[catName].forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'aac-btn glass-card';
        btn.innerHTML = `
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">${item.icon}</div>
            <div style="font-weight: bold; font-size: 1rem;">${item.text}</div>
        `;
        btn.style.padding = '1rem';
        btn.onclick = () => addToSentence(item.text);
        grid.appendChild(btn);
    });
}

function renderFavorites() {
    const favorites = JSON.parse(localStorage.getItem('aac_favorites') || '[]');
    if (favorites.length === 0) {
        favSection.style.display = 'none';
        return;
    }

    favSection.style.display = 'block';
    gridFavorites.innerHTML = '';
    favorites.forEach((fav, index) => {
        const btn = document.createElement('button');
        btn.className = 'aac-btn glass-card';
        btn.style.borderColor = '#22c55e';
        btn.innerHTML = `
            <div style="font-size: 1rem; font-weight: bold;">${fav}</div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;" onclick="deleteFavorite(${index}, event)">[Remove]</div>
        `;
        btn.style.padding = '1rem';
        btn.onclick = (e) => {
            if (e.target.tagName !== 'DIV' || !e.target.innerText.includes('Remove')) {
                speak(fav);
                logActivity('AAC Usage', 1, `Said favorite: "${fav}"`);
            }
        };
        gridFavorites.appendChild(btn);
    });
}

window.deleteFavorite = (index, event) => {
    event.stopPropagation();
    let favorites = JSON.parse(localStorage.getItem('aac_favorites') || '[]');
    favorites.splice(index, 1);
    localStorage.setItem('aac_favorites', JSON.stringify(favorites));
    renderFavorites();
};

async function logActivity(type, score, details) {
    try {
        await fetch('/api/log_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, score, details })
        });
    } catch (e) {
        console.error("Failed to log AAC activity", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const categories = [
        { name: 'basics', grid: 'grid-basics' },
        { name: 'people', grid: 'grid-people' },
        { name: 'feelings', grid: 'grid-emotions' },
        { name: 'food', grid: 'grid-food' },
        { name: 'places', grid: 'grid-places' },
        { name: 'activities', grid: 'grid-activities' },
        { name: 'social', grid: 'grid-social' }
    ];

    categories.forEach(cat => renderCategory(cat.name, cat.grid));
    renderFavorites();
});
