from flask import Flask, render_template, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, ActivityLog, Appointment, LoginLog, DailyGoal, JournalEntry, SensoryLog, BehaviorPrediction, UserBadge
from chatbot import chatbot
import os
import json
import random
import io
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import joblib
import logging

try:
    from transformers import pipeline
    print("Loading DistilBERT Pipeline (this may take a few seconds)...")
    bert_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    print(f"Could not load DistilBERT: {e}")
    bert_analyzer = None

print("Loading Random Forest Behavior Predictor...")
try:
    behavior_model = joblib.load('models/rf_behavior.pkl')
except Exception as e:
    print(f"Could not load Random Forest model: {e}")
    behavior_model = None

# Download NLTK vader lexicon safely
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_INSTANCE_DIR = os.path.join(_BASE_DIR, 'instance')
os.makedirs(_INSTANCE_DIR, exist_ok=True)

_DEFAULT_DB = 'sqlite:///' + os.path.join(_INSTANCE_DIR, 'platform_v3.db').replace('\\', '/')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-only-change-me-in-env'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', _DEFAULT_DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

WELLNESS_SNAPSHOT_DISCLAIMER = (
    'This uses only journal stress ratings and in-app activity scores. '
    'It is not medical advice or a diagnosis. Use it to plan breaks and routines with your family or care team.'
)

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html') # Start at login for now, or landing page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Record successful login attempt
            db.session.add(LoginLog(user_id=user.id))
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return 'Email already exists'
        
        new_user = User(
            username=username,
            email=email, 
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            current_user.username = request.form.get('username')
            db.session.commit()
            message = "Profile updated successfully!"
        elif action == 'update_password':
            new_pwd = request.form.get('new_password')
            current_user.password = generate_password_hash(new_pwd, method='pbkdf2:sha256')
            db.session.commit()
            message = "Password changed safely!"
            
    return render_template('settings.html', user=current_user, message=message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def calculate_streak(user_id):
    from datetime import date, timedelta
    login_logs = LoginLog.query.filter_by(user_id=user_id).all()
    activity_logs = ActivityLog.query.filter_by(user_id=user_id).all()
    
    all_dates = set([log.timestamp.date() for log in login_logs] + [log.timestamp.date() for log in activity_logs])
    if not all_dates:
        return 0
    
    unique_days = sorted(list(all_dates), reverse=True)
    
    streak = 0
    today = date.today()
    
    if unique_days[0] == today:
        streak = 1
        check_date = today - timedelta(days=1)
        for i in range(1, len(unique_days)):
            if unique_days[i] == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    elif unique_days[0] == today - timedelta(days=1):
        streak = 1
        check_date = today - timedelta(days=2)
        for i in range(1, len(unique_days)):
            if unique_days[i] == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
                
    return streak

@app.route('/dashboard')
@login_required
def dashboard():
    activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    total_activities = ActivityLog.query.filter_by(user_id=current_user.id).count()
    streak = calculate_streak(current_user.id)
    
    # --- Gamification Badge Logic ---
    earned_badge_names = [b.badge_name for b in UserBadge.query.filter_by(user_id=current_user.id).all()]
    new_badges = []
    
    if streak >= 3 and "Consistency Master" not in earned_badge_names:
        new_badge = UserBadge(user_id=current_user.id, badge_name="Consistency Master", badge_desc="Logged in 3 days in a row!", icon="🔥")
        db.session.add(new_badge)
        new_badges.append(new_badge)
        earned_badge_names.append("Consistency Master")
        
    if total_activities >= 10 and "Avid Learner" not in earned_badge_names:
        new_badge = UserBadge(user_id=current_user.id, badge_name="Avid Learner", badge_desc="Completed 10 activities!", icon="📚")
        db.session.add(new_badge)
        new_badges.append(new_badge)
        earned_badge_names.append("Avid Learner")
        
    if new_badges:
        db.session.commit()
        
    badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    # -------------------------------
    
    # Daily Goals Logic
    from datetime import UTC
    today = datetime.now(UTC).date()
    goals = DailyGoal.query.filter_by(user_id=current_user.id, date=today).all()
    
    if not goals:
        # Create default goals for today
        default_goals = [
            "Practice 'Speak It Right' for 5 minutes",
            "Complete one 'Memory Match' game",
            "Learn 3 new English words"
        ]
        goals = []
        for content in default_goals:
            new_goal = DailyGoal(user_id=current_user.id, content=content, date=today)
            db.session.add(new_goal)
            goals.append(new_goal)
        db.session.commit()
    
    return render_template('dashboard.html', user=current_user, activities=activities, total_activities=total_activities, streak=streak, daily_goals=goals, badges=badges)

@app.route('/api/toggle_goal/<int:goal_id>', methods=['POST'])
@login_required
def toggle_goal(goal_id):
    goal = db.session.get(DailyGoal, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    if goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    goal.is_completed = not goal.is_completed
    db.session.commit()
    return jsonify({'status': 'success', 'is_completed': goal.is_completed})

@app.route('/learning/magic-storybook')
@login_required
def learning_magic_storybook():
    return render_template('interactive_story.html')

@app.route('/games/social-quest')
@login_required
def games_social_quest():
    return render_template('games/social_quest.html')

@app.route('/api/user_stats')
@login_required
def user_stats():
    activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    total_activities = ActivityLog.query.filter_by(user_id=current_user.id).count()
    streak = calculate_streak(current_user.id)
    
    # XP and Level Calculation
    all_activities = ActivityLog.query.filter_by(user_id=current_user.id).all()
    total_xp = sum([a.score for a in all_activities if a.score])
    level = (total_xp // 200) + 1  # 200 XP per level
    next_level_xp = 200
    current_level_xp = total_xp % 200
    xp_percentage = (current_level_xp / next_level_xp) * 100

    # Chart data
    chart_data = [{'date': a.timestamp.strftime('%m-%d'), 'score': a.score} for a in activities[::-1]]
    
    return jsonify({
        'total_activities': total_activities,
        'streak': streak,
        'chart_data': chart_data,
        'recent_activities': [{
            'type': a.activity_type,
            'score': a.score,
            'date': a.timestamp.strftime('%m-%d %H:%M'),
            'metadata': json.loads(a.metadata_json) if a.metadata_json else None
        } for a in activities],
        'level': level,
        'total_xp': total_xp,
        'xp_percentage': xp_percentage
    })


@app.route('/aac')
@login_required
def aac():
    return render_template('aac.html')

@app.route('/games')
@login_required
def games():
    return render_template('games/hub.html')

@app.route('/games/emotion-matcher')
@login_required
def emotion_matcher():
    return render_template('games/emotion_matcher.html')

@app.route('/games/routine-builder')
@login_required
def routine_builder():
    return render_template('games/routine_builder.html')

@app.route('/games/drawing')
@login_required
def drawing_game():
    return render_template('games/drawing.html')

@app.route('/games/scenarios')
@login_required
def scenarios_game():
    return render_template('games/scenarios.html')

@app.route('/games/sorting')
@login_required
def sorting_game():
    return render_template('games/sorting.html')

@app.route('/games/respect')
@login_required
def respect_game():
    return render_template('games/respect.html')

@app.route('/games/memory-match')
@login_required
def memory_match():
    return render_template('games/memory_match.html')

@app.route('/games/sorting-master')
@login_required
def sorting_master():
    return render_template('games/sorting_master.html')

@app.route('/games/color-matcher')
@login_required
def color_matcher():
    return render_template('games/color_matcher.html')

@app.route('/games/pattern-logic')
@login_required
def pattern_logic():
    return render_template('games/pattern_logic.html')

# New Learning Activities
@app.route('/learning/english_words')
@login_required
def learning_english_words():
    return render_template('learning/english_words.html')

@app.route('/learning/plurals')
@login_required
def learning_plurals():
    return render_template('learning/plurals.html')

@app.route('/learning/social/public')
@login_required
def learning_social_public():
    return render_template('learning/public_social.html')

@app.route('/learning/body-signals')
@login_required
def learning_body_signals():
    return render_template('learning/body_signals.html')

@app.route('/learning/word-builder')
@login_required
def learning_word_builder():
    return render_template('learning/word_builder.html')

@app.route('/learning/math-magic')
@login_required
def learning_math_magic():
    return render_template('learning/math_fun.html')

@app.route('/learning/weather-matcher')
@login_required
def learning_weather_matcher():
    return render_template('learning/weather_matcher.html')

@app.route('/learning/respectful')
@login_required
def learning_respectful():
    return render_template('learning/respectful.html')

@app.route('/learning/grammar')
@login_required
def learning_grammar():
    return render_template('learning/grammar.html')

# --- Chatbot Routes ---
@app.route('/chatbot')
@login_required
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    try:
        data = request.json
        user_message = data.get('message', '')
        username = current_user.username or current_user.email.split('@')[0]
        
        # Fetch latest context for a "responsible" and aware response
        latest_journal = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.timestamp.desc()).first()
        latest_pred = BehaviorPrediction.query.filter_by(user_id=current_user.id).order_by(BehaviorPrediction.timestamp.desc()).first()
        
        context = {
            'mood': latest_journal.mood if latest_journal else 'Neutral',
            'stress_level': latest_journal.stress_level if latest_journal else 1,
            'wellness_signal': latest_pred.predicted_state if latest_pred else 'No snapshot yet'
        }
        
        bot_response = chatbot.get_response(user_message, username=username, context=context)
        suggestions = chatbot.get_suggestions(user_message)
        return jsonify({'response': bot_response, 'suggestions': suggestions})
    except Exception:
        return jsonify({'response': "I'm here for you! I had a tiny slip-up, but I'm ready to keep talking. What's on your mind?"})

# --- English Learning Routes ---
@app.route('/learning')
@login_required
def learning_hub():
    return render_template('learning/english_hub.html')

@app.route('/learning/vocab')
@login_required
def learning_vocab():
    return render_template('learning/vocabulary.html')

@app.route('/learning/life_skills')
@login_required
def learning_life_skills():
    return render_template('learning/life_skills.html')

@app.route('/learning/kitchen_safety')
@login_required
def learning_kitchen_safety():
    return render_template('learning/kitchen_safety.html')

# --- Therapy Routes ---
@app.route('/therapy', methods=['GET', 'POST'])
@login_required
def therapy():
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        time = request.form.get('time')
        notes = request.form.get('notes')
        status = request.form.get('status', 'Scheduled')
        homework = request.form.get('homework')
        
        new_appt = Appointment(
            user_id=current_user.id, 
            title=title, 
            date=date, 
            time=time, 
            notes=notes,
            status=status,
            homework=homework
        )
        db.session.add(new_appt)
        db.session.commit()
        return redirect(url_for('therapy'))
        
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('therapy_schedule.html', appointments=appointments)

@app.route('/therapy/update/<int:appt_id>', methods=['POST'])
@login_required
def update_therapy(appt_id):
    appt = db.session.get(Appointment, appt_id)
    if not appt or appt.user_id != current_user.id:
        return "Unauthorized", 403
    
    appt.status = request.form.get('status')
    db.session.commit()
    return redirect(url_for('therapy'))

@app.route('/therapy/delete/<int:appt_id>', methods=['POST'])
@login_required
def delete_therapy(appt_id):
    appt = db.session.get(Appointment, appt_id)
    if not appt or appt.user_id != current_user.id:
        return "Unauthorized", 403
    
    db.session.delete(appt)
    db.session.commit()
    return redirect(url_for('therapy'))

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        mood = request.form.get('mood')
        note = request.form.get('note')
        stress = request.form.get('stress_level', 1)
        
        # NLP Sentiment Analysis
        sentiment_score = None
        if note and note.strip():
            try:
                sid = SentimentIntensityAnalyzer()
                sentiment_score = sid.polarity_scores(note)['compound']
            except Exception as e:
                print(f"Sentiment Analysis Error: {e}")
        
        new_entry = JournalEntry(user_id=current_user.id, mood=mood, note=note, stress_level=stress, sentiment_score=sentiment_score)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('journal'))
    
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.timestamp.desc()).all()
    return render_template('journal.html', entries=entries)

@app.route('/calm-down')
@login_required
def calm_down():
    return render_template('calm_down.html')

@app.route('/sensory-monitor')
@login_required
def sensory_monitor():
    return render_template('sensory_monitor.html')

def _safe_stress_level(entry):
    try:
        return int(entry.stress_level)
    except (TypeError, ValueError):
        return 1


@app.route('/api/predict_behavior', methods=['POST'])
@login_required
def predict_behavior():
    """Informal wellness snapshot from in-app data only—not clinical."""
    recent_logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_journals = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.timestamp.desc()).limit(5).all()
    
    stress_points = sum(1 for j in recent_journals if _safe_stress_level(j) > 3)
    low_scores = sum(1 for l in recent_logs if l.score and l.score < 40)
    
    # ML Random Forest Prediction
    display_label = 'Steady week (informal)'
    interpretation = 'Journal stress ratings and recent practice scores look relatively steady. Keep predictable routines and short, positive sessions.'
    suggested_actions = 'Continue your usual rhythm: small goals, movement breaks, and celebrating effort—not just scores.'
    confidence = 0.50

    if behavior_model:
        X_input = [[stress_points, low_scores]]
        pred = behavior_model.predict(X_input)[0]
        # Get probability of the predicted class
        probas = behavior_model.predict_proba(X_input)[0]
        confidence = float(max(probas))
        
        if pred == 1:
            display_label = 'May benefit from extra calm & breaks (informal)'
            interpretation = 'Our Random Forest AI noticed patterns (higher stress / lower practice scores) that correlate with fatigue.'
            suggested_actions = 'Try the Calm Down area, shorter learning chunks, sensory-friendly space, and pausing demands.'
        else:
            interpretation += " (Verified by Random Forest AI)"
    else:
        # Fallback to heuristic if model didn't load
        confidence = 0.78
        if stress_points >= 2 or low_scores >= 4:
            display_label = 'May benefit from extra calm & breaks (informal)'
            interpretation = 'Recent entries show higher stress and/or several lower practice scores.'
            suggested_actions = 'Try the Calm Down area, shorter learning chunks, sensory-friendly space, and pausing demands until regulation returns.'
            confidence = 0.74
    
    new_pred = BehaviorPrediction(
        user_id=current_user.id,
        predicted_state=display_label,
        confidence=confidence,
        reasoning=interpretation,
        remedy_suggestion=suggested_actions
    )
    db.session.add(new_pred)
    db.session.commit()
    
    payload = {
        'wellness_signal': display_label,
        'interpretation': interpretation,
        'suggested_actions': suggested_actions,
        'confidence': confidence,
        'disclaimer': WELLNESS_SNAPSHOT_DISCLAIMER,
    }
    # Backward-compatible keys for older clients
    payload['prediction'] = display_label
    payload['reasoning'] = interpretation
    payload['remedy'] = suggested_actions
    return jsonify(payload)

