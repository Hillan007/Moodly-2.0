# GitHub Copilot Instructions for Moodly 2.0

## Project Overview

Moodly is an emotional journaling web application designed for tweens and young adults (ages 14-29). It helps users develop emotional intelligence through guided journaling, mood tracking, and personalized wellness features.

**Live Demo**: https://moodly-2-0.vercel.app/

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3 (Python web framework)
- **Database/Storage**: Supabase (PostgreSQL + Storage)
- **Authentication**: Flask sessions with Werkzeug password hashing (PBKDF2)
- **Environment**: Python 3.8+ (minimum), Python 3.9 (production/Vercel) with python-dotenv for configuration
- **Image Processing**: Pillow (PIL) for profile pictures

### Frontend
- **Templates**: Jinja2 (Flask's default templating engine)
- **Styling**: Custom CSS in `/static/style.css`
- **JavaScript**: Vanilla JavaScript for interactive features
- **Responsive Design**: Mobile-first approach

### External APIs (Optional)
- **OpenAI API**: For AI-generated journaling prompts (has fallback prompts)
- **Spotify API**: For mood-based music recommendations (has fallback playlists)

### Deployment
- **Platform**: Vercel (serverless)
- **Configuration**: `vercel.json` with Python runtime
- **Entry Point**: `/api/index.py` (wraps `moodly_app.py`)

## Project Structure

```
/
├── .github/
│   ├── agents/                    # Custom agent configurations
│   └── copilot-instructions.md    # This file
├── api/
│   └── index.py                   # Vercel entry point
├── static/
│   ├── style.css                  # Main stylesheet
│   └── uploads/profiles/          # Local profile pictures (dev only)
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── index.html                 # Mood selection homepage
│   ├── journal.html               # Journaling interface
│   ├── tracker.html               # Mood tracking timeline
│   ├── analytics.html             # Mood analytics dashboard
│   ├── achievements.html          # Achievement system
│   ├── wellness.html              # Wellness hub
│   ├── breathing.html             # Breathing exercises
│   ├── coping.html                # Coping strategies
│   ├── templates.html             # Journal templates selector
│   ├── template_journal.html      # Template-based journaling
│   ├── about.html                 # About page
│   └── auth/                      # Authentication templates
│       ├── signup.html
│       ├── login.html
│       ├── profile.html
│       ├── edit_profile.html
│       ├── profile_setup.html
│       └── change_password.html
├── moodly_app.py                  # Main Flask application
├── supabase_storage.py            # Supabase storage helper
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── vercel.json                    # Vercel deployment config
```

## Coding Standards & Best Practices

### Python Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable names (e.g., `user_id`, `mood_data`, `journal_entry`)
- Add docstrings for functions and classes
- Keep functions focused and single-purpose
- Use type hints where appropriate

### Flask Patterns
- Use Flask's `session` for user authentication state
- Always use `flash()` for user feedback messages
- Use `url_for()` for generating URLs (never hardcode paths)
- Apply `@login_required` decorator for protected routes
- Return proper HTTP status codes (200, 400, 404, etc.)

### HTML/Template Patterns
- Extend `base.html` for consistent layout
- Use Jinja2 template inheritance (`{% extends "base.html" %}`)
- Place page-specific content in `{% block content %}`
- Use semantic HTML5 elements (`<nav>`, `<section>`, `<article>`)
- Include accessibility attributes (`aria-label`, `alt` text)

### JavaScript Patterns
- Use vanilla JavaScript (no jQuery or frameworks)
- Keep JavaScript in `<script>` tags within templates
- Use event delegation for dynamic content
- Provide fallbacks for failed API calls
- Keep client-side code minimal and focused

### CSS Patterns
- Use mobile-first responsive design
- Leverage CSS variables for theming (colors, spacing)
- Keep styles modular and reusable
- Use meaningful class names (e.g., `.mood-card`, `.achievement-badge`)
- Ensure accessibility (sufficient contrast, focus states)

## Architecture Patterns

### Serverless-First Design
The application is designed to run both locally and on serverless platforms (Vercel):

```python
# Ultra-robust serverless environment detection
IS_SERVERLESS = (
    '/var/task' in os.getcwd() or 
    '/var/task' in __file__ or  # Check if the file itself is in /var/task
    os.environ.get('VERCEL') is not None or  # Any VERCEL env var
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or 
    os.environ.get('NOW_REGION') is not None or 
    'LAMBDA_RUNTIME_DIR' in os.environ or
    os.path.exists('/var/task') or  # Check if /var/task exists
    'vercel' in os.getcwd().lower() or  # Sometimes vercel uses different paths
    'lambda' in os.getcwd().lower()  # AWS Lambda detection
)
```

**Note**: See `moodly_app.py` lines 81-115 for the complete serverless detection implementation with failsafe mechanisms.

**Critical Rules:**
1. **Never use local file system** for persistent storage in production
2. **Always use Supabase** for file uploads (profile pictures)
3. **Detect environment** before any file operations
4. **Disable file uploads** in serverless environments
5. **Use environment variables** for all configuration

### Data Storage
- **User Data**: Stored in Python dictionaries (in-memory for MVP)
- **Profile Pictures**: Supabase Storage (production) or local files (development)
- **Session Data**: Flask sessions with secure cookies
- **Future**: Migrate to Supabase PostgreSQL for persistent storage

### Authentication Flow
1. User registers with username, email, age validation
2. Password hashed with PBKDF2 (Werkzeug)
3. Login creates Flask session with user data
4. Rate limiting: 5 attempts per 15 minutes
5. Session persists for 30 days with "Remember Me"

### Error Handling
- Use try-except blocks for external API calls
- Provide fallback data when APIs fail
- Log errors to console (use `print()` for debugging)
- Show user-friendly error messages via `flash()`
- Never expose sensitive error details to users

## Feature-Specific Guidelines

### Mood Selection (8 Moods)
Supported moods with emojis:
- 😊 Happy
- 😢 Sad
- 🤩 Excited
- 😰 Anxious
- 😌 Calm
- 😠 Angry
- 😕 Confused
- 🙏 Grateful

When adding mood-related features:
- Always support all 8 moods
- Use emoji + text labels
- Provide mood-specific content (prompts, music, coping strategies)
- Use consistent color coding across the app

### Journal Entries
Structure:
```python
{
    'id': str(uuid.uuid4()),
    'user_id': str,
    'mood': str,  # One of the 8 moods
    'prompt': str,
    'entry': str,
    'date': str,  # ISO format
    'timestamp': datetime
}
```

### Wellness Features
1. **Breathing Exercises**: 4 types (anxious, angry, sad, excited)
2. **Coping Strategies**: Evidence-based techniques per mood
3. **Journal Templates**: 4 types (Gratitude, Daily Reflection, Worry Release, Dreams & Goals)
4. **Achievement System**: 8 unlockable badges

### Music Recommendations
- Use Spotify API when credentials available
- Fall back to curated playlists when API unavailable
- Match songs to user's selected mood
- Provide preview links and Spotify integration

## Security Guidelines

### Authentication
- **Never** store passwords in plain text
- Always use `generate_password_hash()` for passwords
- Validate password strength (min 6 chars, letters + numbers)
- Implement rate limiting for login attempts
- Clear sensitive data from sessions on logout

### Input Validation
- Validate all user inputs (age, username, email)
- Sanitize file uploads (profile pictures)
- Escape user content in templates (Jinja2 auto-escapes)
- Limit file sizes and types for uploads
- Use `secure_filename()` for file handling

### Session Security
```python
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = True  # In production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### API Keys & Secrets
- **Never** commit API keys to the repository
- Use environment variables for all secrets
- Provide `.env.example` with placeholder values
- Document required environment variables in README
- Keys to protect: `SECRET_KEY`, `OPENAI_API_KEY`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SUPABASE_URL`, `SUPABASE_KEY`

## Testing Guidelines

### Manual Testing
The project uses manual testing (see `TESTING_GUIDE.md`). When making changes:

1. **Test locally first**: Run `python moodly_app.py`
2. **Test all affected features**: Don't just test the changed code
3. **Test different user states**: Logged in, logged out, new user
4. **Test different moods**: Ensure all 8 moods work
5. **Test mobile view**: Use responsive design mode
6. **Check browser console**: Look for JavaScript errors

### Test Files
- `test_features.py`: Feature testing script
- `test_supabase.py`: Supabase integration tests
- `test_supabase_complete.py`: Complete Supabase test suite

Run tests with:
```bash
python test_features.py
python test_supabase.py
```

## Deployment Considerations

### Environment Variables
Required for production:
```bash
SECRET_KEY=your-production-secret-key
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
FORCE_SUPABASE_ONLY=true  # Disable local file storage
```

Optional:
```bash
OPENAI_API_KEY=your-openai-key
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
```

### Vercel Deployment
1. Entry point is `/api/index.py`
2. Static files served from `/static/`
3. Python version: 3.9 (configured in `vercel.json`)
4. File uploads disabled in serverless mode
5. Use Supabase for all storage needs

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`
3. Run: `python moodly_app.py`
4. Access: `http://localhost:5000`

## Age-Appropriate Content

**Target Audience**: Ages 14-29 (tweens and young adults)

Content Guidelines:
- Use encouraging, positive language
- Avoid patronizing or overly childish tone
- Keep mental health resources appropriate for age group
- Ensure prompts and content are emotionally safe
- Avoid triggering content (violence, explicit themes)
- Focus on emotional growth and self-awareness

## Common Tasks

### Adding a New Route
```python
@app.route('/new-feature')
@login_required
def new_feature():
    user_id = session.get('user_id')
    # Your logic here
    return render_template('new_feature.html')
```

### Adding a New Template
1. Create file in `/templates/new_feature.html`
2. Extend base template: `{% extends "base.html" %}`
3. Add content block: `{% block content %}...{% endblock %}`
4. Update navigation in `base.html` if needed

### Adding a New API Endpoint
```python
@app.route('/api/new-endpoint', methods=['POST'])
def api_new_endpoint():
    try:
        data = request.get_json()
        # Process data
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
```

### Adding a New Mood-Based Feature
1. Support all 8 moods (Happy, Sad, Excited, Anxious, Calm, Angry, Confused, Grateful)
2. Use consistent emoji representation
3. Provide mood-specific content/behavior
4. Update relevant UI components (mood selector, tracker, analytics)

## Important Files to Preserve

**Do NOT modify without understanding**:
- `moodly_app.py` lines 1-27 (nuclear protection system that prevents file operations in serverless)
- `moodly_app.py` lines 81-155 (comprehensive serverless detection and storage configuration)
- `vercel.json` (deployment configuration)
- `/api/index.py` (Vercel entry point)
- `.env.example` (environment template)

**Modify carefully**:
- `base.html` (affects all pages)
- `static/style.css` (affects entire app styling)
- Authentication logic (security-critical)

## Resources & Documentation

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Jinja2 Templates**: https://jinja.palletsprojects.com/
- **Supabase Docs**: https://supabase.com/docs
- **Vercel Python**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Project README**: See `/README.md` for user-facing documentation
- **Testing Guide**: See `/TESTING_GUIDE.md` for testing procedures
- **Security Policy**: See `/SECURITY.md` for security guidelines

## Need Help?

- Check existing code for similar patterns
- Review `README.md` for project overview
- See `TESTING_GUIDE.md` for feature testing
- Check `SECURITY.md` for security best practices
- Contact: victorhillan007@gmail.com

## Summary for GitHub Copilot

When assisting with this project:
1. **Maintain serverless compatibility** - Always check `IS_SERVERLESS` before file operations
2. **Use established patterns** - Follow Flask, Jinja2, and project-specific conventions
3. **Preserve security** - Never compromise authentication or input validation
4. **Support all moods** - Ensure new features work with all 8 mood types
5. **Age-appropriate content** - Keep language and features suitable for 14-29 age group
6. **Test thoroughly** - Consider both local and production environments
7. **Document changes** - Update relevant documentation when adding features
8. **Fallback gracefully** - Provide alternatives when external APIs fail
