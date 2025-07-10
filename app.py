from moodly_app import app

# Vercel expects the app to be available when the module is imported
if __name__ == "__main__":
    app.run()
