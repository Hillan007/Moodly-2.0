# Moodly-2.0
# 🌟 Moodly - Emotional Journaling App for Tweens & Young Adults

A Flask-based web application that helps tweens and young adults (ages 14-29) develop emotional intelligence through guided journaling, mood tracking, and personalized wellness features.

## 🚀 **Live Demo**: [https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)

Try Moodly now without any setup - it's live and ready to use!

## ✨ Features

### 🔐 User Authentication & Profiles
- **User Registration**: Secure account creation with password strength validation
- **Login System**: Login with username or email, "Remember Me" option
- **Profile Management**: Personalized profiles with bio and profile pictures
- **Password Security**: PBKDF2 hashing, rate limiting, and secure sessions
- **Progress Tracking**: Personal statistics and mood analytics

### Core Wellness Features
- **Mood Selection**: Emoji-based mood picker with 8 different emotions
- **AI-Powered Prompts**: Contextual journaling prompts based on selected mood
- **Journal Writing**: Safe space for personal expression and reflection
- **🎵 Music Recommendations**: Spotify-powered mood-based song suggestions with preview playback
- **Mood Tracking**: Visual timeline of emotional journey over time
- **Privacy-First**: Secure data handling with user authentication
- **Age-Appropriate**: Designed for tweens and young adults with appropriate content

### 🆕 Advanced Wellness Features
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

### 🔒 Security Features
- **Password Strength Validation**: Real-time feedback with strength meter
- **Rate Limiting**: Protection against brute force attacks (5 attempts per 15 minutes)
- **Session Management**: Secure sessions with configurable duration
- **Input Validation**: Comprehensive validation for all user inputs

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

### For New Users:
1. **Create Account**: Sign up with username, email, and age (14-29)
2. **Complete Profile**: Add a bio and profile picture (local version)
3. **Choose Your Mood**: Select from 8 emoji-based mood options
4. **Explore Wellness Tools**: Access breathing exercises, coping strategies, or journal templates
5. **Get a Prompt**: Receive an age-appropriate journaling prompt or use a structured template
6. **🎵 Discover Music**: Get mood-based song recommendations with preview playbook
7. **Write Freely**: Express thoughts and feelings in your personal journal
8. **Track Progress**: View your emotional journey, streaks, and patterns over time
9. **Unlock Achievements**: Build consistency and unlock wellness badges
10. **Build Skills**: Learn coping strategies and practice breathing exercises

### For Returning Users:
1. **Sign In**: Login with your username/email and password
2. **Review Progress**: Check your profile stats and recent entries
3. **Continue Journey**: Pick up where you left off with mood tracking
4. **Explore Growth**: View analytics and celebrate achievements

## 🔧 Configuration

### User Accounts
- **Age Requirement**: Users must be between 14-29 years old
- **Profile Features**: Bio (500 characters), profile pictures (local only)
- **Session Duration**: 30 days with "Remember Me" option
- **Password Requirements**: Minimum 6 characters with letters and numbers

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
├── moodly_app.py          # Main Flask application with authentication & wellness features
├── index.py               # Vercel deployment entry point
├── app.py                 # Alternative entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .vercelignore         # Vercel deployment ignore file
├── vercel.json           # Vercel deployment configuration
├── DEPLOYMENT_FIXES.md   # Deployment troubleshooting guide
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation & auth links
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
│   ├── template_journal.html # Structured journaling with templates
│   └── auth/             # Authentication templates
│       ├── signup.html   # User registration form
│       ├── login.html    # User login form
│       ├── profile.html  # User profile dashboard
│       ├── edit_profile.html # Profile editing form
│       ├── profile_setup.html # New user welcome
│       └── change_password.html # Password change form
└── static/               # Static assets
    ├── style.css         # Custom styles
    └── uploads/          # User-uploaded files (local only)
        └── profiles/     # Profile pictures (local only)
