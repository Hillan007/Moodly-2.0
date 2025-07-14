# 🧪 Local Testing Guide for Moodly App

This guide will help you test your Moodly app on localhost before deploying to Vercel.

## 📋 Prerequisites

1. **Python 3.7+** installed on your system
2. **pip** (Python package installer)
3. **Git** (optional, for version control)

## 🚀 Quick Start Instructions

### Step 1: Verify Your Environment

Open PowerShell or Command Prompt and navigate to your project folder:

```powershell
cd "d:\PLP Academy\Moodly_App"
```

Check if Python is installed:
```powershell
python --version
```

### Step 2: Set Up Virtual Environment (Recommended)

Create a virtual environment to keep dependencies isolated:

```powershell
python -m venv moodly_env
```

Activate the virtual environment:
```powershell
# On Windows PowerShell
.\moodly_env\Scripts\Activate.ps1

# On Windows Command Prompt
moodly_env\Scripts\activate.bat
```

You should see `(moodly_env)` at the beginning of your command prompt.

### Step 3: Install Dependencies

Install all required packages:
```powershell
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

1. Copy the example environment file:
   ```powershell
   copy .env.example .env
   ```

2. Edit the `.env` file with your preferred text editor and add your API keys:
   ```
   SECRET_KEY=your-super-secret-key-here
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   OPENAI_API_KEY=your_openai_api_key_optional
   ```

   **Note:** Spotify and OpenAI keys are optional - the app has fallback functionality!

### Step 5: Run the Application

You have several options to start the app:

**Option A: Using the batch file (Easiest)**
```powershell
.\run_app.bat
```

**Option B: Using Python directly**
```powershell
python moodly_app.py
```

**Option C: Using Flask command**
```powershell
set FLASK_APP=moodly_app.py
set FLASK_ENV=development
flask run
```

### Step 6: Test in Browser

1. Open your web browser
2. Navigate to: `http://localhost:5000` or `http://127.0.0.1:5000`
3. You should see the Moodly app homepage!

## 🧪 Testing Features

### Core Features to Test:

1. **Homepage Navigation**
   - Visit `http://localhost:5000`
   - Try clicking different mood buttons
   - Check if all mood emojis display correctly

2. **Journaling Flow**
   - Select a mood
   - Write a journal entry
   - Submit and check for success message
   - Verify music recommendations appear

3. **Mood Tracker**
   - Go to `http://localhost:5000/tracker`
   - Check if your entries appear
   - Verify mood timeline displays

4. **Wellness Hub**
   - Visit `http://localhost:5000/wellness`
   - Test breathing exercises
   - Check analytics display

5. **Templates System**
   - Go to `http://localhost:5000/templates`
   - Try different journal templates
   - Submit template entries

6. **Achievements System**
   - Visit `http://localhost:5000/achievements`
   - Create multiple entries to unlock achievements

### API Endpoints to Test:

Test these URLs directly in your browser:
- `http://localhost:5000/api/music/happy`
- `http://localhost:5000/api/analytics`
- `http://localhost:5000/api/coping/anxious`

## 🔧 Troubleshooting

### Common Issues:

**Port 5000 already in use:**
```powershell
# Kill any process using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Module not found errors:**
```powershell
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**Template not found errors:**
- Check that all HTML files exist in `templates/` folder
- Verify file permissions

**Static files not loading:**
- Check that `static/style.css` exists
- Clear browser cache (Ctrl+F5)

### Debug Mode:

For detailed error messages, run with debug enabled:
```powershell
set FLASK_ENV=development
python moodly_app.py
```

## 📝 Testing Checklist

Use this checklist to ensure everything works:

- [ ] App starts without errors
- [ ] Homepage loads correctly
- [ ] Can select moods and see journaling page
- [ ] Can write and submit journal entries
- [ ] Music recommendations display (or fallback works)
- [ ] Mood tracker shows entries
- [ ] Wellness hub features work
- [ ] Journal templates function
- [ ] Breathing exercises load
- [ ] Coping strategies display
- [ ] Achievements system works
- [ ] Navigation between pages works
- [ ] Mobile responsive design looks good
- [ ] All API endpoints respond correctly

## 🔄 Making Changes

While testing locally:

1. **For Python changes:** Stop the server (Ctrl+C) and restart
2. **For HTML/CSS changes:** Just refresh the browser
3. **For new dependencies:** Add to `requirements.txt` and run `pip install -r requirements.txt`

## 🌐 Ready for Deployment

Once local testing is successful:

1. Commit your changes to Git
2. Push to your repository
3. Deploy to Vercel using the existing `vercel.json` configuration
4. Set environment variables in Vercel dashboard

## 🆘 Need Help?

If you encounter issues:

1. Check the terminal output for error messages
2. Look at browser developer console (F12) for JavaScript errors
3. Verify all files are in the correct locations
4. Ensure virtual environment is activated
5. Try restarting the Flask server

Happy testing! 🎉
