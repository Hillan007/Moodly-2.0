from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import datetime
from datetime import date, timedelta
# from openai import OpenAI  # Temporarily disabled
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv
import requests
import base64
import random
import statistics
from collections import defaultdict, Counter
from PIL import Image
import hashlib
import time
import io

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure OpenAI client
openai_client = None
try:
    if os.environ.get('OPENAI_API_KEY'):
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        print("✅ OpenAI client initialized successfully!")
except Exception as e:
    print(f"⚠️ OpenAI client initialization error: {e}")
    print("App will continue with fallback prompts.")

# Data storage (in production, use a proper database)
JOURNAL_ENTRIES = {}
USER_DATA = {}

# User authentication and profile system
USERS_DB = {}  # In production, use a proper database
USER_SESSIONS = {}  # Track active sessions
LOGIN_ATTEMPTS = {}  # Track failed login attempts for rate limiting
UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update the resize_image function to handle production environment

def resize_image(image_path, max_size=(400, 400)):
    """Resize uploaded image to max dimensions while maintaining aspect ratio."""
    try:
        # Check if we're in production (Vercel)
        if os.environ.get('VERCEL'):
            print("⚠️ File uploads not supported in production environment")
            return False
            
        with Image.open(image_path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

def generate_user_id():
    """Generate unique user ID."""
    return str(uuid.uuid4())

def hash_password(password):
    """Hash password with salt."""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + pwdhash

def verify_password(stored_password, provided_password):
    """Verify provided password against stored hash."""
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return pwdhash == stored_hash

def login_required(f):
    """Decorator to require login for protected routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user data."""
    if 'user_id' in session:
        return USERS_DB.get(session['user_id'])
    return None

def check_rate_limit(identifier, max_attempts=5, window_minutes=15):
    """Check if user has exceeded login attempt rate limit."""
    now = datetime.datetime.now()
    if identifier not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[identifier] = []
    
    # Remove old attempts outside the window
    LOGIN_ATTEMPTS[identifier] = [
        attempt for attempt in LOGIN_ATTEMPTS[identifier]
        if (now - attempt).total_seconds() < window_minutes * 60
    ]
    
    return len(LOGIN_ATTEMPTS[identifier]) < max_attempts

def record_failed_login(identifier):
    """Record a failed login attempt."""
    now = datetime.datetime.now()
    if identifier not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[identifier] = []
    LOGIN_ATTEMPTS[identifier].append(now)

def clear_failed_logins(identifier):
    """Clear failed login attempts for successful login."""
    if identifier in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[identifier]

# Achievement system
ACHIEVEMENTS = {
    'first_entry': {'name': 'First Steps', 'description': 'Wrote your first journal entry!', 'emoji': '👶'},
    'streak_3': {'name': 'Building Habits', 'description': '3 days of journaling in a row!', 'emoji': '🔥'},
    'streak_7': {'name': 'Week Warrior', 'description': '7 days of journaling in a row!', 'emoji': '⚡'},
    'streak_30': {'name': 'Monthly Master', 'description': '30 days of journaling in a row!', 'emoji': '👑'},
    'mood_explorer': {'name': 'Mood Explorer', 'description': 'Experienced 5 different moods!', 'emoji': '🗺️'},
    'gratitude_guru': {'name': 'Gratitude Guru', 'description': 'Practiced gratitude 10 times!', 'emoji': '🙏'},
    'music_lover': {'name': 'Music Lover', 'description': 'Discovered music for 5 different moods!', 'emoji': '🎵'},
    'self_care_champion': {'name': 'Self-Care Champion', 'description': 'Used breathing exercises 5 times!', 'emoji': '🌟'}
}

# Mood options with emojis and colors
MOODS = {
    'happy': {'emoji': '😊', 'color': '#FFD700', 'name': 'Happy'},
    'sad': {'emoji': '😢', 'color': '#87CEEB', 'name': 'Sad'},
    'excited': {'emoji': '🤩', 'color': '#FF6347', 'name': 'Excited'},
    'anxious': {'emoji': '😰', 'color': '#DDA0DD', 'name': 'Anxious'},
    'calm': {'emoji': '😌', 'color': '#98FB98', 'name': 'Calm'},
    'angry': {'emoji': '😠', 'color': '#FF4500', 'name': 'Angry'},
    'confused': {'emoji': '😕', 'color': '#F0E68C', 'name': 'Confused'},
    'grateful': {'emoji': '🙏', 'color': '#DEB887', 'name': 'Grateful'}
}

# Spotify Configuration
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

# Mood-based search terms for Spotify
MOOD_MUSIC_GENRES = {
    'happy': ['happy', 'upbeat', 'pop', 'cheerful', 'feel good', 'uplifting'],
    'sad': ['sad', 'melancholy', 'acoustic', 'emotional', 'gentle', 'soft'],
    'excited': ['energetic', 'dance', 'electronic', 'pump up', 'party', 'high energy'],
    'anxious': ['calming', 'peaceful', 'ambient', 'soothing', 'relaxing', 'meditation'],
    'calm': ['chill', 'peaceful', 'ambient', 'meditation', 'nature sounds', 'lo-fi'],
    'angry': ['rock', 'metal', 'intense', 'powerful', 'alternative', 'punk'],
    'confused': ['indie', 'alternative', 'thoughtful', 'introspective', 'folk', 'acoustic'],
    'grateful': ['inspirational', 'uplifting', 'gospel', 'positive', 'motivational', 'soul']
}

# Breathing exercises for different moods
BREATHING_EXERCISES = {
    'anxious': {
        'name': '4-7-8 Calming Breath',
        'description': 'Perfect for when you feel worried or nervous',
        'steps': [
            'Breathe in through your nose for 4 counts',
            'Hold your breath for 7 counts',
            'Breathe out through your mouth for 8 counts',
            'Repeat 3-4 times'
        ],
        'duration': '2 minutes'
    },
    'angry': {
        'name': 'Box Breathing',
        'description': 'Helps you cool down when feeling upset',
        'steps': [
            'Breathe in for 4 counts',
            'Hold for 4 counts',
            'Breathe out for 4 counts',
            'Hold empty for 4 counts',
            'Repeat 5-6 times'
        ],
        'duration': '3 minutes'
    },
    'excited': {
        'name': 'Grounding Breath',
        'description': 'Helps you focus your exciting energy',
        'steps': [
            'Take 3 deep breaths',
            'Notice 5 things you can see',
            'Notice 4 things you can touch',
            'Notice 3 things you can hear',
            'Take 2 more deep breaths'
        ],
        'duration': '3 minutes'
    },
    'sad': {
        'name': 'Heart Warming Breath',
        'description': 'Gentle breathing to comfort yourself',
        'steps': [
            'Place one hand on your heart',
            'Breathe slowly and deeply',
            'Imagine warmth flowing to your heart',
            'Say "I am kind to myself" with each breath',
            'Continue for 2-3 minutes'
        ],
        'duration': '3 minutes'
    },
    'default': {
        'name': 'Simple Deep Breathing',
        'description': 'Good for any mood',
        'steps': [
            'Sit comfortably',
            'Breathe in slowly for 4 counts',
            'Breathe out slowly for 6 counts',
            'Focus only on your breathing',
            'Repeat 8-10 times'
        ],
        'duration': '2 minutes'
    }
}

# Coping strategies for different moods
COPING_STRATEGIES = {
    'anxious': [
        'Try the 5-4-3-2-1 grounding technique',
        'Write down your worries, then write solutions',
        'Take a short walk outside',
        'Listen to calming music',
        'Talk to someone you trust'
    ],
    'angry': [
        'Count to 10 slowly',
        'Do some physical exercise',
        'Draw or scribble your feelings',
        'Take space from the situation',
        'Use "I feel..." statements'
    ],
    'sad': [
        'Be gentle with yourself',
        'Reach out to a friend or family member',
        'Do something creative',
        'Watch something funny',
        'Practice self-compassion'
    ],
    'confused': [
        'Make a list of what you know vs. what you don\'t know',
        'Talk through your thoughts with someone',
        'Break the problem into smaller parts',
        'Take a break and come back later',
        'Ask for help - it\'s okay!'
    ],
    'excited': [
        'Channel your energy into something positive',
        'Share your excitement with others',
        'Make a plan for your goals',
        'Create or build something',
        'Celebrate your feelings!'
    ]
}

# Enhanced mood playlists (fallback when Spotify isn't available)
ENHANCED_MOOD_PLAYLISTS = {
    'happy': [
        {'title': 'Happy by Pharrell Williams', 'artist': 'Pharrell Williams', 'url': 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH', 'mood_match': 95},
        {'title': 'Can\'t Stop the Feeling!', 'artist': 'Justin Timberlake', 'url': 'https://open.spotify.com/track/0BcuxEZ6V2Jd9A7s8a0fQG', 'mood_match': 92},
        {'title': 'Good as Hell', 'artist': 'Lizzo', 'url': 'https://open.spotify.com/track/6KlmkRh8pqTymVl3ulkOoE', 'mood_match': 90},
        {'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'url': 'https://open.spotify.com/track/6SAzKR0EWKGfpKdQVVCjLY', 'mood_match': 88},
        {'title': 'Three Little Birds', 'artist': 'Bob Marley', 'url': 'https://open.spotify.com/track/0XUfyU2QviPAs6bxSpXYG4', 'mood_match': 85}
    ],
    'calm': [
        {'title': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://open.spotify.com/track/1nrKCDJYHd9m3nj5HwJfJe', 'mood_match': 98},
        {'title': 'Claire de Lune', 'artist': 'Claude Debussy', 'url': 'https://open.spotify.com/track/6GamyPTd8J9AcfLKhORj2K', 'mood_match': 95},
        {'title': 'Spiegel im Spiegel', 'artist': 'Arvo Pärt', 'url': 'https://open.spotify.com/track/0dUrOmfBjIgWfLNxG9M1u5', 'mood_match': 92},
        {'title': 'Aqueous Transmission', 'artist': 'Incubus', 'url': 'https://open.spotify.com/track/6ZPqLiNTfSy1IEqj1dPuYw', 'mood_match': 88},
        {'title': 'Mad World', 'artist': 'Gary Jules', 'url': 'https://open.spotify.com/track/3JOVTQ5h4HIqRuMX9gEVSI', 'mood_match': 85}
    ],
    # Add more enhanced playlists for other moods...
}

# Journal entry templates
JOURNAL_TEMPLATES = {
    'gratitude': {
        'name': 'Gratitude List',
        'prompts': [
            'Three things I\'m grateful for today:',
            'Someone who made me smile:',
            'A simple pleasure I enjoyed:',
            'Something about myself I appreciate:'
        ]
    },
    'daily_reflection': {
        'name': 'Daily Check-in',
        'prompts': [
            'How I\'m feeling right now:',
            'The best part of my day:',
            'Something that challenged me:',
            'What I\'m looking forward to:'
        ]
    },
    'worry_dump': {
        'name': 'Worry Release',
        'prompts': [
            'What\'s worrying me:',
            'What I can control about this:',
            'What I can\'t control:',
            'One small step I can take:'
        ]
    },
    'dream_big': {
        'name': 'Dreams & Goals',
        'prompts': [
            'Something I want to achieve:',
            'Why this matters to me:',
            'First step I could take:',
            'Who could help me:'
        ]
    }
}

def get_user_id():
    """Get or create a user ID for the session"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def get_ai_prompt(mood_key, mood_info):
    """Generate AI-powered journaling prompt based on mood."""
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a supportive, encouraging assistant helping tweens (ages 10-14) with emotional journaling. Be warm, age-appropriate, and understanding. Keep responses to 1-2 sentences."
                    },
                    {
                        "role": "user", 
                        "content": f"I'm feeling {mood_info['name'].lower()} today. Give me a thoughtful journaling prompt to help me explore this emotion."
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            ai_prompt = response.choices[0].message.content.strip()
            print(f"🤖 Generated AI prompt for {mood_key}: {ai_prompt}")
            return ai_prompt
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
    
    # Fallback prompts if OpenAI fails
    fallback_prompts = {
        'happy': "What made you smile today? Describe a moment that brought you joy!",
        'sad': "It's okay to feel sad sometimes. What would help you feel a little better?",
        'excited': "Your excitement is contagious! What are you looking forward to?",
        'anxious': "Take a deep breath. What's one small thing you can do to feel calmer?",
        'calm': "You seem peaceful today. What's helping you feel so centered?",
        'angry': "Those feelings are valid. What happened, and how can we work through it?",
        'confused': "It's normal to feel mixed up sometimes. What's on your mind?",
        'grateful': "Gratitude is beautiful! What are you most thankful for right now?"
    }
    
    prompt = fallback_prompts.get(mood_key, "How are you feeling today? Tell me what's on your mind.")
    print(f"📝 Using fallback prompt for {mood_key}")
    return prompt

def get_motivational_message(mood):
    """Generate a motivational message based on mood"""
    messages = {
        'happy': "Keep spreading that wonderful energy! 🌟",
        'sad': "Remember, tough times don't last, but tough people like you do! 💪",
        'excited': "Your enthusiasm is amazing! Channel that energy into something awesome! ⚡",
        'anxious': "You're braver than you believe and stronger than you seem. Take it one step at a time. 🌈",
        'calm': "Your inner peace is a gift. Share that calm energy with the world! 🕊️",
        'angry': "It's okay to feel angry. Use that energy to make positive changes! 🔥➡️💫",
        'confused': "Every question is a step toward understanding. You're on the right path! 🧭",
        'grateful': "A grateful heart is a magnet for miracles! Keep counting those blessings! ✨"
    }
    return messages.get(mood, "You're doing great! Every day is a new opportunity to grow! 🌱")

def get_spotify_token():
    """Get Spotify access token using client credentials flow"""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print(f"Spotify credentials missing - ID: {bool(SPOTIFY_CLIENT_ID)}, Secret: {bool(SPOTIFY_CLIENT_SECRET)}")
        return None
    
    try:
        print("Attempting to get Spotify token...")
        # Encode credentials
        credentials = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        
        if response.status_code == 200:
            print("Successfully obtained Spotify token")
            return response.json()['access_token']
        else:
            print(f"Spotify token error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Spotify token error: {e}")
        return None

def get_mood_songs(mood, limit=5):
    """Get song recommendations based on mood"""
    print(f"Getting songs for mood: {mood}")
    
    token = get_spotify_token()
    if not token:
        print("No Spotify token available, using fallback songs")
        # Return fallback songs if Spotify is not configured
        return get_fallback_songs(mood, limit)
    
    try:
        print(f"Using Spotify API with token")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get search terms for the mood
        search_terms = MOOD_MUSIC_GENRES.get(mood, ['happy'])
        print(f"Search terms for {mood}: {search_terms}")
        
        all_songs = []
        
        for term in search_terms[:2]:  # Use first 2 search terms
            # Search for tracks
            search_url = f"https://api.spotify.com/v1/search"
            params = {
                'q': f'genre:{term} year:2020-2024',  # Recent songs
                'type': 'track',
                'limit': 10,
                'market': 'US'
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            print(f"Spotify API response status: {response.status_code}")
            
            if response.status_code == 200:
                tracks = response.json()['tracks']['items']
                print(f"Found {len(tracks)} tracks for term '{term}'")
                
                for track in tracks:
                    if track['preview_url']:  # Only include tracks with preview
                        song_data = {
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'preview_url': track['preview_url'],
                            'spotify_url': track['external_urls']['spotify'],
                            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'duration_ms': track['duration_ms']
                        }
                        all_songs.append(song_data)
            else:
                print(f"Spotify API error for term '{term}': {response.status_code}")
        
        # Remove duplicates and limit results
        unique_songs = []
        seen_names = set()
        for song in all_songs:
            if song['name'] not in seen_names:
                unique_songs.append(song)
                seen_names.add(song['name'])
                if len(unique_songs) >= limit:
                    break
        
        print(f"Returning {len(unique_songs)} unique songs from Spotify")
        if len(unique_songs) > 0:
            return unique_songs[:limit]
        else:
            print("No songs found from Spotify, using fallback")
            return get_fallback_songs(mood, limit)
        
    except Exception as e:
        print(f"Spotify API error: {e}")
        return get_fallback_songs(mood, limit)

def get_fallback_songs(mood, limit=5):
    """Fallback songs when Spotify API is not available"""
    print(f"Using fallback songs for mood: {mood}")
    
    fallback_songs = {
        'happy': [
            {'name': 'Happy', 'artist': 'Pharrell Williams', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH', 'image_url': None},
            {'name': 'Good as Hell', 'artist': 'Lizzo', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/1WkMMavIMc4JZ8cfMmxHkI', 'image_url': None},
            {'name': 'Shake It Off', 'artist': 'Taylor Swift', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0G3fbPbvIjkOqnKk3SEkxF', 'image_url': None},
            {'name': 'Can\'t Stop the Feeling!', 'artist': 'Justin Timberlake', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/6YLJuuENhWCpYNWwhPE8JY', 'image_url': None},
            {'name': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0', 'image_url': None}
        ],
        'sad': [
            {'name': 'Someone Like You', 'artist': 'Adele', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4eHbdreAnSOrDDsFfc4Fpm', 'image_url': None},
            {'name': 'Mad World', 'artist': 'Gary Jules', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3JOVQD9v7fMNvqWLNKpYRZ', 'image_url': None},
            {'name': 'Hurt', 'artist': 'Johnny Cash', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/5W1XsShlfGhfx7S2N4DP1I', 'image_url': None},
            {'name': 'Breathe Me', 'artist': 'Sia', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/5Je5Ldh1yi6gTsOBJdwgbp', 'image_url': None},
            {'name': 'Skinny Love', 'artist': 'Bon Iver', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4TeXHRfejYsLA85rKBKFhz', 'image_url': None}
        ],
        'excited': [
            {'name': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS', 'image_url': None},
            {'name': 'I Gotta Feeling', 'artist': 'Black Eyed Peas', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC', 'image_url': None},
            {'name': 'Dynamite', 'artist': 'BTS', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0t1kP63rueHleOhQkYSXFY', 'image_url': None},
            {'name': 'Levitating', 'artist': 'Dua Lipa', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/463CkQjx2Zk1yXoBuierM9', 'image_url': None},
            {'name': 'Don\'t Stop Me Now', 'artist': 'Queen', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/7hQJA50XrCWABAu5v6QZ4i', 'image_url': None}
        ],
        'anxious': [
            {'name': 'Weightless', 'artist': 'Marconi Union', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4TJVks9lQdFRvIILDNXdLt', 'image_url': None},
            {'name': 'Claire de Lune', 'artist': 'Claude Debussy', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4Nd5HJn4EExnLmHtClk4QV', 'image_url': None},
            {'name': 'Aqueous Transmission', 'artist': 'Incubus', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3nKODR4UAp60lvqNhfKOQt', 'image_url': None},
            {'name': 'The Sound of Silence', 'artist': 'Simon & Garfunkel', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/5tVA6TkbaAH9QMITTQRrNv', 'image_url': None},
            {'name': 'Breathe (2 AM)', 'artist': 'Anna Nalick', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3BKD4HLcLUkbf3riHD5wqz', 'image_url': None}
        ],
        'calm': [
            {'name': 'Holocene', 'artist': 'Bon Iver', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0WhTQoq6skCchWovp1ykGh', 'image_url': None},
            {'name': 'Sunset Lover', 'artist': 'Petit Biscuit', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0dYNAhiQHQOXUPe8k8FW23', 'image_url': None},
            {'name': 'River', 'artist': 'Joni Mitchell', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3GY8ORd6vL5OSkbDqzTrCh', 'image_url': None},
            {'name': 'Mad About You', 'artist': 'Sting', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/6ykAAgp2jHVFXLOBa7vNiZ', 'image_url': None},
            {'name': 'Weightless', 'artist': 'Marconi Union', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4TJVks9lQdFRvIILDNXdLt', 'image_url': None}
        ],
        'angry': [
            {'name': 'Stronger', 'artist': 'Kelly Clarkson', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0jnFwJcJQbTTk7KPxBZdmF', 'image_url': None},
            {'name': 'Fight Song', 'artist': 'Rachel Platten', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/1lzr43nnXAijIGYnCHxAuH', 'image_url': None},
            {'name': 'Roar', 'artist': 'Katy Perry', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/2pgG9DXDfGhLaJWbwH6wdQ', 'image_url': None},
            {'name': 'Confident', 'artist': 'Demi Lovato', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/4b7nKjJDNFy3LrCTZHQ43t', 'image_url': None},
            {'name': 'Titanium', 'artist': 'David Guetta ft. Sia', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0lTqv8RFkuAKMODSZ65ZcS', 'image_url': None}
        ],
        'confused': [
            {'name': 'Mad World', 'artist': 'Tears for Fears', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/6sXLJJXhNhKZZWnCdxfKZj', 'image_url': None},
            {'name': 'Losing Religion', 'artist': 'R.E.M.', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/1VXOaUa7GIlwZDC5rlEOkq', 'image_url': None},
            {'name': 'Black', 'artist': 'Pearl Jam', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0Hcbm0IHjWTL6gNmMkNaow', 'image_url': None},
            {'name': 'Everybody Hurts', 'artist': 'R.E.M.', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3d8MPBHb8LeJLJbOqTLNog', 'image_url': None},
            {'name': 'Fix You', 'artist': 'Coldplay', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q', 'image_url': None}
        ],
        'grateful': [
            {'name': 'Thank U, Next', 'artist': 'Ariana Grande', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/3e9HZxeyfWwjeyPAMmWSSQ', 'image_url': None},
            {'name': 'Count on Me', 'artist': 'Bruno Mars', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/0lPCPzBnAkWnQi8nz6xfGe', 'image_url': None},
            {'name': 'What a Wonderful World', 'artist': 'Louis Armstrong', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/5anR4ry9qrJN5ZOGHOnXwn', 'image_url': None},
            {'name': 'Three Little Birds', 'artist': 'Bob Marley', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/6JloTDuTKz96G4zgu3PoqC', 'image_url': None},
            {'name': 'Here Comes the Sun', 'artist': 'The Beatles', 'preview_url': None, 'spotify_url': 'https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2', 'image_url': None}
        ]
    }
    
    result = fallback_songs.get(mood, fallback_songs['happy'])[:limit]
    print(f"Returning {len(result)} fallback songs for {mood}")
    return result

@app.route('/')
def index():
    return render_template('index.html', moods=MOODS)

@app.route('/mood/<mood_key>')
def mood_selected(mood_key):
    """Handle mood selection and show journaling interface."""
    if mood_key not in MOODS:
        return redirect(url_for('index'))
    
    mood_info = MOODS[mood_key]
    
    # Check if user is logged in
    user = get_current_user()
    if user:
        # For logged-in users, store in their personal data
        if 'current_mood' not in session:
            session['current_mood'] = {}
        session['current_mood'] = {
            'key': mood_key,
            'info': mood_info,
            'user_id': user['id']
        }
    else:
        # For anonymous users, store in session only
        session['current_mood'] = {
            'key': mood_key,
            'info': mood_info,
            'user_id': None
        }
    
    # Get AI-powered or fallback prompt
    ai_prompt = get_ai_prompt(mood_key, mood_info)
    
    # Get mood-appropriate music
    songs = get_mood_songs(mood_key)
    
    return render_template('journal.html', 
                         mood=mood_info, 
                         mood_key=mood_key,
                         ai_prompt=ai_prompt,
                         songs=songs,
                         user=user)

@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    user_id = get_user_id()
    data = request.get_json()
    
    mood = data.get('mood')
    entry_text = data.get('entry', '').strip()
    
    if not entry_text:
        return jsonify({'error': 'Please write something in your journal!'}), 400
    
    # Store the journal entry
    entry_id = str(uuid.uuid4())
    entry = {
        'id': entry_id,
        'date': date.today().isoformat(),
        'timestamp': datetime.datetime.now().isoformat(),
        'mood': mood,
        'entry': entry_text,
        'user_id': user_id
    }
    
    if user_id not in JOURNAL_ENTRIES:
        JOURNAL_ENTRIES[user_id] = []
    
    JOURNAL_ENTRIES[user_id].append(entry)
    
    # Get motivational message
    motivational_msg = get_motivational_message(mood)
    
    return jsonify({
        'success': True,
        'message': motivational_msg,
        'entry_id': entry_id
    })

@app.route('/tracker')
def mood_tracker():
    user_id = get_user_id()
    entries = JOURNAL_ENTRIES.get(user_id, [])
    
    # Prepare data for the mood timeline
    mood_data = []
    for entry in sorted(entries, key=lambda x: x['timestamp']):
        mood_data.append({
            'date': entry['date'],
            'mood': entry['mood'],
            'mood_info': MOODS.get(entry['mood'], {}),
            'entry_preview': entry['entry'][:100] + '...' if len(entry['entry']) > 100 else entry['entry']
        })
    
    return render_template('tracker.html', mood_data=mood_data, moods=MOODS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/music/<mood_key>')
def get_music_for_mood(mood_key):
    """API endpoint to get music recommendations for a specific mood"""
    if mood_key not in MOODS:
        return jsonify({'error': 'Invalid mood'}), 400
    
    songs = get_mood_songs(mood_key, limit=10)
    return jsonify({
        'mood': mood_key,
        'songs': songs,
        'mood_info': MOODS[mood_key]
    })

def calculate_mood_streak(user_id):
    """Calculate current journaling streak for user"""
    if user_id not in JOURNAL_ENTRIES:
        return 0
    
    entries = JOURNAL_ENTRIES[user_id]
    if not entries:
        return 0
    
    # Sort entries by date
    sorted_entries = sorted(entries, key=lambda x: x['date'], reverse=True)
    
    streak = 0
    current_date = date.today()
    
    for entry in sorted_entries:
        entry_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d').date()
        if entry_date == current_date or entry_date == current_date - timedelta(days=streak):
            streak += 1
            current_date = entry_date
        else:
            break
    
    return streak

def get_mood_analytics(user_id):
    """Get mood analytics for user"""
    if user_id not in JOURNAL_ENTRIES:
        return {'total_entries': 0, 'mood_distribution': {}, 'streak': 0, 'insights': []}
    
    entries = JOURNAL_ENTRIES[user_id]
    total_entries = len(entries)
    
    if total_entries == 0:
        return {'total_entries': 0, 'mood_distribution': {}, 'streak': 0, 'insights': []}
    
    # Calculate mood distribution
    mood_counts = Counter(entry['mood'] for entry in entries)
    mood_distribution = {mood: count for mood, count in mood_counts.items()}
    
    # Calculate streak
    streak = calculate_mood_streak(user_id)
    
    # Generate insights
    insights = []
    if total_entries >= 7:
        most_common_mood = mood_counts.most_common(1)[0][0]
        insights.append(f"Your most common mood this week is {MOODS[most_common_mood]['emoji']} {MOODS[most_common_mood]['name']}")
    
    if streak >= 3:
        insights.append(f"Amazing! You're on a {streak}-day journaling streak! 🔥")
    
    recent_entries = entries[-7:] if len(entries) >= 7 else entries
    recent_moods = [entry['mood'] for entry in recent_entries]
    if 'grateful' in recent_moods:
        insights.append("You've been practicing gratitude - that's wonderful for your wellbeing! 🙏")
    
    return {
        'total_entries': total_entries,
        'mood_distribution': mood_distribution,
        'streak': streak,
        'insights': insights
    }

def check_achievements(user_id):
    """Check and award new achievements"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {'achievements': [], 'stats': {}}
    
    user_data = USER_DATA[user_id]
    current_achievements = set(user_data.get('achievements', []))
    new_achievements = []
    
    if user_id in JOURNAL_ENTRIES:
        entries = JOURNAL_ENTRIES[user_id]
        total_entries = len(entries)
        streak = calculate_mood_streak(user_id)
        unique_moods = len(set(entry['mood'] for entry in entries))
        grateful_entries = len([e for e in entries if e['mood'] == 'grateful'])
        
        # Check for achievements
        if total_entries >= 1 and 'first_entry' not in current_achievements:
            new_achievements.append('first_entry')
        
        if streak >= 3 and 'streak_3' not in current_achievements:
            new_achievements.append('streak_3')
        
        if streak >= 7 and 'streak_7' not in current_achievements:
            new_achievements.append('streak_7')
        
        if streak >= 30 and 'streak_30' not in current_achievements:
            new_achievements.append('streak_30')
        
        if unique_moods >= 5 and 'mood_explorer' not in current_achievements:
            new_achievements.append('mood_explorer')
        
        if grateful_entries >= 10 and 'gratitude_guru' not in current_achievements:
            new_achievements.append('gratitude_guru')
    
    # Add new achievements
    user_data['achievements'].extend(new_achievements)
    
    return new_achievements

def get_breathing_exercise(mood):
    """Get appropriate breathing exercise for mood"""
    return BREATHING_EXERCISES.get(mood, BREATHING_EXERCISES['default'])

def get_coping_strategies(mood):
    """Get coping strategies for mood"""
    strategies = COPING_STRATEGIES.get(mood, [])
    # Return 3 random strategies
    return random.sample(strategies, min(3, len(strategies))) if strategies else []

def get_journal_template(template_type):
    """Get journal template"""
    return JOURNAL_TEMPLATES.get(template_type, JOURNAL_TEMPLATES['daily_reflection'])

def predict_mood_patterns(user_id):
    """Simple mood pattern analysis"""
    if user_id not in JOURNAL_ENTRIES:
        return {}
    
    entries = JOURNAL_ENTRIES[user_id]
    if len(entries) < 7:
        return {'message': 'Keep journaling to see patterns!'}
    
    # Analyze mood patterns by day of week
    mood_by_day = defaultdict(list)
    for entry in entries:
        entry_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
        day_of_week = entry_date.weekday()  # 0 = Monday
        mood_by_day[day_of_week].append(entry['mood'])
    
    insights = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day, moods in mood_by_day.items():
        if len(moods) >= 2:
            most_common = Counter(moods).most_common(1)[0][0]
            insights.append(f"You tend to feel {MOODS[most_common]['name']} on {day_names[day]}s")
    
    return {'insights': insights[:3]}  # Return top 3 insights

# For Vercel deployment - export the app object
application = app

@app.route('/breathing/<mood_key>')
def breathing_exercise(mood_key):
    """Show breathing exercise for specific mood"""
    if mood_key not in MOODS:
        return redirect(url_for('index'))
    
    exercise = get_breathing_exercise(mood_key)
    return render_template('breathing.html', 
                         mood=MOODS[mood_key], 
                         exercise=exercise,
                         mood_key=mood_key)

@app.route('/wellness')
def wellness_hub():
    """Wellness hub with various tools"""
    user_id = get_user_id()
    analytics = get_mood_analytics(user_id)
    recent_achievements = USER_DATA.get(user_id, {}).get('achievements', [])[-3:]  # Last 3 achievements
    
    return render_template('wellness.html', 
                         analytics=analytics,
                         achievements=recent_achievements,
                         achievement_details=ACHIEVEMENTS)

@app.route('/analytics')
def analytics():
    """Analytics dashboard page."""
    user = get_current_user()
    
    # Get mood data for analytics
    if user:
        user_entries = JOURNAL_ENTRIES.get(user['id'], [])
    else:
        user_entries = session.get('journal_entries', [])
    
    # Calculate analytics
    mood_data = []
    for entry in user_entries:
        mood_data.append({
            'date': entry['date'],
            'mood_key': entry['mood_key'],
            'mood_info': MOODS[entry['mood_key']],
            'timestamp': entry['timestamp']
        })
    
    # Calculate streaks and patterns
    analytics_data = calculate_mood_analytics(mood_data)
    
    return render_template('analytics.html', 
                         mood_data=mood_data,
                         analytics=analytics_data,
                         user=user)

@app.route('/api/analytics')
def analytics_api():
    """API endpoint for analytics data."""
    user = get_current_user()
    
    if user:
        user_entries = JOURNAL_ENTRIES.get(user['id'], [])
    else:
        user_entries = session.get('journal_entries', [])
    
    # Prepare data for charts
    mood_counts = Counter([entry['mood_key'] for entry in user_entries])
    
    return jsonify({
        'mood_counts': dict(mood_counts),
        'total_entries': len(user_entries)
    })

@app.route('/templates')
def journal_templates():
    """Show available journal templates"""
    return render_template('templates.html', templates=JOURNAL_TEMPLATES)

@app.route('/template/<template_type>')
def use_template(template_type):
    """Use a specific journal template"""
    if template_type not in JOURNAL_TEMPLATES:
        return redirect(url_for('journal_templates'))
    
    template = get_journal_template(template_type)
    return render_template('template_journal.html', 
                         template=template,
                         template_type=template_type)

@app.route('/coping/<mood_key>')
def coping_strategies_page(mood_key):
    """Show coping strategies for specific mood"""
    if mood_key not in MOODS:
        return redirect(url_for('index'))
    
    strategies = get_coping_strategies(mood_key)
    exercise = get_breathing_exercise(mood_key)
    
    return render_template('coping.html',
                         mood=MOODS[mood_key],
                         mood_key=mood_key,
                         strategies=strategies,
                         exercise=exercise)

@app.route('/achievements')
def achievements_page():
    """Show user achievements"""
    user_id = get_user_id()
    user_achievements = USER_DATA.get(user_id, {}).get('achievements', [])
    
    achieved = {ach_id: ACHIEVEMENTS[ach_id] for ach_id in user_achievements if ach_id in ACHIEVEMENTS}
    not_achieved = {ach_id: details for ach_id, details in ACHIEVEMENTS.items() if ach_id not in user_achievements}
    
    return render_template('achievements.html',
                         achieved=achieved,
                         not_achieved=not_achieved)

@app.route('/api/achievements/check')
def check_achievements_api():
    """API endpoint to check for new achievements"""
    user_id = get_user_id()
    new_achievements = check_achievements(user_id)
    
    return jsonify({
        'new_achievements': [
            {'id': ach_id, 'details': ACHIEVEMENTS[ach_id]} 
            for ach_id in new_achievements if ach_id in ACHIEVEMENTS
        ]
    })



@app.route('/api/coping/<mood_key>')
def coping_api(mood_key):
    """API endpoint for coping strategies"""
    if mood_key not in MOODS:
        return jsonify({'error': 'Invalid mood'}), 400
    
    strategies = get_coping_strategies(mood_key)
    exercise = get_breathing_exercise(mood_key)
    
    return jsonify({
        'mood': mood_key,
        'strategies': strategies,
        'breathing_exercise': exercise
    })

@app.route('/submit_template_entry', methods=['POST'])
def submit_template_entry():
    """Submit a journal entry from a template"""
    data = request.get_json()
    user_id = get_user_id()
    
    if user_id not in JOURNAL_ENTRIES:
        JOURNAL_ENTRIES[user_id] = []
    
    # Combine template responses into a single entry
    template_responses = data.get('responses', {})
    combined_entry = "\n\n".join([f"{prompt}: {response}" for prompt, response in template_responses.items()])
    
    entry = {
        'id': str(uuid.uuid4()),
        'mood': data.get('mood', 'happy'),
        'entry': combined_entry,
        'date': date.today().strftime('%Y-%m-%d'),
        'timestamp': datetime.datetime.now().isoformat(),
        'template_type': data.get('template_type', 'custom')
    }
    
    JOURNAL_ENTRIES[user_id].append(entry)
    
    # Check for new achievements
    new_achievements = check_achievements(user_id)
    
    # Generate motivational message
    motivational_messages = [
        "Great job expressing yourself! 🌟",
        "Your thoughts and feelings matter! 💖",
        "You're building such great self-awareness! 🧠",
        "Keep up the amazing work! ✨",
        "Every entry helps you grow! 🌱"
    ]
    
    return jsonify({
        'success': True,
        'message': random.choice(motivational_messages),
        'new_achievements': [
            {'id': ach_id, 'details': ACHIEVEMENTS[ach_id]} 
            for ach_id in new_achievements if ach_id in ACHIEVEMENTS
        ]
    })

# User authentication routes

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        age = request.form.get('age', '')
        
        # Validation
        errors = []
        
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        
        # Enhanced username validation
        if not username.replace('_', '').replace('-', '').isalnum():
            errors.append("Username can only contain letters, numbers, underscores, and hyphens")
        
        if '@' not in email or '.' not in email.split('@')[1]:
            errors.append("Please enter a valid email address")
        
        # Enhanced password validation
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        # Check for password strength
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not has_letter:
            errors.append("Password must contain at least one letter")
        
        if not has_number:
            errors.append("Password must contain at least one number")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        try:
            age_int = int(age)
            if age_int < 14 or age_int > 29:
                errors.append("Age must be between 14 and 29")
        except ValueError:
            errors.append("Please enter a valid age")
        
        # Check if username or email already exists
        for user_data in USERS_DB.values():
            if user_data['username'].lower() == username.lower():
                errors.append("Username already exists")
            if user_data['email'].lower() == email.lower():
                errors.append("Email already registered")
        
        if errors:
            return render_template('auth/signup.html', errors=errors, 
                                 username=username, email=email, age=age)
        
        # Create new user
        user_id = generate_user_id()
        USERS_DB[user_id] = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': hash_password(password),
            'age': int(age),
            'profile_picture': None,
            'bio': '',
            'created_at': datetime.datetime.now().isoformat(),
            'last_login': None,
            'mood_streak': 0,
            'total_entries': 0,
            'achievements': [],
            'email_verified': True,  # In production, implement email verification
            'account_status': 'active'
        }
        
        # Initialize user's journal entries
        JOURNAL_ENTRIES[user_id] = []
        USER_DATA[user_id] = {}
        
        # Auto-login after signup
        session['user_id'] = user_id
        session['username'] = username
        
        return redirect(url_for('profile_setup'))
    
    return render_template('auth/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Check rate limiting based on IP or username
        client_identifier = request.environ.get('REMOTE_ADDR', 'unknown') + '_' + username_or_email.lower()
        
        if not check_rate_limit(client_identifier):
            error = "Too many failed login attempts. Please try again in 15 minutes."
            return render_template('auth/login.html', error=error, 
                                 username_or_email=username_or_email)
        
        # Find user by username or email
        user = None
        for user_data in USERS_DB.values():
            if (user_data['username'].lower() == username_or_email.lower() or 
                user_data['email'].lower() == username_or_email.lower()):
                user = user_data
                break
        
        if user and verify_password(user['password'], password):
            # Successful login - clear any failed attempts
            clear_failed_logins(client_identifier)
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Set session permanent if remember me is checked
            if remember_me:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
            
            # Update last login
            user['last_login'] = datetime.datetime.now().isoformat()
            
            # Redirect to intended page or home
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            # Record failed login attempt
            record_failed_login(client_identifier)
            
            error = "Invalid username/email or password"
            return render_template('auth/login.html', error=error, 
                                 username_or_email=username_or_email)
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Get user's recent journal entries
    user_entries = []
    if user['id'] in JOURNAL_ENTRIES:
        user_entries = JOURNAL_ENTRIES[user['id']][-10:]  # Last 10 entries
    
    # Calculate user statistics
    total_entries = len(JOURNAL_ENTRIES.get(user['id'], []))
    user_data = USER_DATA.get(user['id'], {})
    mood_counts = {}
    
    # Count mood frequencies
    for entry in JOURNAL_ENTRIES.get(user['id'], []):
        mood = entry.get('mood_key', 'unknown')
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    return render_template('auth/profile.html', 
                         user=user,
                         recent_entries=user_entries,
                         total_entries=total_entries,
                         mood_counts=mood_counts)

@app.route('/profile/setup')
@login_required
def profile_setup():
    """Profile setup page for new users."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('auth/profile_setup.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        success_message = None
        error_message = None
        
        # Handle bio update
        bio = request.form.get('bio', '').strip()
        if len(bio) <= 500:  # Validate bio length
            user['bio'] = bio
            success_message = "Profile updated successfully!"
        else:
            error_message = "Bio must be 500 characters or less."
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                # Generate secure filename
                timestamp = str(int(time.time()))
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f"profile_{user['id']}_{timestamp}.{file_extension}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    # Save file
                    file.save(filepath)
                    
                    # Resize image
                    if resize_image(filepath):
                        # Remove old profile picture if exists
                        if user.get('profile_picture'):
                            old_path = os.path.join(app.config['UPLOAD_FOLDER'], user['profile_picture'])
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Update user profile
                        user['profile_picture'] = filename
                        success_message = "Profile picture updated successfully!"
                    else:
                        # If resize failed, remove the file
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        error_message = "Failed to process image. Please try a different image."
                        
                except Exception as e:
                    error_message = f"Error uploading image: {str(e)}"
                    if os.path.exists(filepath):
                        os.remove(filepath)
            elif file and file.filename:
                error_message = "Invalid file type. Please use JPG, PNG, GIF, or WebP images."
        
        # Redirect with message
        if success_message:
            return render_template('auth/edit_profile.html', user=user, success=success_message)
        elif error_message:
            return render_template('auth/edit_profile.html', user=user, error=error_message)
        
        return redirect(url_for('profile'))
    
    return render_template('auth/edit_profile.html', user=user)

@app.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Verify current password
        if not verify_password(user['password'], current_password):
            errors.append("Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 6:
            errors.append("New password must be at least 6 characters long")
        
        if new_password != confirm_password:
            errors.append("New passwords do not match")
        
        # Check password strength
        has_letter = any(c.isalpha() for c in new_password)
        has_number = any(c.isdigit() for c in new_password)
        
        if not has_letter:
            errors.append("Password must contain at least one letter")
        
        if not has_number:
            errors.append("Password must contain at least one number")
        
        if errors:
            return render_template('auth/change_password.html', errors=errors)
        
        # Update password
        user['password'] = hash_password(new_password)
        
        return render_template('auth/change_password.html', 
                             success="Password updated successfully!")
    
    return render_template('auth/change_password.html')

# Add this helper function after your existing helper functions

def calculate_mood_analytics(mood_data):
    """Calculate comprehensive mood analytics."""
    if not mood_data:
        return {
            'total_entries': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'most_common_mood': None,
            'mood_distribution': {},
            'weekly_average': 0
        }
    
    # Count mood occurrences
    mood_counts = Counter([entry['mood_key'] for entry in mood_data])
    most_common = mood_counts.most_common(1)
    most_common_mood = most_common[0][0] if most_common else None
    
    # Calculate streaks (consecutive days with entries)
    dates = sorted(set([entry['date'] for entry in mood_data]))
    current_streak = 0
    longest_streak = 0
    temp_streak = 1
    
    for i in range(1, len(dates)):
        prev_date = datetime.datetime.strptime(dates[i-1], '%Y-%m-%d').date()
        curr_date = datetime.datetime.strptime(dates[i], '%Y-%m-%d').date()
        
        if (curr_date - prev_date).days == 1:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 1
    
    longest_streak = max(longest_streak, temp_streak)
    
    # Calculate current streak
    if dates:
        last_date = datetime.datetime.strptime(dates[-1], '%Y-%m-%d').date()
        today = datetime.date.today()
        if (today - last_date).days <= 1:
            current_streak = temp_streak
    
    # Mood distribution as percentages
    total_entries = len(mood_data)
    mood_distribution = {
        mood: (count / total_entries) * 100 
        for mood, count in mood_counts.items()
    }
    
    return {
        'total_entries': total_entries,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'most_common_mood': most_common_mood,
        'mood_distribution': mood_distribution,
        'weekly_average': total_entries / max(len(set([entry['date'][:7] for entry in mood_data])), 1)
    }

# Export the app for Vercel
application = app

@app.context_processor
def inject_user():
    """Make get_current_user available in all templates."""
    return dict(get_current_user=get_current_user)

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='127.0.0.1', port=5000)
else:
    # For production (Vercel)
    app.run(debug=False)