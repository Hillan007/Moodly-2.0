# 🧪 Moodly App - Local Testing Guide

## ✅ Setup Complete!
Your app is now running locally at: **http://127.0.0.1:5000**

## 🔍 How to Test Each Feature

### 1. **Basic Mood Journaling**
- [ ] Visit the homepage and select different moods
- [ ] Write a journal entry for each mood
- [ ] Check that you get motivational messages after submitting
- [ ] Verify AI prompts appear (fallback prompts work without OpenAI)

### 2. **Mood Tracker & Analytics**
- [ ] Go to "Track Progress" → "Mood Tracker"
- [ ] Verify your entries appear in the timeline
- [ ] Check that mood colors and emojis display correctly
- [ ] Go to "Track Progress" → "Analytics Dashboard"
- [ ] View your mood distribution and insights

### 3. **Achievement System**
- [ ] Go to "Track Progress" → "Achievements"
- [ ] Write your first entry to unlock "First Steps" 👶
- [ ] Try different moods to work toward "Mood Explorer" 🗺️
- [ ] Check the achievement notification system

### 4. **Wellness Tools**
- [ ] Go to "Wellness Hub" → "Breathing Exercises"
- [ ] Try exercises for different moods (anxious, angry, etc.)
- [ ] Go to "Wellness Hub" → "Coping Strategies"
- [ ] Test strategies for different emotional states

### 5. **Journal Templates**
- [ ] Go to "Journal" → "Templates"
- [ ] Try the "Gratitude List" template
- [ ] Test "Daily Check-in" and "Worry Release"
- [ ] Verify template entries save properly

### 6. **Music Recommendations**
- [ ] Write a journal entry and check music suggestions
- [ ] Test different moods to see varied playlists
- [ ] Click on Spotify links to verify they work

### 7. **Mobile Responsiveness**
- [ ] Open browser developer tools (F12)
- [ ] Toggle device toolbar and test mobile view
- [ ] Check navigation menu works on mobile
- [ ] Verify all features work on smaller screens

## 📱 Testing URLs

While your app is running, test these specific pages:

- **Homepage**: http://127.0.0.1:5000/
- **Mood Tracker**: http://127.0.0.1:5000/tracker
- **Analytics**: http://127.0.0.1:5000/analytics
- **Achievements**: http://127.0.0.1:5000/achievements
- **Wellness Hub**: http://127.0.0.1:5000/wellness
- **Templates**: http://127.0.0.1:5000/templates
- **Breathing (Anxious)**: http://127.0.0.1:5000/breathing/anxious
- **Coping (Sad)**: http://127.0.0.1:5000/coping/sad
- **About Page**: http://127.0.0.1:5000/about

## 🔧 API Testing

Test these API endpoints directly:
- **Music API**: http://127.0.0.1:5000/api/music/happy
- **Analytics API**: http://127.0.0.1:5000/api/analytics
- **Achievements API**: http://127.0.0.1:5000/api/achievements/check
- **Coping API**: http://127.0.0.1:5000/api/coping/anxious

## 🚨 Common Issues & Solutions

### App Won't Start?
```powershell
# Check if virtual environment is activated
& "D:/PLP Academy/Moodly_App/.venv/Scripts/python.exe" --version

# Reinstall dependencies if needed
& "D:/PLP Academy/Moodly_App/.venv/Scripts/pip.exe" install -r requirements.txt
```

### Port Already in Use?
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Or change the port in moodly_app.py line 871:
# app.run(debug=True, host='127.0.0.1', port=5001)
```

### Pages Not Loading?
- Check the terminal output for errors
- Verify all template files exist in the `templates/` folder
- Check that `static/style.css` exists

## 🌟 What to Look For

### ✅ Good Signs:
- Clean, colorful interface loads properly
- Mood selection works smoothly
- Journal entries save and appear in tracker
- Achievements unlock as you use features
- Music recommendations appear
- Mobile view looks good
- No error messages in browser console

### ❌ Red Flags:
- 404 errors on any pages
- Broken images or missing styles
- JavaScript errors in browser console
- Music features completely broken
- Templates not saving entries
- Achievement system not working

## 🚀 Next Steps After Testing

1. **If everything works locally**: You're ready to deploy to Vercel!
2. **If you find issues**: Note them down and we can fix them
3. **Want to customize**: You can modify colors, add features, or adjust text

## 💡 Pro Testing Tips

1. **Test with multiple moods** - Try all 8 mood types
2. **Use different browsers** - Test in Chrome, Firefox, Edge
3. **Try the mobile view** - Use responsive design mode
4. **Test the full user journey** - From mood selection to achievement unlock
5. **Check the analytics** - Write multiple entries to see patterns

---

Your app is running at: **http://127.0.0.1:5000**

Have fun testing your creation! 🎉
