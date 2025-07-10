#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from moodly_app import app

# This is the WSGI application
application = app

if __name__ == "__main__":
    app.run(debug=False)
