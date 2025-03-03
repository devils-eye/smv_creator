"""
ImageItem class for storing image settings
"""

import os
from pathlib import Path


class ImageItem:
    """Class to store image settings and metadata"""
    
    def __init__(self, filepath):
        """Initialize with default settings"""
        self.filepath = filepath
        
        # Default settings
        self.duration = 3.0  # seconds
        self.start_transition = "Fade In"
        self.start_duration = 1.0  # seconds
        self.end_transition = "Fade Out"
        self.end_duration = 1.0  # seconds
        self.effect = "None"
    
    def get_filename(self):
        """Get the filename without path"""
        return os.path.basename(self.filepath)
    
    def get_total_duration(self):
        """Get the total duration including transitions"""
        # The total duration is the base duration plus any non-overlapping parts of transitions
        return self.duration
    
    def __str__(self):
        """String representation"""
        return f"ImageItem({self.get_filename()}, duration={self.duration}s)" 