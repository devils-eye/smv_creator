#!/usr/bin/env python3
"""
Run script for the Slideshow Video Maker application
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from main import main

if __name__ == "__main__":
    main() 