@app.route('/api/log_activity', methods=['POST'])
@login_required
def log_activity():
    data = request.json
    activity_type = data.get('type')
    score = data.get('score', 0)
    details = data.get('details', '')
    metadata = data.get('metadata', {})
    metadata_str = json.dumps(metadata) if metadata else None

    new_log = ActivityLog(
        user_id=current_user.id,
        activity_type=activity_type,
        score=score,
        details=details,
        metadata_json=metadata_str
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/parent/dashboard')
@login_required
def parent_dashboard():
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).all()
    
    domains = {
        'Communication': ['AAC Usage', 'English Word Mastery', 'Sentence Builder', 'Noun or Verb Sorter', 'Grammar Mastery'],
        'Social Cognition': ['Respectful Learner', 'Emotion Matcher', 'Social Adventure', 'Body Signals', 'Public Social Rules'],
        'Executive Function': ['Memory Match', 'Sorting Master', 'Routine Builder', 'Logic Master', 'Pattern Logic'],
        'Life Skills': ['Life Safety', 'Kitchen Safety', 'Morning Routine', 'Time Manager'],
        'Creative Expression': ['Creative Studio', 'Drawing', 'Color Mastery']
    }
    
    domain_metrics = {d: {'count': 0, 'total_score': 0, 'avg': 0} for d in domains}
    activity_map = {}
    for d, acts in domains.items():
        for act in acts:
            activity_map[act] = d
            
    for log in logs:
        domain = activity_map.get(log.activity_type)
        if domain:
            domain_metrics[domain]['count'] += 1
            if log.score:
                domain_metrics[domain]['total_score'] += log.score
                
    radar_data = {}
    for d, m in domain_metrics.items():
        if m['count'] > 0:
            m['avg'] = round(m['total_score'] / m['count'], 1)
        radar_data[d] = m['avg']
        
    from collections import defaultdict
    daily_scores = defaultdict(list)
    for log in logs:
        if log.score:
            date_str = log.timestamp.strftime('%Y-%m-%d')
            daily_scores[date_str].append(log.score)
            
    sorted_dates = sorted(daily_scores.keys())[-30:]
    trajectory_labels = []
    trajectory_data = []
    
    for d in sorted_dates:
        scores = daily_scores[d]
        avg_daily = sum(scores) / len(scores)
        trajectory_labels.append(d[5:])
        trajectory_data.append(round(avg_daily, 1))

    lowest_domain = min(radar_data, key=radar_data.get) if radar_data else 'Communication'
    lowest_score = radar_data.get(lowest_domain, 0)
    
    recommendation = ""
    if lowest_score < 50:
        recommendation = (
            f"Gentle focus: {lowest_domain} shows the lowest average score so far. "
            f"Try two short, low-pressure practice blocks (about 10 minutes) when energy is good."
        )
    elif lowest_score < 75:
        recommendation = (
            f"Steady growth in {lowest_domain}—keep going with small, regular sessions for confidence."
        )
    else:
        recommendation = (
            "Across tracked areas, averages look strong. Offer variety and optional stretch activities when interest is high."
        )

    # --- 1. Emotional Trends (Mood & Stress over time) ---
    journals = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.timestamp.desc()).limit(30).all()
    mood_labels = []
    mood_data = [] # numeric scale for charts
    stress_data = []
    
    mood_map = {"Happy": 4, "Neutral": 3, "Sad": 2, "Anxious/Stressed": 1}
    for j in reversed(journals):
        mood_labels.append(j.timestamp.strftime('%m-%d'))
        mood_data.append(mood_map.get(j.mood, 3))
        stress_data.append(j.stress_level)

    # --- 2. Behavioral Patterns & Sensory Insights ---
    sensory_logs = SensoryLog.query.filter_by(user_id=current_user.id).order_by(SensoryLog.timestamp.desc()).limit(10).all()
    prediction = BehaviorPrediction.query.filter_by(user_id=current_user.id).order_by(BehaviorPrediction.timestamp.desc()).first()
    
    # --- 3. Family-friendly suggestion (informal—not medical) ---
    latest_journal = journals[0] if journals else None
    streak = calculate_streak(current_user.id)
    traj_avg = round(sum(trajectory_data) / len(trajectory_data), 1) if trajectory_data else None

    smart_rec = {
        'title': "Steady rhythm",
        'action': "Open Home",
        'action_endpoint': 'dashboard',
        'type': 'Neutral',
        'suggestion': "Keep using the journal and short learning blocks that already work for your family."
    }

    if latest_journal:
        if _safe_stress_level(latest_journal) >= 4 or latest_journal.mood == "Anxious/Stressed":
            smart_rec = {
                'title': "Journal shows high stress",
                'action': "Open Calm Down",
                'action_endpoint': 'calm_down',
                'type': 'Support',
                'suggestion': (
                    "The latest journal entry looks intense. A calm break, less noise, and fewer demands "
                    "often help before more learning."
                )
            }
        elif latest_journal.mood == "Sad":
            smart_rec = {
                'title': "Journal suggests low mood",
                'action': "Browse games hub",
                'action_endpoint': 'games',
                'type': 'Attention',
                'suggestion': (
                    "Consider something low-demand together—a preferred hobby, a walk, or a short social scenario game "
                    "only if it feels welcome."
                )
            }

    if lowest_score < 60:
        smart_rec = {
            'title': f"Extra practice: {lowest_domain}",
            'action': "Go to Academy",
            'action_endpoint': 'learning_hub',
            'type': 'Focus',
            'suggestion': (
                f"Average score in {lowest_domain} is about {lowest_score}%. "
                f"Two brief, encouraging sessions often beat one long one."
            )
        }

    # Educational Video Recommendation System (Categorized)
    curated_videos = [
        {'id': 'bIi1wnjBowM', 'title': 'Transition Tips for Parents', 'category': 'Social', 'desc': 'Shannon Penrod shares essential transition tips for parents of autistic children in this recent 2025 episode.'},
        {'id': 'tPeaWOGC_60', 'title': 'Guide for 3-5 Year Olds', 'category': 'Communication', 'desc': 'A comprehensive guide for parents of children aged 3-5 newly diagnosed with ASD, focusing on early intervention and support.'},
        {'id': 'IJCf2tMi4tI', 'title': 'ABA Therapy Basics', 'category': 'Communication', 'desc': 'An in-depth explanation of ABA therapy principles and how parents can support their child\'s learning journey.'},
        {'id': 'alk2yKAN59c', 'title': 'Top Ten Resources', 'category': 'Social', 'desc': 'A valuable breakdown of the top 10 resources curated specifically for families navigating autism support.'},
        {'id': 'p6zu1ofZseI', 'title': 'The Four Types of Play', 'category': 'Social', 'desc': 'Newcastle Speech Pathology explains the four stages of play development and how to engage children effectively.'},
        {'id': 'InOMSSYOU0k', 'title': 'Teaching Compliance Correct-ly', 'category': 'Communication', 'desc': 'Autism Live discusses ethical and effective methods for teaching compliance and functional communication.'},
        {'id': 'U3MjjhtFQeM', 'title': 'Best Toys for ASD Development', 'category': 'Calming', 'desc': 'A curated list of developmental toys designed to enhance sensory play and skill-building for children with autism.'},
        {'id': '479VhkmDuYQ', 'title': 'Making Therapy a Priority', 'category': 'Calming', 'desc': 'A very recent discussion on why incorporating therapy into daily routines is essential for long-term progress.'},
        {'id': '6m0QryB1x78', 'title': '7 Hacks to Calm Meltdowns', 'category': 'Calming', 'desc': '2025 update on proven strategies to manage and prevent meltdowns by understanding triggers.'},
        {'id': 'Np6qJg9GSZY', 'title': 'Coping Strategies for Kids', 'category': 'Calming', 'desc': 'Latest 2025 coping mechanisms and sensory tools to help autistic individuals feel regulated.'},
        {'id': 'DNj--qTipy4', 'title': 'Encouraging Functional Speech', 'category': 'Communication', 'desc': 'Expert advice from India Autism Center on evidence-based techniques for non-verbal children.'},
        {'id': '9_x_W2X0I6A', 'title': 'Music for Communication', 'category': 'Communication', 'desc': 'A specialized musical approach designed to engage children and prompt communication breakthroughs.'},
        {'id': 'm6rG3risIts', 'title': 'Home-Based Language Tips', 'category': 'Communication', 'desc': 'Practical tips for parents to create communication opportunities within daily home routines.'},
        {'id': 'rvXYzD1NuG8', 'title': 'Fostering Joint Attention', 'category': 'Social', 'desc': 'Mary Barbera demonstrates how to build joint attention, the foundational block for social interaction.'},
        {'id': 'Dpg3UhE5yYI', 'title': 'Sport & Social Skills', 'category': 'Social', 'desc': 'How structured physical activities help developed vital social cues and cooperative play.'},
        {'id': 'bNMG7yEWdqc', 'title': 'Helping Kids Make Friends', 'category': 'Social', 'desc': 'Targeted advice on facilitating social connections and navigating friendship complexities.'}
    ]

    return render_template(
        'parent_dashboard.html',
        user=current_user,
        logs=logs,
        radar_data=radar_data,
        trajectory_labels=trajectory_labels,
        trajectory_data=trajectory_data,
        mood_labels=mood_labels,
        mood_data=mood_data,
        stress_data=stress_data,
        sensory_logs=sensory_logs,
        prediction=prediction,
        smart_rec=smart_rec,
        recommendation=recommendation,
        total_sessions=len(logs),
        videos=curated_videos,
        streak=streak,
        traj_avg=traj_avg,
        lowest_domain=lowest_domain,
        wellness_disclaimer=WELLNESS_SNAPSHOT_DISCLAIMER,
    )

