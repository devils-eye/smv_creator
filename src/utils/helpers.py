"""
Helper functions for the Slideshow Video Maker application
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox


def get_supported_image_extensions():
    """Return a list of supported image file extensions"""
    return [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]


def is_valid_image_file(filepath):
    """Check if a file is a valid image file"""
    if not os.path.isfile(filepath):
        return False
    
    ext = os.path.splitext(filepath)[1].lower()
    return ext in get_supported_image_extensions()


def format_time(seconds):
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def get_aspect_ratio_dimensions(aspect_ratio, base_height=1080):
    """Get dimensions for a given aspect ratio"""
    if aspect_ratio == "16:9":
        return (int(base_height * 16 / 9), base_height)
    elif aspect_ratio == "4:3":
        return (int(base_height * 4 / 3), base_height)
    elif aspect_ratio == "1:1":
        return (base_height, base_height)
    elif aspect_ratio == "9:16":
        return (base_height, int(base_height * 16 / 9))
    elif aspect_ratio == "21:9":
        return (int(base_height * 21 / 9), base_height)
    else:
        # Default to 16:9
        return (int(base_height * 16 / 9), base_height)


def show_error_message(parent, title, message):
    """Show an error message dialog"""
    QMessageBox.critical(parent, title, message)


def show_info_message(parent, title, message):
    """Show an information message dialog"""
    QMessageBox.information(parent, title, message)


def show_warning_message(parent, title, message):
    """Show a warning message dialog"""
    QMessageBox.warning(parent, title, message)


def get_estimated_file_size(duration, bitrate_kbps):
    """Estimate file size in MB based on duration and bitrate"""
    # Convert duration to seconds and bitrate to bytes per second
    bytes_per_second = bitrate_kbps * 1000 / 8
    total_bytes = duration * bytes_per_second
    
    # Convert to MB
    total_mb = total_bytes / (1024 * 1024)
    
    return total_mb 