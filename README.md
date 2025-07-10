# Moodly-2.0
# 🌟 Moodly - Emotional Journaling App for Tweens

A Flask-based web application that helps tweens (ages 10-14) develop emotional intelligence through guided journaling, mood tracking, and AI-powered prompts.

## 🚀 **Live Demo**: [https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)

Try Moodly now without any setup - it's live and ready to use!

## ✨ Features

- **Mood Selection**: Emoji-based mood picker with 8 different emotions
- **AI-Powered Prompts**: Contextual journaling prompts based on selected mood
- **Journal Writing**: Safe space for tweens to express their thoughts and feelings
- **🎵 Music Recommendations**: Spotify-powered mood-based song suggestions with preview playback
- **Mood Tracking**: Visual timeline of emotional journey over time
- **Privacy-First**: No personal data stored externally, session-based storage
- **Age-Appropriate**: Designed specifically for tweens with appropriate language and tone
- **Motivational Messages**: Uplifting feedback after each journal entry
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

**🌐 Use Online**: Visit [https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/) to use Moodly instantly without any setup!

**💻 Run Locally**: Follow the steps below to run Moodly on your own computer:

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd "d:\PLP Academy\Moodly_App"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional)**
   ```bash
   copy .env.example .env
   ```
   Edit the `.env` file and add your OpenAI API key if you want AI-generated prompts. The app works without it using fallback prompts.

4. **Run the application**
   ```bash
   python moodly_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How It Works

1. **Choose Your Mood**: Select from 8 emoji-based mood options
2. **Get a Prompt**: Receive an age-appropriate journaling prompt
3. **🎵 Discover Music**: Get mood-based song recommendations with preview playback
4. **Write Freely**: Express thoughts and feelings in a safe, private space
5. **Get Encouragement**: Receive motivational messages after writing
6. **Track Progress**: View your emotional journey over time

## 🔧 Configuration

### OpenAI Integration (Optional)
To enable AI-generated prompts, add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

Without an API key, the app uses carefully crafted fallback prompts for each mood.

### Spotify Integration (Optional)
To enable real-time music recommendations, you'll need to set up Spotify API credentials:

1. **Create a Spotify App**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Click "Create an App"
   - Fill in the app name and description
   - Accept the terms and create the app

2. **Get your credentials**:
   - Copy the Client ID and Client Secret from your app dashboard
   - Add them to your `.env` file:
   ```
   SPOTIFY_CLIENT_ID=your-client-id-here
   SPOTIFY_CLIENT_SECRET=your-client-secret-here
   ```

Without Spotify credentials, the app uses curated fallback music recommendations for each mood.

### Flask Configuration
```
SECRET_KEY=your-secret-key-for-sessions
FLASK_ENV=development
```

## 📁 Project Structure

```
Moodly_App/
├── moodly_app.py          # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── PRD.MD                # Product Requirements Document
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with common layout
│   ├── index.html        # Home page with mood selection
│   ├── journal.html      # Journaling page
│   ├── tracker.html      # Mood tracking timeline
│   └── about.html        # About page
└── static/               # Static assets
    └── style.css         # Additional custom styles
```

## 🎨 Moods Supported

- 😊 Happy
- 😢 Sad  
- 🤩 Excited
- 😰 Anxious
- 😌 Calm
- 😠 Angry
- 😕 Confused
- 🙏 Grateful

## 🛡️ Privacy & Safety

- **No External Data Storage**: Journal entries are stored in browser sessions only
- **Age-Appropriate Content**: All prompts and messages designed for tweens
- **No User Tracking**: No analytics or user behavior tracking
- **Safe Environment**: Positive, supportive tone throughout the application

## 🌍 Educational Value

Moodly supports several UN Sustainable Development Goals:
- **Goal 3**: Good Health and Well-being
- **Goal 4**: Quality Education (emotional learning)
- **Goal 10**: Reduced Inequalities (accessible mental health tools)

## 🔄 Future Enhancements

Based on the PRD, potential future features include:
- Spotify integration for mood-based music suggestions
- Voice-to-text journaling
- Export/backup functionality
- Educator dashboard
- Parent/guardian insights (with permission)

## 🤝 For Educators & Parents

Moodly can be a valuable tool for:
- Teaching emotional vocabulary
- Encouraging self-reflection
- Opening conversations about feelings
- Supporting mental health awareness
- Building emotional resilience

## 🚀 Deployment

### Live Deployment
Moodly is live and accessible at: **[https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)**

### Local Development
For production deployment on your own server:

1. **Set up a production environment**
2. **Configure environment variables**
3. **Use a production WSGI server like Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 moodly_app:app
   ```

## 📄 License

This project is designed for educational and therapeutic use with tweens. Please ensure compliance with local privacy laws and educational guidelines when deploying.

## 🆘 Support

For questions about emotional wellness resources for tweens, consult with:
- School counselors
- Mental health professionals
- Pediatric psychologists
- Educational therapists

---

**Remember**: Every feeling is valid, every thought matters, and you're doing amazing by taking care of your emotional health! 🌟