@app.route('/parent/support')
@login_required
def parent_support():
    """Parent-facing tips and curated video recommendations."""
    # Domain list matches the family progress dashboard for consistency.
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).all()

    domains = {
        'Communication': ['AAC Usage', 'English Word Mastery', 'Sentence Builder', 'Noun or Verb Sorter', 'Grammar Mastery'],
        'Social Cognition': ['Respectful Learner', 'Emotion Matcher', 'Social Adventure', 'Body Signals', 'Public Social Rules'],
        'Executive Function': ['Memory Match', 'Sorting Master', 'Routine Builder', 'Logic Master', 'Pattern Logic'],
        'Life Skills': ['Life Safety', 'Kitchen Safety', 'Morning Routine', 'Time Manager'],
        'Creative Expression': ['Creative Studio', 'Drawing', 'Color Mastery']
    }

    domain_metrics = {d: {'count': 0} for d in domains}
    activity_map = {}
    for d, acts in domains.items():
        for act in acts:
            activity_map[act] = d

    for log in logs:
        domain = activity_map.get(log.activity_type)
        if domain:
            domain_metrics[domain]['count'] += 1

    # Identify domain with least practice to personalize tips
    practiced_counts = {d: m['count'] for d, m in domain_metrics.items()}
    lowest_domain = min(practiced_counts, key=practiced_counts.get) if practiced_counts else 'Communication'

    # Curated Support Videos (YouTube IDs), tagged by category
    curated_videos = [
        {'id': 'bIi1wnjBowM', 'title': 'Transition Tips for Parents', 'category': 'Social', 'domain': 'Executive Function'},
        {'id': 'tPeaWOGC_60', 'title': 'Guide for 3-5 Year Olds', 'category': 'Communication', 'domain': 'Communication'},
        {'id': 'IJCf2tMi4tI', 'title': 'ABA Therapy Basics', 'category': 'Communication', 'domain': 'Communication'},
        {'id': 'alk2yKAN59c', 'title': 'Top Ten Resources', 'category': 'Social', 'domain': 'Life Skills'},
        {'id': 'p6zu1ofZseI', 'title': 'The Four Types of Play', 'category': 'Social', 'domain': 'Social Cognition'},
        {'id': 'InOMSSYOU0k', 'title': 'Teaching Compliance Correct-ly', 'category': 'Communication', 'domain': 'Social Cognition'},
        {'id': 'U3MjjhtFQeM', 'title': 'Best Toys for ASD Development', 'category': 'Calming', 'domain': 'Creative Expression'},
        {'id': '479VhkmDuYQ', 'title': 'Making Therapy a Priority', 'category': 'Calming', 'domain': 'Life Skills'},
        {'id': '6m0QryB1x78', 'title': '7 Hacks to Calm Meltdowns', 'category': 'Calming', 'domain': 'Life Skills'},
        {'id': 'Np6qJg9GSZY', 'title': 'Coping Strategies for Kids', 'category': 'Calming', 'domain': 'Creative Expression'},
        {'id': 'DNj--qTipy4', 'title': 'Encouraging Functional Speech', 'category': 'Communication', 'domain': 'Communication'},
        {'id': '9_x_W2X0I6A', 'title': 'Music for Communication', 'category': 'Communication', 'domain': 'Communication'},
        {'id': 'm6rG3risIts', 'title': 'Home-Based Language Tips', 'category': 'Communication', 'domain': 'Communication'},
        {'id': 'rvXYzD1NuG8', 'title': 'Fostering Joint Attention', 'category': 'Social', 'domain': 'Social Cognition'},
        {'id': 'Dpg3UhE5yYI', 'title': 'Sport & Social Skills', 'category': 'Social', 'domain': 'Social Cognition'},
        {'id': 'bNMG7yEWdqc', 'title': 'Helping Kids Make Friends', 'category': 'Social', 'domain': 'Social Cognition'}
    ]

    # Prioritize videos that align with the least-practiced domain
    prioritized_videos = sorted(
        curated_videos,
        key=lambda v: 0 if v['domain'] == lowest_domain else 1
    )

    # Gentle, parent-friendly quick tips
    quick_tips = [
        "Keep language short, clear, and predictable. One simple sentence is easier to process than many.",
        "Offer choices instead of demands when possible (\"blue shirt or red shirt?\").",
        "Notice and praise tiny steps, not just big wins. Consistency matters more than perfection.",
        "Build in calm breaks before your child is overwhelmed, not after.",
        "Use the same words for routines every day so they become familiar scripts."
    ]

    return render_template(
        'parent_support.html',
        user=current_user,
        lowest_domain=lowest_domain,
        videos=prioritized_videos,
        quick_tips=quick_tips
    )

