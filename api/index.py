import sys
import os

# Add the parent directory to Python path  
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from moodly_app import app
    
    # Export the app
    application = app
    
except Exception as e:
    print(f"Error importing app: {e}")
    raise