```
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

## 🛡️ Privacy & Security

### Data Protection
- **Secure Authentication**: PBKDF2 password hashing with salt
- **Session Security**: Secure session cookies with configurable duration
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Comprehensive validation for all user inputs
- **Local File Storage**: Profile pictures stored locally (development only)

### Privacy Features
- **Personal Accounts**: Each user has their own private journal space
- **No External Tracking**: No analytics or user behavior tracking
- **Age Verification**: Age restriction enforcement (14-29 years)
- **Safe Environment**: Positive, supportive tone throughout the application

### Production vs Development
- **Production (Vercel)**: File uploads disabled, optimized for serverless
- **Development (Local)**: Full features including profile picture uploads
- **Environment Detection**: Automatic feature adjustment based on environment

## 🌍 Educational Value

Moodly supports several UN Sustainable Development Goals:
- **Goal 3**: Good Health and Well-being
- **Goal 4**: Quality Education (emotional learning)
- **Goal 10**: Reduced Inequalities (accessible mental health tools)

## 🔄 Recent Updates & Enhancements

### 🆕 Version 2.1 - Authentication & Security
- ✅ **Complete User Authentication System**
- ✅ **Profile Management with Pictures**
- ✅ **Password Security & Rate Limiting**
- ✅ **Session Management**
- ✅ **Vercel Deployment Fixes**
- ✅ **Production Optimizations**

All the recommended features have been successfully implemented:

### ✅ **Immediate Enhancements (High Impact)**
- **Enhanced Mood Tracking & Analytics**: Mood streaks, weekly/monthly summaries, pattern recognition
- **Improved Music Experience**: Enhanced playlists with mood matching scores
- **Enhanced Journaling Features**: 4 structured templates (gratitude, daily reflection, worry dump, dream big)
- **Achievement System**: 8 progressive achievements with beautiful UI

### ✅ **Previous Enhancements**
- **AI-Powered Insights**: Pattern analysis and mood prediction
- **Wellness Integration**: Breathing exercises, coping strategies, mindfulness activities
- **Educational Content**: Age-appropriate emotional intelligence resources
- **Customization & Personalization**: Enhanced UI with dropdown navigation
- **Gamification Elements**: Achievement badges, progress tracking, mood streaks
- **Export & Memory Features**: Visual analytics and progress summaries
- **Enhanced Safety Features**: Crisis resources, emergency contacts, mental health resources
- **Technical Improvements**: Enhanced navigation, responsive design, API endpoints

## 🤝 For Educators, Parents & Young Adults

Moodly can be a valuable tool for:
- **Teaching emotional vocabulary** and self-awareness
- **Encouraging self-reflection** and mindfulness practices
- **Opening conversations** about mental health and feelings
- **Supporting emotional wellness** for tweens and young adults
- **Building emotional resilience** through consistent practice
- **Creating healthy habits** around emotional expression
- **Providing safe space** for personal growth and exploration

## 🚀 Deployment & Usage

### 🌐 Live Deployment
Moodly is live and accessible at: **[https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)**
- ✅ Fully functional authentication system
- ✅ All wellness features available
- ⚠️ Profile picture uploads disabled (use local version for this feature)

### 💻 Local Development
For full features including profile picture uploads:

1. **Clone the repository**
2. **Set up environment variables** (see Configuration section)
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run locally**: `python moodly_app.py`
5. **Access at**: `http://localhost:5000`

### 🔧 Environment Variables
Optional configuration for enhanced features:
```bash
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-openai-key-for-ai-prompts
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
```

### 📊 Health Check
Monitor deployment status at: `/health` endpoint

## 💡 Getting Started

1. **Visit** [https://moodly-2-0.vercel.app/](https://moodly-2-0.vercel.app/)
2. **Sign Up** for your free account (ages 14-29)
3. **Complete** your profile setup
4. **Start** tracking your emotional wellness journey
5. **Explore** breathing exercises, coping strategies, and journal templates
6. **Unlock** achievements as you build healthy habits

## 📄 License & Support

This project is designed for educational and therapeutic use with tweens and young adults. Please ensure compliance with local privacy laws and educational guidelines when deploying.

For support or questions, check the deployment guide at `DEPLOYMENT_FIXES.md` or create an issue in the repository.

---

**Remember: It's okay to feel all your feelings. You're doing great! 🌟**
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