@app.route('/api/insights')
@login_required
def get_insights():
    # Smart Recommendation Engine
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(30).all()
    
    if not logs:
        return jsonify({'insight': "Welcome! Start your journey by trying the 'English Word Mastery' task."})

    counts = {}
    for log in logs:
        counts[log.activity_type] = counts.get(log.activity_type, 0) + 1
            
    # Category Analysis
    cat_counts = {
        'Language': sum(counts.get(x, 0) for x in ['AAC Usage', 'English Word Mastery', 'Sentence Builder', 'Noun or Verb Sorter']),
        'Social': sum(counts.get(x, 0) for x in ['Respectful Learner', 'Emotion Matcher', 'Social Adventure']),
        'Logic': sum(counts.get(x, 0) for x in ['Memory Match', 'Sorting Master', 'Routine Builder'])
    }
    
    # Identify least practiced category
    least_practiced = min(cat_counts, key=cat_counts.get)
    
    # Recommendations
    recs = {
        'Language': "You've been doing great with social tasks! Why not try building some sentences in 'Grammar Games'?",
        'Social': "Excellent focus on memory tasks! A 'Respectful Learner' session could be a great next step.",
        'Logic': "You're communicating so well! Practice your focus with a 'Memory Match' game."
    }
    
    insight_text = recs.get(least_practiced, "Keep up the great work! You are becoming a well-rounded learner.")
            
    return jsonify({'insight': f"Suggestion: {insight_text}"})

@app.route('/ml-evaluation')
@login_required
def ml_evaluation():
    return render_template('ml_evaluation.html')

@app.route('/api/ml_compare', methods=['POST'])
@login_required
def ml_compare():
    data = request.json
    text = data.get('text', '')
    
    vader_res = "Not calculated"
    bert_res = "Not loaded"
    
    if text:
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            sid = SentimentIntensityAnalyzer()
            v_score = sid.polarity_scores(text)['compound']
            vader_res = f"Compound: {round(v_score, 3)} ({'Positive' if v_score > 0.1 else 'Negative' if v_score < -0.1 else 'Neutral'})"
        except Exception as e:
            vader_res = str(e)
            
        if bert_analyzer:
            try:
                b = bert_analyzer(text)[0]
                bert_res = f"Label: {b['label']}, Confidence: {round(b['score'], 3)}"
            except Exception as e:
                bert_res = f"Error: {e}"
        else:
            bert_res = "DistilBERT pipeline not initialized."
            
    return jsonify({
        'vader': vader_res,
        'bert': bert_res
    })

def create_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    _debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes')
    app.run(debug=_debug)
