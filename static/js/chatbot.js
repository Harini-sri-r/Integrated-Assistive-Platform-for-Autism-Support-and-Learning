const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const suggestionsContainer = document.getElementById('suggestions-container');
const ttsBtn = document.getElementById('tts-btn');

let ttsEnabled = false; // Default to false to not startle users

// Initialize TTS Button state
if (ttsBtn) {
    ttsBtn.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        if (ttsEnabled) {
            ttsBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            ttsBtn.style.color = '#10b981'; // green when on
        } else {
            ttsBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            ttsBtn.style.color = '#9ca3af'; // gray when off
            window.speechSynthesis.cancel(); // stop current speech
        }
    });
    // Set initial styling to match default disabled state
    ttsBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
    ttsBtn.style.color = '#9ca3af';
}


// Markdown parser
function parseMarkdown(text) {
    let parsedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    parsedText = parsedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
    parsedText = parsedText.replace(/\n/g, '<br>');
    return parsedText;
}

// Time formater
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    msgDiv.innerHTML = parseMarkdown(text);
    
    // Add timestamp
    const timeDiv = document.createElement('div');
    timeDiv.classList.add('message-time');
    timeDiv.textContent = getCurrentTime();
    msgDiv.appendChild(timeDiv);

    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    // Speak if bot and TTS is enabled
    if (sender === 'bot' && ttsEnabled && 'speechSynthesis' in window) {
        // Strip markdown styling out for natural voice reading
        const plainText = text.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1').replace(/#/g, '');
        const utterance = new SpeechSynthesisUtterance(plainText);
        utterance.rate = 1.0;
        utterance.pitch = 1.1; 
        window.speechSynthesis.speak(utterance);
    }

}

function renderSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';
    if (!suggestions || suggestions.length === 0) return;

    suggestions.forEach(suggestion => {
        const pill = document.createElement('button');
        pill.classList.add('suggestion-pill');
        pill.textContent = suggestion;
        pill.onclick = () => {
            chatInput.value = suggestion;
            sendMessage();
        };
        suggestionsContainer.appendChild(pill);
    });
}

function clearSuggestions() {
    suggestionsContainer.innerHTML = '';
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    chatInput.value = '';
    clearSuggestions();

    // typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot-message');
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();

        // Remove typing indicator
        const currentTyping = document.getElementById('typing-indicator');
        if (currentTyping) currentTyping.remove();

        appendMessage(data.response, 'bot');
        if (data.suggestions) {
            renderSuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('Error:', error);
        
        // Remove typing indicator
        const currentTyping = document.getElementById('typing-indicator');
        if (currentTyping) currentTyping.remove();

        appendMessage("Sorry, I'm having trouble connecting right now.", 'bot');
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onstart = function() {
        micBtn.classList.add('recording');
        chatInput.placeholder = "Listening...";
    };

    recognition.onresult = function(event) {
        const currentText = event.results[0][0].transcript;
        chatInput.value = currentText;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
        micBtn.classList.remove('recording');
        chatInput.placeholder = "Type a message...";
    };

    recognition.onend = function() {
        micBtn.classList.remove('recording');
        chatInput.placeholder = "Type a message...";
    };

    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('recording')) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
} else {
    micBtn.style.display = 'none'; // Hide if not supported
    console.warn('Speech recognition not supported in this browser.');
}
