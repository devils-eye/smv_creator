# Slideshow Video Maker

A desktop application that converts a series of images into a polished video with customizable transitions and effects.

## Features

- **Image Input**: Upload multiple images to include in your video
- **Per-Image Customization**:
  - Choose starting transitions (fade in, slide in, zoom in, etc.)
  - Choose ending transitions (fade out, zoom out, slide out, etc.)
  - Apply special effects (zoom, color filters, rotation, etc.)
  - Apply overlay effects (watermark, text caption, frame, etc.)
  - Set individual display durations
- **Global Video Settings**:
  - Set aspect ratio (16:9, 9:16, 4:3)
  - Choose frame rate (24fps, 30fps, etc.)
  - Adjust transition overlap
  - Apply global settings to all images
  - Use random transitions and effects
  - Apply default profile settings
- **Video Output**: Export as MP4 video file

## Global Settings Options

- **Manual Mode**: Manually set transitions and effects for all images
- **Random Mode**: Randomly apply transitions and effects to each image
- **Default Profile**: Apply a predefined set of transitions and effects (Fade In/Out with Zoom In)

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt

## License

MIT
