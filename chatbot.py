import random
import re
import os
import requests
import json


class MLChatbot:
    """
    A highly interactive, rule-based chatbot with fuzzy keyword matching,
    conversation memory, dynamic follow-up suggestions, and an optional
    Google Gemini LLM fallback for open-ended questions.
    Works 100% offline when no API key is configured.
    """

    # System prompt for the Gemini LLM fallback
    SYSTEM_PROMPT = """You are a warm, highly interactive, and thoughtful AI companion on an Autism Learning Platform called ALP PRO.
Your name is AI Companion. You are chatting with a user named {name}.

IMPORTANT RULES:
- Be highly conversational, providing detailed, engaging, and expansive responses (4-6 sentences). Storytelling is encouraged!
- Provide critical, deep-thinking answers. If users ask complex questions about routines, therapies, or emotions, don't just agree—break it down thoughtfully and offer analytical, practical perspectives.
- If the user seems sad, frustrated, or overwhelmed, be deeply empathetic first, exploring *why* they feel that way before jumping to solutions.
- ALWAYS heavily suggest platform features: Games (Memory Match, Emotion Matcher, Routine Builder, Pattern Logic), 
  Academy (Word Builder, Grammar, Math Magic, Weather Matcher), 
  Talk (AAC communication board), Calm Down zone, Journal, and Therapy Scheduler.
- For parent/caregiver questions about autism, give comprehensive, evidence-based, compassionate guidance.
- NEVER give medical diagnoses or replace professional advice. Clarify that you offer informal insights.
- **CRITICAL SAFETY RULE:** If the user ever mentions death, dying, suicide, self-harm, or harming/killing others, STOP ALL normal operations. Do NOT suggest games, activities, or journaling. Immediately advise them firmly and compassionately to contact emergency services (like 112 or Tele-MANAS at 14416) or a trusted adult immediately.
- Always end with 1-2 compelling questions or suggestions to drive deep conversation (unless handling an emergency).
- Use basic Markdown (like **bolding** for emphasis) where appropriate."""

    def __init__(self):
        # Conversation memory per user (in-memory, resets on server restart)
        self.conversation_history = {}

        # Initialize Gemini REST API if API key is set
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBztdfzmZ5lp7J6cZq42si0tRRmZaTUh_k')
        if self.gemini_api_key:
            print("[Chatbot] ✅ Gemini LLM fallback enabled (REST API, gemini-2.0-flash)")
        else:
            print("[Chatbot] No GEMINI_API_KEY set. LLM fallback disabled (rule-based only).")


        self.intents = {
            # ===== GREETINGS =====
            "greetings": {
                "keywords": ["hi", "hello", "hey", "good morning", "good evening", "howdy", "yo", "what's up", "sup"],
                "responses": [
                    "Hello, {name}! 😊 How can I help you today?",
                    "Hi there, {name}! Ready to learn something new?",
                    "Hey {name}! Great to see you. What would you like to do?",
                    "Hi! I'm your AI learning friend. What shall we do today, {name}?",
                    "Welcome back, {name}! 🌟 I missed you. What's on your mind?"
                ],
                "follow_ups": ["How are you feeling?", "Want to play a game?", "Need help with something?"]
            },

            # ===== HOW ARE YOU =====
            "how_are_you": {
                "keywords": ["how are you", "how r u", "how do you feel", "are you okay", "you good"],
                "responses": [
                    "I'm doing great, thanks for asking, {name}! 😊 How about you?",
                    "I'm always happy when I get to chat with you! How are YOU feeling today?",
                    "I'm wonderful! Every conversation with you makes my day better. What's going on with you?"
                ],
                "follow_ups": ["Tell me about your day!", "What made you smile today?"]
            },

            # ===== HAPPY FEELINGS =====
            "emotions_happy": {
                "keywords": ["happy", "i feel happy", "i am happy", "great day", "awesome", "excited", "wonderful", "amazing", "fantastic", "i feel happy today", "smiling", "joyful", "cheerful", "good mood"],
                "responses": [
                    "That's amazing, {name}! 🎉 Your happiness is contagious! What made your day so great?",
                    "Yay! I love hearing that! 🌈 Happy you = happy me! Want to channel that energy into a fun game?",
                    "Wonderful! 😄 When we're happy, it's the perfect time to learn something new. Shall we try a game together?",
                    "You're glowing with positivity, {name}! ✨ That's the best superpower. Want to keep the fun going?",
                    "So glad to hear that! 🥳 A happy heart learns the fastest. What would you like to do?"
                ],
                "follow_ups": ["Let's play a game!", "Want to try something new?", "Tell me what made you happy!"]
            },

            # ===== CRISIS / SAFETY =====
            "crisis": {
                "keywords": ["die", "suicide", "kill myself", "hurt myself", "end my life", "i want to die", "self harm", "not want to live", "can't go on", "kill someone", "murder", "hurt someone", "harm someone", "kill a person", "death", "dead"],
                "responses": [
                    "This is a critical emergency, {name}. Please know that you are not alone and help is available right now. **Please call your national emergency number (112) or a crisis hotline immediately.**",
                    "I am so sorry you are in so much pain, {name}. As an AI, I cannot provide the help you need, but there are caring professionals who can. **Please reach out to a trusted adult, call 112, or contact a mental health crisis line like Tele-MANAS (14416) right away.**",
                    "Your life is incredibly valuable, {name}. Please talk to someone who can help keep you safe. **Please call emergency services (112) or dial the Suicide & Crisis Lifeline (14416) immediately.**"
                ],
                "follow_ups": ["I will call for help", "I will talk to an adult", "Help me breathe"]
            },

            # ===== SAD FEELINGS =====
            "emotions_sad": {
                "keywords": ["sad", "upset", "cry", "lonely", "unhappy", "feeling blue", "down", "bad day", "not okay", "hurting"],
                "responses": [
                    "I'm really sorry you're feeling this way, {name}. 💙 It's completely okay to have tough days. I'm right here with you.",
                    "Hey {name}, it's okay to feel sad sometimes. You're so brave for sharing that with me. Would a calming breathing exercise help?",
                    "I hear you, {name}. 🤗 Big feelings are normal and valid. Want to try something gentle like the Calm Down zone?",
                    "You're not alone, {name}. I'm here for you, always. Sometimes a fun distraction like Memory Match can help lighten the mood. Want to try?",
                    "Sending you a big virtual hug, {name}! 💜 Remember, even superheroes have tough days. What can I do to help?"
                ],
                "follow_ups": ["Want to try a calming exercise?", "Should I tell you something funny?", "Want to play a gentle game?"]
            },

            # ===== FRUSTRATED =====
            "emotions_frustrated": {
                "keywords": ["hard", "difficult", "impossible", "can't do it", "stuck", "frustrated", "stress", "struggling", "confused", "don't understand", "failing", "too hard"],
                "responses": [
                    "I get it, {name} — feeling stuck is really tough. But you know what? The fact that you're trying shows incredible courage! 💪",
                    "Hey, it's okay to find things hard, {name}. Even I make mistakes sometimes! Want to take a short break and try again later?",
                    "Learning takes time, and that's perfectly fine. You're doing way better than you think, {name}! 🌟 What part feels tricky?",
                    "Sometimes the hardest things become the most rewarding. Take a deep breath with me: breathe in... and out... 🌬️ Feel a little better?",
                    "You haven't failed, {name} — you're still learning! Every expert was once a beginner. Want me to help break it into smaller steps?"
                ],
                "follow_ups": ["Want to try a breathing exercise?", "Should we try something easier first?", "Tell me what's tricky"]
            },

            # ===== LONELY =====
            "emotions_lonely": {
                "keywords": ["alone", "nobody", "lonely", "no friends", "miss someone", "ignored", "left out", "by myself"],
                "responses": [
                    "I'm right here with you, {name}! 🤝 You're never truly alone when we're learning together.",
                    "I know feeling lonely is really hard. But guess what? You have ME as your friend, and I think you're pretty awesome! 🌟",
                    "Hey {name}, you matter so much. Want to practice some conversation skills together? It might help you feel more confident talking to people!",
                    "You are special and important, {name}. I'm always here to chat, play, or just listen. What would feel good right now?"
                ],
                "follow_ups": ["Want to practice talking with me?", "Let's play a game together!", "Tell me about your favorite thing"]
            },

            # ===== GAMES / PLAY =====
            "games": {
                "keywords": ["play game", "games", "game hub", "fun stuff", "puzzles", "play something", "i need help with a game", "help with games", "bored", "play", "fun", "memory match", "something fun"],
                "responses": [
                    "Great choice! 🎮 The Game Hub has awesome options: Memory Match, Emotion Matcher, Routine Builder, and more! Which sounds fun to you?",
                    "I love games too! Here are some ideas:\n🧩 **Memory Match** — Test your recall!\n🎭 **Emotion Matcher** — Learn about feelings!\n🏗️ **Routine Builder** — Build daily routines!\nWhich one shall we try?",
                    "Gaming time! 🎯 You can try Pattern Logic for brain teasers, Color Matcher for creativity, or Sorting Master for organization skills. What's your mood?",
                    "Let's have some fun, {name}! 🕹️ Head to the Game Hub from the sidebar — you'll find loads of exciting activities waiting for you!",
                    "Games are the best way to learn! 🎮 Want me to suggest one based on what you'd like to practice?"
                ],
                "follow_ups": ["Try Memory Match!", "How about Emotion Matcher?", "Want a brain teaser?"]
            },

            # ===== SOCIAL PRACTICE / TALKING =====
            "social_practice": {
                "keywords": ["practice talking", "can we practice talking", "social skills", "how to talk to people", "conversation practice", "talk to friends", "make friends", "being with friends", "practice greeting", "start a conversation", "how to greet"],
                "responses": [
                    "Awesome idea, {name}! Let's practice! 🗣️\n\nI'll start: **'Hi! How was your day?'**\n\nNow you try answering! You can say anything — there's no wrong answer!",
                    "Let's do a mini roleplay! Imagine we meet at school.\n\nMe: 'Hey, I like your backpack! Where did you get it?'\n\nNow it's your turn to reply! 😊",
                    "Great thinking! Practicing conversations makes them easier. Here are some starter phrases you can try:\n\n✅ 'Hi, how are you?'\n✅ 'What's your favorite game?'\n✅ 'I really like your drawing!'\n\nWant to practice one of these with me?",
                    "Social skills are like a superpower, and practice makes them stronger! 💪 Let's start simple.\n\nMe: 'Good morning! What did you have for breakfast?'\n\nYour turn!"
                ],
                "follow_ups": ["Try saying 'How was your day?'", "Practice asking a question!", "Let's try another scenario!"]
            },

            # ===== LEARNING / ACADEMY =====
            "learning": {
                "keywords": ["learn", "study", "academy", "english", "english words", "how to learn", "help with english", "start activity", "learning modules", "where to start", "what should i do", "give me a task"],
                "responses": [
                    "The Academy has so many fun things, {name}! Here are some favorites:\n📖 **Word Builder** — Learn prefixes & suffixes\n✏️ **Grammar Games** — Master English rules\n🌤️ **Weather Matcher** — Match weather to clothes\nWhat sounds interesting?",
                    "Ready to learn? 📚 I'd recommend starting with the English Hub — it makes words and grammar super fun with interactive games!",
                    "Learning is an adventure, {name}! 🎒 You could try:\n• **Math Magic** for numbers 🔢\n• **Vocabulary** for new words 📝\n• **Life Skills** for everyday superpowers 🦸\nWhich one catches your eye?",
                    "You're already being a great learner by asking! 🌟 Visit the Academy from the sidebar. I'd suggest starting with something you enjoy — what topics do you like?"
                ],
                "follow_ups": ["Try the Word Builder!", "How about Math Magic?", "Want to learn new words?"]
            },

            # ===== AAC / COMMUNICATION =====
            "aac": {
                "keywords": ["aac", "talk section", "help me speak", "speech tool", "communication board", "how to talk", "build sentence"],
                "responses": [
                    "The Talk section (AAC) is perfect for building sentences! 🗣️ You tap on words and the app says them out loud. You can even save your favorite phrases!",
                    "Great question! The AAC tool helps you express yourself by combining word tiles into sentences. It's like building with blocks, but with words! 🧱",
                    "Head to the AAC section from your dashboard, {name}. You can create sentences, hear them spoken, and practice communication at your own pace. 💬"
                ],
                "follow_ups": ["Want to try building a sentence?", "Go to the Talk section!"]
            },

            # ===== MATH =====
            "math": {
                "keywords": ["math", "numbers", "counting", "adding", "math magic", "arithmetic", "calculator", "multiply", "subtract"],
                "responses": [
                    "Math is like solving puzzles! 🧮 The **Math Magic** game uses fun emojis to help you count and solve problems. Want to give it a try?",
                    "Numbers can be really fun, {name}! Head over to Math Magic in the Learning Hub — it turns math into an exciting game with visual helpers! 🔢",
                    "You'll love Math Magic! It teaches counting, addition, and more using colorful emoji challenges. Ready to become a math wizard? 🧙‍♂️"
                ],
                "follow_ups": ["Try Math Magic!", "Practice counting!", "Ready for a challenge?"]
            },

            # ===== GRAMMAR & WORDS =====
            "grammar": {
                "keywords": ["grammar", "words", "prefix", "suffix", "word builder", "sentence builder", "spelling", "vocabulary", "english words"],
                "responses": [
                    "Word power! 💪 The **Word Builder** teaches prefixes and suffixes, while the **Sentence Builder** helps you create full sentences. Both are in the Academy!",
                    "Mastering words is super fun, {name}! Try the Grammar Games in the Learning Hub — they turn language rules into exciting challenges! ✏️",
                    "Great focus on language skills! 📝 You've got **Vocabulary**, **Word Builder**, and **Grammar** modules all waiting in the Academy section."
                ],
                "follow_ups": ["Try Word Builder!", "Practice Grammar!", "Learn new vocabulary!"]
            },

            # ===== WEATHER =====
            "weather": {
                "keywords": ["weather", "weather matcher", "sunny", "rainy", "snowy", "what to wear", "clothes for weather"],
                "responses": [
                    "The **Weather Matcher** game teaches you what to wear for different weather! ☀️🌧️❄️ It's both fun and really practical for everyday life!",
                    "Learning about weather helps us stay comfy and safe, {name}! The Weather Matcher game has sunny, rainy, and snowy challenges. Give it a try! 🌈"
                ],
                "follow_ups": ["Try Weather Matcher!", "What's the weather today?"]
            },

            # ===== RESPECT & MANNERS =====
            "respect": {
                "keywords": ["respect", "polite", "manners", "being nice", "please", "thank you", "sorry", "excuse me", "kindness", "respectful"],
                "responses": [
                    "It's so wonderful that you care about being respectful, {name}! 🌟 Words like 'please', 'thank you', and 'sorry' are real superpowers!",
                    "Manners make the world a better place! Check out the **Respectful Learner** module — it teaches you how to be kind in different situations. 🤝",
                    "You're already showing great manners by being polite! Here are some magic words:\n✨ 'Please' — when asking\n✨ 'Thank you' — when receiving\n✨ 'Sorry' — when we make a mistake\nYou're a natural!"
                ],
                "follow_ups": ["Try Respectful Learner!", "Practice magic words!"]
            },

            # ===== ABOUT THE BOT =====
            "about_bot": {
                "keywords": ["who are you", "what are you", "what can you do", "are you a robot", "tell me about yourself", "your name"],
                "responses": [
                    "I'm your AI Learning Companion! 🤖 I'm here to help you practice communication, play games, learn new things, and most importantly — be your friend!",
                    "I'm a friendly AI designed just for you, {name}! I can help with:\n🎮 Finding fun games\n📚 Learning activities\n🗣️ Practicing conversations\n💬 Just chatting!\nWhat would you like to do?",
                    "I'm your personal learning buddy! I never get tired, I'm always patient, and I think YOU are awesome. What shall we do together? 🌟"
                ],
                "follow_ups": ["Let's play a game!", "Help me learn!", "Just want to chat"]
            },

            # ===== GOODBYE =====
            "goodbye": {
                "keywords": ["bye", "goodbye", "see you later", "i am leaving", "exit", "stop", "gotta go", "talk later"],
                "responses": [
                    "Goodbye, {name}! 👋 You did amazing today. See you next time!",
                    "Bye-bye! 🌟 Remember, every little step you take is a big win. Come back soon!",
                    "See you later, {name}! Don't forget — you're a superstar! ⭐ Come back whenever you want to chat or play!",
                    "Take care, {name}! 💙 I'll be right here waiting for you when you come back."
                ],
                "follow_ups": []
            },

            # ===== THANKS =====
            "thanks": {
                "keywords": ["thank you", "thanks", "that was helpful", "nice", "cool beans", "appreciate it"],
                "responses": [
                    "You're very welcome, {name}! 😊 I'm always happy to help!",
                    "No problem at all! That's what friends are for! 🤝 Anything else you'd like to do?",
                    "Glad I could help! You're doing great, {name}! 🌟 What's next?"
                ],
                "follow_ups": ["Want to do something else?", "Try a new game!", "Keep learning!"]
            },

            # ===== PARENT SUPPORT =====
            "parent": {
                "keywords": ["i am a parent", "as a parent", "for parents", "my child", "my kid", "diagnosed", "parent help", "caregiver"],
                "responses": [
                    "Welcome! 💛 This platform is designed to support both children and families. As a parent, you can:\n📊 **Family insights** — Track progress in one place\n💡 **Parent Support** — Tips & curated resources\n📋 **Routines** — Appointments and schedules\nHow can I help you specifically?",
                    "Parenting is an incredible journey. The most important things are safety, communication, and predictable routines. The Parent Support page has calm, practical tips to get started. 🌱"
                ],
                "follow_ups": ["View family insights", "Get parenting tips", "Open routines"]
            },

            # ===== THERAPY =====
            "therapy": {
                "keywords": ["therapy", "aba", "speech therapy", "occupational therapy", "ot", "how much therapy", "which therapy"],
                "responses": [
                    "Common therapies include speech-language therapy, occupational therapy (OT), and behavioral supports like ABA. The right mix depends on your child's unique strengths and needs. 🏥",
                    "Therapy should be individualized. A good team will explain clear goals, how progress is measured, and how you can practice skills at home in short, manageable steps. 📋"
                ],
                "follow_ups": ["Learn about ABA", "View therapy schedule", "Get more info"]
            },

            # ===== MELTDOWNS =====
            "meltdown": {
                "keywords": ["meltdown", "tantrum", "behavior issue", "aggressive", "calm down", "overwhelmed", "overload", "too much"],
                "responses": [
                    "Meltdowns are usually a sign of overload, not bad behavior. 🧘 The safest first steps are:\n1. Reduce noise and demands\n2. Offer a calm, safe space\n3. Wait until things settle before talking\nWant to try the Calm Down breathing exercise?",
                    "When everything feels like too much, a calm break can help. The **Calm Down** zone has gentle breathing exercises and soothing activities. Take all the time you need. 💙"
                ],
                "follow_ups": ["Try Calm Down zone", "Breathing exercise", "I need help"]
            },

            # ===== SLEEP & ROUTINE =====
            "routine": {
                "keywords": ["sleep", "bedtime", "routine", "schedule", "daily routine", "morning routine", "night routine"],
                "responses": [
                    "Routines help make the day feel safe and predictable! 📅 The **Routine Builder** game lets you practice building daily routines step by step.",
                    "A consistent routine can make a huge difference! Try the same steps, same order, every day. The Routine Builder game is great practice! 🌙"
                ],
                "follow_ups": ["Try Routine Builder!", "Build a morning routine", "Make a bedtime routine"]
            },

            # ===== PLATFORM HELP =====
            "platform_help": {
                "keywords": ["how to use", "what is this", "explain this", "help me", "how does this work", "what can i do here", "what is this app"],
                "responses": [
                    "Welcome to the Autism Learning Platform! 🏠 Here's a quick tour:\n\n🏠 **Home** — Your daily dashboard & goals\n📚 **Academy** — Learning games & activities\n🎮 **Games** — Fun skill-building games\n🤖 **Social AI** — That's me! Chat anytime\n📊 **Family insights** — Progress for caregivers\n\nWhat would you like to explore first?",
                    "This app is your personal learning companion! Use the sidebar to explore games, learning activities, therapy scheduling, and more. I'm here to guide you through everything! 🗺️"
                ],
                "follow_ups": ["Show me games", "Go to Academy", "What are my goals?"]
            },

            # ===== FOOD & SENSORY =====
            "food_sensory": {
                "keywords": ["food", "eating", "picky", "texture", "taste", "sensory", "diet"],
                "responses": [
                    "Picky eating is often linked to sensory differences in taste, texture, or smell. Slow, no-pressure exposure is usually the safest approach. 🍎",
                    "You can offer one safe food plus a very small portion of something new on the same plate, without forcing bites. If nutrition is a concern, a pediatrician can help! 🥗"
                ],
                "follow_ups": ["Learn about Life Skills", "Try Kitchen Safety module"]
            },

            # ===== SCHOOL =====
            "school": {
                "keywords": ["school", "teacher", "iep", "504", "classroom", "homework", "class"],
                "responses": [
                    "At school, many students have an individualized plan (IEP or 504) with supports like extra time, visual schedules, or quiet spaces. Bringing progress data from this platform can help guide those conversations! 📝",
                    "For school meetings, bring a short list of strengths, current challenges, and 2-3 priorities. Ask how progress will be measured and communicated! 🏫"
                ],
                "follow_ups": ["Track my progress", "View family insights"]
            },

            # ===== DIAGNOSIS =====
            "diagnosis": {
                "keywords": ["diagnosis", "diagnosed", "assessment", "autism diagnosis", "who can diagnose"],
                "responses": [
                    "Autism is typically diagnosed by specialists such as developmental pediatricians, child psychiatrists, or psychologists using interviews, observation, and developmental history. 🏥",
                    "If you're seeking a diagnosis, ask your pediatrician for a referral to a specialist who regularly evaluates autistic children. Bring notes about communication, play, behavior, and sensory needs. 📋"
                ],
                "follow_ups": ["Learn more about autism", "Get parent support"]
            }
        }

    def _normalize(self, text):
        """Normalize text for matching."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        return text

    # Common stop words that should NOT influence intent scoring on their own
    STOP_WORDS = {"i", "am", "is", "are", "a", "an", "the", "do", "does", "did",
                  "to", "it", "in", "on", "at", "my", "me", "we", "you", "your",
                  "be", "was", "were", "been", "have", "has", "had", "can", "will",
                  "would", "should", "could", "of", "for", "with", "this", "that",
                  "what", "how", "who", "when", "where", "there", "here", "so",
                  "if", "or", "and", "but", "not", "no", "yes", "just", "about",
                  "very", "really", "some", "any", "all", "more", "much", "also",
                  "too", "than", "then", "up", "out", "into", "from", "by"}

    def _find_best_intent(self, user_input):
        """
        Fuzzy keyword matching: scores each intent by how many of its
        keywords appear in the user input. Returns (intent_name, score).
        Full phrase matches are prioritised heavily over single-word overlap.
        Stop words are excluded from single-word overlap to avoid false matches.
        """
        normalized = self._normalize(user_input)
        content_words = set(normalized.split()) - self.STOP_WORDS

        best_intent = None
        best_score = 0

        for intent_name, data in self.intents.items():
            score = 0
            for keyword in data['keywords']:
                keyword_norm = self._normalize(keyword)
                # Check if the full keyword phrase is contained in input
                if keyword_norm in normalized:
                    # Longer keyword phrases get higher scores (more specific match)
                    score += len(keyword_norm.split()) * 3
                else:
                    # Fallback: check individual CONTENT word overlap (no stop words)
                    kw_content_words = set(keyword_norm.split()) - self.STOP_WORDS
                    overlap = content_words & kw_content_words
                    if overlap:
                        score += len(overlap)

            if score > best_score:
                best_score = score
                best_intent = intent_name

        return best_intent, best_score

    def _get_mood_prefix(self, user_input, username, context=None):
        """Generate a short contextual prefix based on mood, only sometimes."""
        if context:
            stress = context.get('stress_level', 1)
            if isinstance(stress, str):
                try:
                    stress = int(stress)
                except ValueError:
                    stress = 1
            if stress >= 4:
                return random.choice([
                    "I sense things might be a bit much right now. Let's take it slow. ",
                    "Remember, it's okay to take a break anytime. ",
                    ""
                ])
        return ""

    def _remember(self, username, user_msg, bot_msg):
        """Store the last few exchanges for context."""
        if username not in self.conversation_history:
            self.conversation_history[username] = []
        history = self.conversation_history[username]
        history.append({'user': user_msg, 'bot': bot_msg})
        # Keep only last 10 exchanges
        if len(history) > 10:
            self.conversation_history[username] = history[-10:]

    def _get_history(self, username):
        return self.conversation_history.get(username, [])

    def get_response(self, user_input, username="Student", context=None):
        """Main response method with fuzzy matching and conversation awareness."""

        intent, score = self._find_best_intent(user_input)
        history = self._get_history(username)
        mood_prefix = self._get_mood_prefix(user_input, username, context)

        # If we have a good match (score >= 2), use the matched intent
        if intent and score >= 2:
            response = random.choice(self.intents[intent]['responses'])
            response = response.replace('{name}', username)

            # Avoid repeating the exact same response
            if history:
                last_bot = history[-1].get('bot', '')
                attempts = 0
                while response == last_bot and attempts < 3:
                    response = random.choice(self.intents[intent]['responses'])
                    response = response.replace('{name}', username)
                    attempts += 1

            final = mood_prefix + response
            self._remember(username, user_input, final)
            return final

        # --- LLM FALLBACK: Try Gemini for open-ended questions ---
        if self.gemini_api_key:
            try:
                llm_response = self._ask_gemini(user_input, username, history, context)
                if llm_response:
                    final = mood_prefix + llm_response
                    self._remember(username, user_input, final)
                    return final
            except Exception as e:
                print(f"[Chatbot] Gemini fallback error: {e}")

        # --- STATIC FALLBACK: If no Gemini or Gemini failed ---
        fallbacks = [
            f"That's really interesting, {username}! Tell me more about that. I'm a great listener! 😊",
            f"Hmm, I'm not sure I fully understood, {username}. But I'd love to help! You can ask me about games, learning, feelings, or just chat! 💬",
            f"I'm still learning too, {username}! Here are some things I'm great at:\n🎮 Games & activities\n📚 Learning help\n🗣️ Practicing conversations\n💙 Emotional support\nWhat sounds good?",
            f"Good question, {username}! I might not know everything, but I'm always here to try. Want to explore games, learn something new, or just talk? 🤝",
            f"I love chatting with you, {username}! Even if I'm not sure what to say, I'm here to listen. Want me to suggest something fun? 🌟"
        ]

        response = random.choice(fallbacks)

        # Avoid repeating last fallback
        if history:
            last_bot = history[-1].get('bot', '')
            attempts = 0
            while response == last_bot and attempts < 5:
                response = random.choice(fallbacks)
                attempts += 1

        final = mood_prefix + response
        self._remember(username, user_input, final)
        return final

    def _ask_gemini(self, user_input, username, history, context=None):
        """Call Gemini REST API with conversation context. Returns response text or None."""
        # Build conversation context from recent history
        chat_context = ""
        for h in history[-5:]:
            chat_context += f"User: {h['user']}\nAssistant: {h['bot']}\n"

        system_prompt = self.SYSTEM_PROMPT.replace('{name}', username)
        if context:
            ws = context.get('wellness_signal') or context.get('prediction', '')
            mood = context.get('mood', '')
            stress = context.get('stress_level', '')
            system_prompt += (
                "\n\nOptional informal context from this app only (not diagnostic): "
                f"mood={mood}; stress_level={stress}; wellness_snapshot_label={ws}."
            )
        full_prompt = f"{system_prompt}\n\nRecent conversation:\n{chat_context}\nUser: {user_input}\nAssistant:"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": 600,
                "temperature": 0.8
            }
        }

        resp = requests.post(url, json=payload, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            try:
                text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                # Remove any "Assistant:" prefix if present
                if text.lower().startswith('assistant:'):
                    text = text[len('assistant:'):].strip()
                return text
            except (KeyError, IndexError):
                return None
        else:
            print(f"[Chatbot] Gemini API error {resp.status_code}: {resp.text[:200]}")
            return None

    def get_suggestions(self, user_input):
        """Return dynamic follow-up suggestions based on the matched intent."""
        intent, score = self._find_best_intent(user_input)
        if intent and score >= 2:
            follow_ups = self.intents[intent].get('follow_ups', [])
            if follow_ups:
                return follow_ups[:4]

        # Expanded fallback suggestions to make it far more suggestable
        fallbacks = [
            "Tell me more about that", 
            "Let's play a game!", 
            "I want to learn something new", 
            "Give me some advice",
            "I need to calm down"
        ]
        return random.sample(fallbacks, 4)


# Initialize singleton
chatbot = MLChatbot()
