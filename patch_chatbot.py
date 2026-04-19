import sys
import re

with open('static/js/chatbot.js', 'r', encoding='utf-8') as f:
    content = f.read()

tts_init = """const ttsBtn = document.getElementById('tts-btn');

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
"""

if 'let ttsEnabled' not in content:
    content = content.replace("const suggestionsContainer = document.getElementById('suggestions-container');", "const suggestionsContainer = document.getElementById('suggestions-container');\n" + tts_init)

tts_logic = """
    // Speak if bot and TTS is enabled
    if (sender === 'bot' && ttsEnabled && 'speechSynthesis' in window) {
        // Strip markdown styling out for natural voice reading
        const plainText = text.replace(/\\*\\*(.*?)\\*\\*/g, '$1').replace(/\\*(.*?)\\*/g, '$1').replace(/#/g, '');
        const utterance = new SpeechSynthesisUtterance(plainText);
        utterance.rate = 1.0;
        utterance.pitch = 1.1; 
        window.speechSynthesis.speak(utterance);
    }
"""

if '// Speak if bot and TTS is enabled' not in content:
    # We replace the closing brace of appendMessage
    content = content.replace("    chatHistory.scrollTop = chatHistory.scrollHeight;\n}", "    chatHistory.scrollTop = chatHistory.scrollHeight;" + tts_logic + "\n}")

with open('static/js/chatbot.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Patched chatbot.js')
