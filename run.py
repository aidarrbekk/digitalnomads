#!/usr/bin/env python
"""
Entry point for the Digital Nomads Flask application
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main.app import app

if __name__ == '__main__':
    app.run(debug=True)
