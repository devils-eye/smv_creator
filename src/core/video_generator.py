"""
VideoGenerator class for creating videos from images with transitions and effects
"""

import os
import numpy as np
from moviepy.editor import (
    ImageClip, CompositeVideoClip, concatenate_videoclips, 
    ColorClip, vfx, transfx
)


class VideoGenerator:
    """Class to generate videos from images with transitions and effects"""
    
    def __init__(self):
        """Initialize the video generator"""
        # Quality presets (bitrate in kbps)
        self.quality_presets = {
            "Low": 1000,
            "Medium": 2000,
            "High": 5000,
            "Very High": 10000
        }
        
        # Aspect ratio dimensions (width, height)
        self.aspect_ratios = {
            "16:9": (1920, 1080),
            "4:3": (1440, 1080),
            "1:1": (1080, 1080),
            "9:16": (1080, 1920),
            "21:9": (2560, 1080)
        }
    
    def generate_video(self, image_items, output_path, aspect_ratio="16:9", 
                      frame_rate=30, transition_overlap=0.5, quality="High"):
        """Generate a video from the provided image items"""
        if not image_items:
            raise ValueError("No images provided")
        
        # Get dimensions based on aspect ratio
        width, height = self.aspect_ratios.get(aspect_ratio, (1920, 1080))
        
        # Get bitrate based on quality
        bitrate = self.quality_presets.get(quality, 5000)
        
        # Create clips for each image
        clips = []
        
        for item in image_items:
            # Create the base image clip
            clip = self._create_image_clip(item, width, height)
            clips.append(clip)
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose", padding=0)
        
        # Write the final video file
        final_clip.write_videofile(
            output_path,
            fps=frame_rate,
            codec='libx264',
            bitrate=f"{bitrate}k",
            audio=False,
            threads=4,
            preset='medium'
        )
        
        # Close clips to free memory
        final_clip.close()
        for clip in clips:
            clip.close()
    
    def _create_image_clip(self, image_item, width, height):
        """Create a video clip from an image with transitions and effects"""
        # Load the image
        img_clip = ImageClip(image_item.filepath)
        
        # Resize to fit the aspect ratio while maintaining original aspect ratio
        img_clip = self._resize_clip(img_clip, width, height)
        
        # Set the duration
        img_clip = img_clip.set_duration(image_item.duration)
        
        # Apply effect if specified
        img_clip = self._apply_effect(img_clip, image_item.effect)
        
        # Apply start transition if specified
        if image_item.start_transition != "None":
            img_clip = self._apply_start_transition(
                img_clip, 
                image_item.start_transition, 
                image_item.start_duration
            )
        
        # Apply end transition if specified
        if image_item.end_transition != "None":
            img_clip = self._apply_end_transition(
                img_clip, 
                image_item.end_transition, 
                image_item.end_duration
            )
        
        return img_clip
    
    def _resize_clip(self, clip, width, height):
        """Resize a clip to fit within the specified dimensions while maintaining aspect ratio"""
        # Get the original dimensions
        orig_width, orig_height = clip.size
        
        # Calculate the scaling factor
        width_ratio = width / orig_width
        height_ratio = height / orig_height
        
        # Use the smaller ratio to ensure the image fits within the frame
        scale_factor = min(width_ratio, height_ratio)
        
        # Calculate the new dimensions
        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)
        
        # Resize the clip
        resized_clip = clip.resize((new_width, new_height))
        
        # Create a background clip with the target dimensions
        bg_clip = ColorClip(size=(width, height), color=(0, 0, 0))
        bg_clip = bg_clip.set_duration(clip.duration)
        
        # Position the resized clip in the center of the background
        x_pos = (width - new_width) // 2
        y_pos = (height - new_height) // 2
        
        # Composite the resized clip onto the background
        final_clip = CompositeVideoClip([
            bg_clip,
            resized_clip.set_position((x_pos, y_pos))
        ])
        
        return final_clip
    
    def _apply_start_transition(self, clip, transition_type, duration):
        """Apply a start transition to the clip"""
        if transition_type == "Fade In":
            return clip.fadein(duration)
        elif transition_type == "Slide In Left":
            return transfx.slide_in(clip, duration=duration, side="left")
        elif transition_type == "Slide In Right":
            return transfx.slide_in(clip, duration=duration, side="right")
        elif transition_type == "Slide In Top":
            return transfx.slide_in(clip, duration=duration, side="top")
        elif transition_type == "Slide In Bottom":
            return transfx.slide_in(clip, duration=duration, side="bottom")
        else:
            return clip
    
    def _apply_end_transition(self, clip, transition_type, duration):
        """Apply an end transition to the clip"""
        if transition_type == "Fade Out":
            return clip.fadeout(duration)
        elif transition_type == "Slide Out Left":
            return transfx.slide_out(clip, duration=duration, side="left")
        elif transition_type == "Slide Out Right":
            return transfx.slide_out(clip, duration=duration, side="right")
        elif transition_type == "Slide Out Top":
            return transfx.slide_out(clip, duration=duration, side="top")
        elif transition_type == "Slide Out Bottom":
            return transfx.slide_out(clip, duration=duration, side="bottom")
        else:
            return clip
    
    def _apply_effect(self, clip, effect_type):
        """Apply a special effect to the clip"""
        if effect_type == "Zoom In":
            return clip.fx(vfx.resize, lambda t: 1 + 0.1 * t)
        elif effect_type == "Zoom Out":
            return clip.fx(vfx.resize, lambda t: 1.1 - 0.1 * t)
        elif effect_type == "Pan Left to Right":
            w, h = clip.size
            return clip.fx(vfx.scroll, w, 0)
        elif effect_type == "Pan Right to Left":
            w, h = clip.size
            return clip.fx(vfx.scroll, -w, 0)
        elif effect_type == "Pan Top to Bottom":
            w, h = clip.size
            return clip.fx(vfx.scroll, 0, h)
        elif effect_type == "Pan Bottom to Top":
            w, h = clip.size
            return clip.fx(vfx.scroll, 0, -h)
        elif effect_type == "Sepia":
            return clip.fx(vfx.colorx, 1.5).fx(vfx.lum_contrast, 0, 0.3, 0.6)
        elif effect_type == "Grayscale":
            return clip.fx(vfx.blackwhite)
        elif effect_type == "Blur":
            return clip.fx(vfx.gaussian_blur, 2)
        else:
            return clip 