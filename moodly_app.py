from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import datetime
from datetime import date
# from openai import OpenAI  # Temporarily disabled
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from dotenv import load_dotenv
import requests
import base64

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
def home():
    return render_template('index.html', moods=MOODS)

@app.route('/mood/<mood_key>')
def mood_selected(mood_key):
    if mood_key not in MOODS:
        return redirect(url_for('home'))
    
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)