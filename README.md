# Moodly-2.0
# 🌟 Moodly - Emotional Journaling App for Tweens

A Flask-based web application that helps tweens (ages 10-14) develop emotional intelligence through guided journaling, mood tracking, and AI-powered prompts.

## 🚀 **Live Demo**: [https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)

Try Moodly now without any setup - it's live and ready to use!

## ✨ Features

### Core Features
- **Mood Selection**: Emoji-based mood picker with 8 different emotions
- **AI-Powered Prompts**: Contextual journaling prompts based on selected mood
- **Journal Writing**: Safe space for tweens to express their thoughts and feelings
- **🎵 Music Recommendations**: Spotify-powered mood-based song suggestions with preview playback
- **Mood Tracking**: Visual timeline of emotional journey over time
- **Privacy-First**: No personal data stored externally, session-based storage
- **Age-Appropriate**: Designed specifically for tweens with appropriate language and tone
- **Motivational Messages**: Uplifting feedback after each journal entry
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🆕 New Wellness Features
- **🧘‍♀️ Breathing Exercises**: Guided breathing exercises for anxiety, anger, sadness, and excitement
- **🏆 Achievement System**: 8 unlockable achievements to encourage consistent journaling
- **📊 Enhanced Analytics**: Mood streaks, pattern analysis, and personalized insights
- **📝 Journal Templates**: 4 structured templates (Gratitude, Daily Reflection, Worry Release, Dreams & Goals)
- **💡 Coping Strategies**: Evidence-based strategies for managing difficult emotions
- **🌟 Wellness Hub**: Centralized access to all wellness tools and resources
- **📈 Mood Predictions**: Simple pattern analysis to help understand emotional trends
- **🎯 Gamification**: Streaks, badges, and progress tracking to maintain engagement
- **🆘 Crisis Resources**: Access to mental health resources and emergency contacts
- **🎨 Enhanced UI**: Improved navigation with dropdowns and better mobile experience

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
2. **Explore Wellness Tools**: Access breathing exercises, coping strategies, or journal templates
3. **Get a Prompt**: Receive an age-appropriate journaling prompt or use a structured template
4. **🎵 Discover Music**: Get mood-based song recommendations with preview playback
5. **Write Freely**: Express thoughts and feelings in a safe, private space
6. **Get Encouragement**: Receive motivational messages and unlock achievements
7. **Track Progress**: View your emotional journey, streaks, and patterns over time
8. **Build Skills**: Learn coping strategies and practice breathing exercises for emotional regulation

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
├── moodly_app.py          # Main Flask application with all wellness features
├── index.py               # Vercel deployment entry point
├── app.py                 # Alternative entry point
├── test_features.py       # Feature testing script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .vercelignore         # Vercel deployment ignore file
├── vercel.json           # Vercel deployment configuration
├── PRD.MD                # Product Requirements Document
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with enhanced navigation
│   ├── index.html        # Home page with mood selection
│   ├── journal.html      # Journaling page
│   ├── tracker.html      # Mood tracking timeline
│   ├── about.html        # About page
│   ├── wellness.html     # Wellness hub dashboard
│   ├── analytics.html    # Advanced mood analytics
│   ├── breathing.html    # Interactive breathing exercises
│   ├── coping.html       # Coping strategies and resources
│   ├── achievements.html # Achievement system
│   ├── templates.html    # Journal template selection
│   └── template_journal.html # Structured journaling with templates
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

## 🔄 Implemented Enhancements

All the recommended features have been successfully implemented:

### ✅ **Immediate Enhancements (High Impact)**
- **Enhanced Mood Tracking & Analytics**: Mood streaks, weekly/monthly summaries, pattern recognition
- **Improved Music Experience**: Enhanced playlists with mood matching scores
- **Enhanced Journaling Features**: 4 structured templates (gratitude, daily reflection, worry dump, dream big)
- **Achievement System**: 8 progressive achievements with beautiful UI

### ✅ **Advanced Features (Higher Impact)**
- **AI-Powered Insights**: Pattern analysis and mood prediction
- **Wellness Integration**: Breathing exercises, coping strategies, mindfulness activities
- **Educational Content**: Age-appropriate emotional intelligence resources
- **Customization & Personalization**: Enhanced UI with dropdown navigation

### ✅ **Creative Additions**
- **Gamification Elements**: Achievement badges, progress tracking, mood streaks
- **Export & Memory Features**: Visual analytics and progress summaries

### ✅ **Safety & Support Enhancements**
- **Enhanced Safety Features**: Crisis resources, emergency contacts, mental health resources
- **Content Moderation**: Age-appropriate guidance and positive messaging

### ✅ **Technical Improvements**
- **Enhanced Navigation**: Dropdown menus, better mobile experience
- **Responsive Design**: Optimized for all devices
- **API Endpoints**: RESTful APIs for achievements, analytics, and coping strategies

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
