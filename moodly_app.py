from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import datetime
from datetime import date, timedelta
# from openai import OpenAI  # Temporarily disabled
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from dotenv import load_dotenv
import requests
import base64
import random
import statistics
from collections import defaultdict, Counter

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure OpenAI client (you'll need to set your API key)
# Temporarily disabled to avoid dependency issues
openai_client = None
# try:
#     if os.environ.get('OPENAI_API_KEY'):
#         openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
# except Exception as e:
#     print(f"OpenAI client initialization error: {e}")
#     print("App will continue with fallback prompts.")

# Data storage (in production, use a proper database)
JOURNAL_ENTRIES = {}
USER_DATA = {}

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

def get_ai_prompt(mood, user_age=12):
    """Generate an AI journaling prompt based on mood"""
    if not openai_client:
        # Fallback prompts if OpenAI is not configured
        fallback_prompts = {
            'happy': "What made you smile today? Describe a moment that brought you joy!",
            'sad': "It's okay to feel sad sometimes. What would help you feel a little better?",
            'excited': "Your excitement is contagious! What are you looking forward to?",
            'anxious': "Take a deep breath. What's one small thing you can do to feel calmer?",
            'calm': "You seem peaceful today. What helps you stay centered?",
            'angry': "Strong feelings are normal. What triggered this feeling?",
            'confused': "When we're confused, writing can help clarify our thoughts. What's on your mind?",
            'grateful': "Gratitude is a superpower! What are three things you're thankful for today?"
        }
        return fallback_prompts.get(mood, "How are you feeling today? Write about what's in your heart.")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a supportive journaling assistant for tweens (ages 10-14). Generate age-appropriate, encouraging journaling prompts. Keep language simple, positive, and engaging. The user is feeling {mood}."},
                {"role": "user", "content": f"Generate a supportive journaling prompt for a {user_age}-year-old who is feeling {mood}. Make it encouraging and age-appropriate."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Return fallback prompt
        fallback_prompts = {
            'happy': "What made you smile today? Describe a moment that brought you joy!",
            'sad': "It's okay to feel sad sometimes. What would help you feel a little better?",
            'excited': "Your excitement is contagious! What are you looking forward to?",
            'anxious': "Take a deep breath. What's one small thing you can do to feel calmer?",
            'calm': "You seem peaceful today. What helps you stay centered?",
            'angry': "Strong feelings are normal. What triggered this feeling?",
            'confused': "When we're confused, writing can help clarify our thoughts. What's on your mind?",
            'grateful': "Gratitude is a superpower! What are three things you're thankful for today?"
        }
        return fallback_prompts.get(mood, "How are you feeling today? Write about what's in your heart.")

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
    if mood_key not in MOODS:
        return redirect(url_for('index'))
    
    mood_info = MOODS[mood_key]
    prompt = get_ai_prompt(mood_key)
    songs = get_mood_songs(mood_key, limit=5)
    
    return render_template('journal.html', 
                         mood=mood_info, 
                         mood_key=mood_key,
                         prompt=prompt,
                         songs=songs)

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
def analytics_page():
    """Detailed analytics page"""
    user_id = get_user_id()
    analytics = get_mood_analytics(user_id)
    patterns = predict_mood_patterns(user_id)
    
    return render_template('analytics.html', 
                         analytics=analytics,
                         patterns=patterns,
                         moods=MOODS)

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

@app.route('/api/analytics')
def analytics_api():
    """API endpoint for analytics data"""
    user_id = get_user_id()
    analytics = get_mood_analytics(user_id)
    patterns = predict_mood_patterns(user_id)
    
    return jsonify({
        'analytics': analytics,
        'patterns': patterns
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)