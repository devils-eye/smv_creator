"""
VideoGenerator class for creating videos from images with transitions and effects
"""

import os
import sys
import traceback
import numpy as np
from moviepy.editor import (
    ImageClip, CompositeVideoClip, concatenate_videoclips, 
    ColorClip, vfx, transfx, TextClip
)
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageFont
import random
import math

# Set the default font
DEFAULT_FONT = 'DejaVuSans'


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
            "9:16": (1080, 1920),
            "4:3": (1440, 1080)
        }
        
        # Debug mode
        self.debug = True
    
    def log(self, message):
        """Print debug message if debug mode is enabled"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def generate_video(self, image_items, output_path, aspect_ratio="16:9", 
                      frame_rate=30, transition_overlap=0.5, quality="High"):
        """Generate a video from the provided image items"""
        if not image_items:
            raise ValueError("No images provided")
        
        self.log(f"Starting video generation with {len(image_items)} images")
        self.log(f"Aspect ratio: {aspect_ratio}, Frame rate: {frame_rate}, Quality: {quality}")
        
        # Get dimensions based on aspect ratio
        width, height = self.aspect_ratios.get(aspect_ratio, (1920, 1080))
        self.log(f"Video dimensions: {width}x{height}")
        
        # Get bitrate based on quality
        bitrate = self.quality_presets.get(quality, 5000)
        
        # Create clips for each image
        clips = []
        
        try:
            for i, item in enumerate(image_items):
                self.log(f"Processing image {i+1}/{len(image_items)}: {item.filepath}")
                
                # Create the base image clip
                try:
                    clip = self._create_image_clip(item, width, height)
                    self.log(f"  - Created clip with size: {clip.size}, duration: {clip.duration}s")
                    
                    # Store clip information for debugging
                    if hasattr(clip, 'size'):
                        self.log(f"  - Clip size: {clip.size}")
                    else:
                        self.log(f"  - Warning: Clip has no size attribute")
                    
                    clips.append(clip)
                except Exception as e:
                    self.log(f"  - ERROR creating clip: {str(e)}")
                    self.log(traceback.format_exc())
                    raise Exception(f"Error processing image {i+1}: {str(e)}")
            
            self.log(f"All clips created, concatenating {len(clips)} clips")
            
            # Print information about all clips for debugging
            for i, clip in enumerate(clips):
                self.log(f"Clip {i+1} info: size={clip.size}, duration={clip.duration}s")
            
            # Concatenate all clips
            try:
                self.log("Attempting to concatenate clips...")
                final_clip = concatenate_videoclips(clips, method="compose", padding=0)
                self.log(f"Concatenation successful, final duration: {final_clip.duration}s")
            except Exception as e:
                self.log(f"ERROR during concatenation: {str(e)}")
                self.log(traceback.format_exc())
                
                # Check if clips have different sizes
                sizes = [clip.size for clip in clips]
                if len(set(sizes)) > 1:
                    self.log(f"ERROR: Clips have different sizes: {sizes}")
                
                raise Exception(f"Error concatenating clips: {str(e)}")
            
            # Write the final video file
            try:
                self.log(f"Writing video to {output_path}")
                final_clip.write_videofile(
                    output_path,
                    fps=frame_rate,
                    codec='libx264',
                    bitrate=f"{bitrate}k",
                    audio=False,
                    threads=4,
                    preset='medium',
                    logger=None  # Disable moviepy's logger
                )
                self.log("Video successfully written")
            except Exception as e:
                self.log(f"ERROR writing video: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error writing video: {str(e)}")
            
            # Close clips to free memory
            self.log("Cleaning up clips")
            final_clip.close()
            for clip in clips:
                clip.close()
                
        except Exception as e:
            self.log(f"ERROR in generate_video: {str(e)}")
            self.log(traceback.format_exc())
            
            # Clean up in case of error
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass
            raise Exception(f"Error generating video: {str(e)}")
    
    def _create_image_clip(self, image_item, width, height):
        """Create a video clip from an image with transitions and effects"""
        temp_path = None
        
        try:
            self.log(f"Loading image: {image_item.filepath}")
            
            # Check if file exists
            if not os.path.exists(image_item.filepath):
                raise FileNotFoundError(f"Image file not found: {image_item.filepath}")
            
            # Load the image using PIL first to ensure it's valid
            try:
                pil_img = Image.open(image_item.filepath)
                self.log(f"  - Original image size: {pil_img.size}, mode: {pil_img.mode}")
                
                # Convert to RGB to ensure consistent format
                if pil_img.mode != 'RGB':
                    self.log(f"  - Converting image from {pil_img.mode} to RGB")
                    pil_img = pil_img.convert('RGB')
                
                # Save to a temporary file to avoid format issues
                temp_path = f"/tmp/temp_img_{os.path.basename(image_item.filepath)}"
                pil_img.save(temp_path, format='JPEG', quality=95)
                self.log(f"  - Saved temporary image to {temp_path}")
            except Exception as e:
                self.log(f"  - ERROR processing image with PIL: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error processing image with PIL: {str(e)}")
            
            # Load the image with MoviePy
            try:
                img_clip = ImageClip(temp_path)
                self.log(f"  - MoviePy loaded image with size: {img_clip.size}")
            except Exception as e:
                self.log(f"  - ERROR loading image with MoviePy: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error loading image with MoviePy: {str(e)}")
            
            # Resize to fit the aspect ratio while maintaining original aspect ratio
            try:
                self.log("  - Resizing clip to fit aspect ratio")
                img_clip = self._resize_clip(img_clip, width, height)
                self.log(f"  - Resized clip size: {img_clip.size}")
            except Exception as e:
                self.log(f"  - ERROR resizing clip: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error resizing clip: {str(e)}")
            
            # Set the duration
            img_clip = img_clip.set_duration(image_item.duration)
            self.log(f"  - Set clip duration: {img_clip.duration}s")
            
            # Apply effect if specified
            if image_item.effect != "None":
                try:
                    self.log(f"  - Applying effect: {image_item.effect}")
                    img_clip = self._apply_effect(img_clip, image_item.effect)
                except Exception as e:
                    self.log(f"  - ERROR applying effect: {str(e)}")
                    self.log(traceback.format_exc())
                    # Continue without the effect
                    self.log("  - Continuing without effect")
            
            # Apply overlay effect if specified
            if hasattr(image_item, 'overlay_effect') and image_item.overlay_effect != "None":
                try:
                    self.log(f"  - Applying overlay effect: {image_item.overlay_effect}")
                    # Check if overlay_text attribute exists, use empty string if not
                    overlay_text = getattr(image_item, 'overlay_text', '')
                    self.log(f"  - Overlay text: {overlay_text}")
                    img_clip = self._apply_overlay_effect(img_clip, image_item.overlay_effect, overlay_text)
                except Exception as e:
                    self.log(f"  - ERROR applying overlay effect: {str(e)}")
                    self.log(traceback.format_exc())
                    # Continue without the overlay
                    self.log("  - Continuing without overlay effect")
            
            # Apply start transition if specified
            if image_item.start_transition != "None":
                try:
                    self.log(f"  - Applying start transition: {image_item.start_transition} ({image_item.start_duration}s)")
                    img_clip = self._apply_start_transition(
                        img_clip, 
                        image_item.start_transition, 
                        image_item.start_duration
                    )
                except Exception as e:
                    self.log(f"  - ERROR applying start transition: {str(e)}")
                    self.log(traceback.format_exc())
                    # Continue without the transition
                    self.log("  - Continuing without start transition")
            
            # Apply end transition if specified
            if image_item.end_transition != "None":
                try:
                    self.log(f"  - Applying end transition: {image_item.end_transition} ({image_item.end_duration}s)")
                    img_clip = self._apply_end_transition(
                        img_clip, 
                        image_item.end_transition, 
                        image_item.end_duration
                    )
                except Exception as e:
                    self.log(f"  - ERROR applying end transition: {str(e)}")
                    self.log(traceback.format_exc())
                    # Continue without the transition
                    self.log("  - Continuing without end transition")
            
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    self.log(f"  - Removed temporary file: {temp_path}")
                except Exception as e:
                    self.log(f"  - WARNING: Could not remove temporary file: {str(e)}")
            
            self.log("  - Image clip creation completed successfully")
            return img_clip
            
        except Exception as e:
            self.log(f"ERROR in _create_image_clip: {str(e)}")
            self.log(traceback.format_exc())
            
            # Clean up temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            raise Exception(f"Error processing image: {str(e)}")
    
    def _resize_clip(self, clip, width, height):
        """Resize a clip to fit within the specified dimensions while maintaining aspect ratio"""
        try:
            # Get the original dimensions
            orig_width, orig_height = clip.size
            self.log(f"  - Original clip size: {orig_width}x{orig_height}")
            
            # Calculate the scaling factor
            width_ratio = width / orig_width
            height_ratio = height / orig_height
            self.log(f"  - Width ratio: {width_ratio:.4f}, Height ratio: {height_ratio:.4f}")
            
            # Use the smaller ratio to ensure the image fits within the frame
            scale_factor = min(width_ratio, height_ratio)
            self.log(f"  - Using scale factor: {scale_factor:.4f}")
            
            # Calculate the new dimensions
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            self.log(f"  - New dimensions after scaling: {new_width}x{new_height}")
            
            # Resize the clip
            try:
                resized_clip = clip.resize((new_width, new_height))
                self.log(f"  - Resized clip size: {resized_clip.size}")
            except Exception as e:
                self.log(f"  - ERROR during resize operation: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error during resize operation: {str(e)}")
            
            # Create a background clip with the target dimensions
            try:
                self.log(f"  - Creating background clip with size: {width}x{height}")
                bg_clip = ColorClip(size=(width, height), color=(0, 0, 0))
                bg_clip = bg_clip.set_duration(clip.duration)
            except Exception as e:
                self.log(f"  - ERROR creating background clip: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error creating background clip: {str(e)}")
            
            # Position the resized clip in the center of the background
            x_pos = (width - new_width) // 2
            y_pos = (height - new_height) // 2
            self.log(f"  - Positioning resized clip at ({x_pos}, {y_pos})")
            
            # Composite the resized clip onto the background
            try:
                self.log("  - Creating composite clip")
                final_clip = CompositeVideoClip([
                    bg_clip,
                    resized_clip.set_position((x_pos, y_pos))
                ])
                self.log(f"  - Final composite clip size: {final_clip.size}")
                return final_clip
            except Exception as e:
                self.log(f"  - ERROR creating composite clip: {str(e)}")
                self.log(traceback.format_exc())
                raise Exception(f"Error creating composite clip: {str(e)}")
                
        except Exception as e:
            self.log(f"ERROR in _resize_clip: {str(e)}")
            self.log(traceback.format_exc())
            raise Exception(f"Error resizing clip: {str(e)}")
    
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
        elif transition_type == "Zoom In":
            # Create a zoom in effect from small to normal size
            return clip.fx(
                vfx.resize, 
                lambda t: min(1, t/duration) if t < duration else 1
            )
        elif transition_type == "Expand":
            # Create an expand effect from center
            w, h = clip.size
            return clip.fx(
                lambda c: c.resize(
                    lambda t: (
                        max(0.01, min(1, t/duration)) if t < duration else 1,
                        max(0.01, min(1, t/duration)) if t < duration else 1
                    )
                ).set_position(('center', 'center'))
            )
        elif transition_type == "Wipe In Left":
            # Create a wipe effect from left to right
            w, h = clip.size
            def make_frame(t):
                if t < duration:
                    progress = min(1, t/duration)
                    mask_width = int(w * progress)
                    mask = np.zeros((h, w))
                    mask[:, :mask_width] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe In Right":
            # Create a wipe effect from right to left
            w, h = clip.size
            def make_frame(t):
                if t < duration:
                    progress = min(1, t/duration)
                    mask_width = int(w * progress)
                    mask = np.zeros((h, w))
                    mask[:, w-mask_width:] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe In Top":
            # Create a wipe effect from top to bottom
            w, h = clip.size
            def make_frame(t):
                if t < duration:
                    progress = min(1, t/duration)
                    mask_height = int(h * progress)
                    mask = np.zeros((h, w))
                    mask[:mask_height, :] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe In Bottom":
            # Create a wipe effect from bottom to top
            w, h = clip.size
            def make_frame(t):
                if t < duration:
                    progress = min(1, t/duration)
                    mask_height = int(h * progress)
                    mask = np.zeros((h, w))
                    mask[h-mask_height:, :] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Rotate In":
            # Create a rotation effect
            return clip.fx(
                vfx.rotate,
                lambda t: 360 * (1 - min(1, t/duration)) if t < duration else 0
            )
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
        elif transition_type == "Zoom Out":
            # Create a zoom out effect from normal to small size
            clip_duration = clip.duration
            return clip.fx(
                vfx.resize, 
                lambda t: min(1, (clip_duration - t) / duration) if t > clip_duration - duration else 1
            )
        elif transition_type == "Shrink":
            # Create a shrink effect to center
            clip_duration = clip.duration
            w, h = clip.size
            return clip.fx(
                lambda c: c.resize(
                    lambda t: (
                        max(0.01, min(1, (clip_duration - t) / duration)) if t > clip_duration - duration else 1,
                        max(0.01, min(1, (clip_duration - t) / duration)) if t > clip_duration - duration else 1
                    )
                ).set_position(('center', 'center'))
            )
        elif transition_type == "Wipe Out Left":
            # Create a wipe effect from right to left
            w, h = clip.size
            clip_duration = clip.duration
            def make_frame(t):
                if t > clip_duration - duration:
                    progress = min(1, (clip_duration - t) / duration)
                    mask_width = int(w * progress)
                    mask = np.zeros((h, w))
                    mask[:, :mask_width] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe Out Right":
            # Create a wipe effect from left to right
            w, h = clip.size
            clip_duration = clip.duration
            def make_frame(t):
                if t > clip_duration - duration:
                    progress = min(1, (clip_duration - t) / duration)
                    mask_width = int(w * progress)
                    mask = np.zeros((h, w))
                    mask[:, w-mask_width:] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe Out Top":
            # Create a wipe effect from bottom to top
            w, h = clip.size
            clip_duration = clip.duration
            def make_frame(t):
                if t > clip_duration - duration:
                    progress = min(1, (clip_duration - t) / duration)
                    mask_height = int(h * progress)
                    mask = np.zeros((h, w))
                    mask[:mask_height, :] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Wipe Out Bottom":
            # Create a wipe effect from top to bottom
            w, h = clip.size
            clip_duration = clip.duration
            def make_frame(t):
                if t > clip_duration - duration:
                    progress = min(1, (clip_duration - t) / duration)
                    mask_height = int(h * progress)
                    mask = np.zeros((h, w))
                    mask[h-mask_height:, :] = 255
                    return mask
                else:
                    return np.ones((h, w)) * 255
            
            mask_clip = ImageClip(make_frame, ismask=True, duration=clip.duration)
            return clip.set_mask(mask_clip)
        elif transition_type == "Rotate Out":
            # Create a rotation effect
            clip_duration = clip.duration
            return clip.fx(
                vfx.rotate,
                lambda t: 360 * min(1, (t - (clip_duration - duration)) / duration) if t > clip_duration - duration else 0
            )
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
        elif effect_type == "Brightness Pulse":
            # Create a pulsing brightness effect
            return clip.fx(
                vfx.colorx, 
                lambda t: 1 + 0.3 * np.sin(2 * np.pi * t)
            )
        elif effect_type == "Color Boost":
            # Enhance color saturation
            return clip.fx(vfx.colorx, 1.5)
        elif effect_type == "Vignette":
            # Add a vignette effect (darker corners)
            w, h = clip.size
            
            def vignette_filter(image):
                img = Image.fromarray(image)
                # Create a radial gradient mask
                mask = Image.new('L', (w, h), 0)
                draw = ImageDraw.Draw(mask)
                
                # Draw a radial gradient
                for i in range(min(w, h) // 2, 0, -1):
                    alpha = int(255 * (i / (min(w, h) // 2)))
                    draw.ellipse(
                        [(w//2 - i, h//2 - i), (w//2 + i, h//2 + i)],
                        fill=alpha
                    )
                
                # Apply the mask
                img = ImageEnhance.Brightness(img).enhance(0.8)
                img.putalpha(mask)
                
                return np.array(img)
            
            return clip.fl_image(vignette_filter)
        elif effect_type == "Mirror X":
            # Mirror the image horizontally
            return clip.fx(vfx.mirror_x)
        elif effect_type == "Mirror Y":
            # Mirror the image vertically
            return clip.fx(vfx.mirror_y)
        elif effect_type == "Rotate Clockwise":
            # Slowly rotate the image clockwise
            return clip.fx(
                vfx.rotate,
                lambda t: 15 * t
            )
        elif effect_type == "Rotate Counter-Clockwise":
            # Slowly rotate the image counter-clockwise
            return clip.fx(
                vfx.rotate,
                lambda t: -15 * t
            )
        else:
            return clip
    
    def _apply_overlay_effect(self, clip, overlay_type, overlay_text=None):
        """Apply an overlay effect to a clip"""
        try:
            self.log(f"Applying overlay effect: {overlay_type}")
            
            if overlay_type == "None" or not overlay_type:
                self.log("No overlay effect selected, returning original clip")
                return clip
            
            clip_width, clip_height = clip.size
            self.log(f"Clip dimensions for overlay: {clip_width}x{clip_height}")
            
            # List of all supported overlay types for easy checking
            supported_overlays = [
                "Watermark", "Text Caption", "Border", "Frame", 
                "Vintage", "Dust and Scratches", "Film Grain", 
                "Sepia Tone", "Black and White", "Film Noir"
            ]
            
            if overlay_type not in supported_overlays:
                self.log(f"Unsupported overlay type: {overlay_type}, returning original clip")
                return clip
                
            if overlay_type == "Watermark":
                try:
                    self.log("Applying watermark overlay")
                    # Create a semi-transparent rectangle in the bottom right corner
                    watermark_text = overlay_text or "Watermark"
                    self.log(f"Watermark text: {watermark_text}")
                    
                    def add_watermark(image):
                        try:
                            img = Image.fromarray(image)
                            draw = ImageDraw.Draw(img)
                            
                            # Try to load a font, fall back to default if not available
                            try:
                                font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"
                                if not os.path.exists(font_path):
                                    font_path = "/home/ranjith/.conda/envs/business_apps/fonts/DejaVuSans.ttf"
                                    if not os.path.exists(font_path):
                                        self.log(f"Warning: Could not find font at {font_path}, using default")
                                        font = None
                                    else:
                                        self.log(f"Using font from conda env: {font_path}")
                                        font = ImageFont.truetype(font_path, 20)
                                else:
                                    self.log(f"Using system font: {font_path}")
                                    font = ImageFont.truetype(font_path, 20)
                            except Exception as e:
                                self.log(f"Error loading font: {str(e)}")
                                font = None
                            
                            # Get text size
                            text_width = 150  # Default if font measurement fails
                            text_height = 30
                            if font:
                                try:
                                    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                                    text_width = text_bbox[2] - text_bbox[0] + 20  # Add padding
                                    text_height = text_bbox[3] - text_bbox[1] + 10  # Add padding
                                    self.log(f"Calculated text size: {text_width}x{text_height}")
                                except Exception as e:
                                    self.log(f"Error calculating text size: {str(e)}")
                            
                            # Draw semi-transparent background
                            rect_x = img.width - text_width - 10
                            rect_y = img.height - text_height - 10
                            self.log(f"Drawing watermark rectangle at ({rect_x}, {rect_y}) with size {text_width}x{text_height}")
                            
                            # Create a semi-transparent overlay
                            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                            overlay_draw = ImageDraw.Draw(overlay)
                            overlay_draw.rectangle(
                                [(rect_x, rect_y), (rect_x + text_width, rect_y + text_height)],
                                fill=(0, 0, 0, 128)
                            )
                            
                            # Draw text
                            text_x = rect_x + 10
                            text_y = rect_y + 5
                            if font:
                                overlay_draw.text((text_x, text_y), watermark_text, font=font, fill=(255, 255, 255, 255))
                            else:
                                overlay_draw.text((text_x, text_y), watermark_text, fill=(255, 255, 255, 255))
                            
                            # Convert image to RGBA if it's not already
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Composite the overlay onto the image
                            img = Image.alpha_composite(img, overlay)
                            
                            # Convert back to RGB for MoviePy
                            return np.array(img.convert('RGB'))
                        except Exception as e:
                            self.log(f"Error in add_watermark function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_watermark)
                except Exception as e:
                    self.log(f"Error applying watermark: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
                
            elif overlay_type == "Text Caption":
                try:
                    self.log("Applying text caption overlay")
                    caption_text = overlay_text or "Caption"
                    self.log(f"Caption text: {caption_text}")
                    
                    def add_caption(image):
                        try:
                            img = Image.fromarray(image)
                            draw = ImageDraw.Draw(img)
                            
                            # Try to load a font, fall back to default if not available
                            try:
                                font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"
                                if not os.path.exists(font_path):
                                    font_path = "/home/ranjith/.conda/envs/business_apps/fonts/DejaVuSans.ttf"
                                    if not os.path.exists(font_path):
                                        self.log(f"Warning: Could not find font at {font_path}, using default")
                                        font = None
                                    else:
                                        self.log(f"Using font from conda env: {font_path}")
                                        font = ImageFont.truetype(font_path, 24)
                                else:
                                    self.log(f"Using system font: {font_path}")
                                    font = ImageFont.truetype(font_path, 24)
                            except Exception as e:
                                self.log(f"Error loading font: {str(e)}")
                                font = None
                            
                            # Create a semi-transparent overlay for the bottom of the image
                            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                            overlay_draw = ImageDraw.Draw(overlay)
                            
                            # Draw semi-transparent background at the bottom
                            caption_height = 50
                            overlay_draw.rectangle(
                                [(0, img.height - caption_height), (img.width, img.height)],
                                fill=(0, 0, 0, 160)
                            )
                            
                            # Draw text
                            text_y = img.height - caption_height + 10
                            if font:
                                # Try to center the text
                                try:
                                    text_bbox = draw.textbbox((0, 0), caption_text, font=font)
                                    text_width = text_bbox[2] - text_bbox[0]
                                    text_x = (img.width - text_width) // 2
                                    self.log(f"Positioning caption text at ({text_x}, {text_y})")
                                    overlay_draw.text((text_x, text_y), caption_text, font=font, fill=(255, 255, 255, 255))
                                except Exception as e:
                                    self.log(f"Error centering text: {str(e)}")
                                    overlay_draw.text((10, text_y), caption_text, font=font, fill=(255, 255, 255, 255))
                            else:
                                overlay_draw.text((10, text_y), caption_text, fill=(255, 255, 255, 255))
                            
                            # Convert image to RGBA if it's not already
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Composite the overlay onto the image
                            img = Image.alpha_composite(img, overlay)
                            
                            # Convert back to RGB for MoviePy
                            return np.array(img.convert('RGB'))
                        except Exception as e:
                            self.log(f"Error in add_caption function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_caption)
                except Exception as e:
                    self.log(f"Error applying text caption: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
                
            elif overlay_type == "Border":
                try:
                    self.log("Applying border overlay")
                    
                    def add_border(image):
                        try:
                            img = Image.fromarray(image)
                            
                            # Create a new image with a white border
                            border_width = 20
                            self.log(f"Adding border with width: {border_width}")
                            
                            bordered_img = ImageOps.expand(img, border=border_width, fill='white')
                            
                            # Resize back to original dimensions
                            bordered_img = bordered_img.resize((img.width, img.height))
                            
                            return np.array(bordered_img)
                        except Exception as e:
                            self.log(f"Error in add_border function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_border)
                except Exception as e:
                    self.log(f"Error applying border: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
                
            elif overlay_type == "Frame":
                try:
                    self.log("Applying frame overlay")
                    
                    def add_frame(image):
                        try:
                            img = Image.fromarray(image)
                            
                            # Create a new image with a decorative frame
                            frame_width = 30
                            self.log(f"Adding frame with width: {frame_width}")
                            
                            # Create a new image with a black background
                            framed_img = Image.new('RGB', img.size, (0, 0, 0))
                            
                            # Calculate the inner rectangle
                            inner_width = img.width - 2 * frame_width
                            inner_height = img.height - 2 * frame_width
                            
                            # Resize the original image to fit inside the frame
                            inner_img = img.resize((inner_width, inner_height))
                            
                            # Paste the resized image onto the frame
                            framed_img.paste(inner_img, (frame_width, frame_width))
                            
                            return np.array(framed_img)
                        except Exception as e:
                            self.log(f"Error in add_frame function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_frame)
                except Exception as e:
                    self.log(f"Error applying frame: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
                
            elif overlay_type == "Vintage":
                try:
                    self.log("Applying vintage overlay effect")
                    
                    def add_vintage_effect(image):
                        try:
                            img = Image.fromarray(image)
                            
                            # Split the image into RGB channels
                            r, g, b = img.split()
                            
                            # Enhance red channel
                            r = ImageEnhance.Contrast(r).enhance(1.1)
                            r = ImageEnhance.Brightness(r).enhance(1.1)
                            
                            # Reduce blue channel
                            b = ImageEnhance.Contrast(b).enhance(0.9)
                            b = ImageEnhance.Brightness(b).enhance(0.8)
                            
                            # Adjust green channel
                            g = ImageEnhance.Contrast(g).enhance(1.0)
                            g = ImageEnhance.Brightness(g).enhance(0.9)
                            
                            # Merge channels back
                            img = Image.merge('RGB', (r, g, b))
                            
                            # Add slight sepia tone
                            img = ImageEnhance.Color(img).enhance(0.8)
                            
                            # Add vignette
                            width, height = img.size
                            mask = Image.new('L', (width, height), 0)
                            draw = ImageDraw.Draw(mask)
                            
                            # Draw a radial gradient for vignette
                            for i in range(min(width, height) // 2, 0, -1):
                                alpha = int(255 * (i / (min(width, height) // 2)))
                                draw.ellipse(
                                    [(width//2 - i, height//2 - i), (width//2 + i, height//2 + i)],
                                    fill=alpha
                                )
                            
                            # Apply the vignette
                            img = img.filter(ImageFilter.SMOOTH)
                            
                            # Create a black background
                            black_bg = Image.new('RGB', img.size, (0, 0, 0))
                            
                            # Use the mask to blend the image with the black background
                            img = Image.composite(img, black_bg, mask)
                            
                            # Add film grain
                            grain = np.random.normal(0, 10, (height, width, 3)).astype(np.uint8)
                            grain_img = Image.fromarray(grain)
                            
                            # Blend grain with the image (subtle effect)
                            img = Image.blend(img, grain_img, 0.05)
                            
                            return np.array(img)
                        except Exception as e:
                            self.log(f"Error in add_vintage_effect function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_vintage_effect)
                except Exception as e:
                    self.log(f"Error applying vintage effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            elif overlay_type == "Dust and Scratches":
                try:
                    self.log("Applying dust and scratches overlay effect")
                    
                    def add_dust_and_scratches(image):
                        try:
                            img = Image.fromarray(image)
                            width, height = img.size
                            self.log(f"  - Processing dust and scratches effect for image size {width}x{height}")
                            
                            # Create a new transparent layer for dust and scratches
                            dust_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                            draw = ImageDraw.Draw(dust_layer)
                            
                            # Add random dust particles
                            num_dust_particles = int(width * height * 0.0005)  # 0.05% of pixels
                            self.log(f"  - Adding {num_dust_particles} dust particles")
                            
                            for _ in range(num_dust_particles):
                                x = random.randint(0, width - 1)
                                y = random.randint(0, height - 1)
                                size = random.randint(1, 3)
                                opacity = random.randint(100, 200)
                                draw.ellipse([(x, y), (x + size, y + size)], fill=(255, 255, 255, opacity))
                            
                            # Add random scratches
                            num_scratches = random.randint(5, 15)
                            self.log(f"  - Adding {num_scratches} scratches")
                            
                            for _ in range(num_scratches):
                                # Determine scratch start and end points
                                start_x = random.randint(0, width - 1)
                                start_y = random.randint(0, height - 1)
                                
                                # Scratches are mostly horizontal with some angle
                                angle = random.uniform(-0.2, 0.2)
                                length = random.randint(width // 10, width // 3)
                                
                                end_x = min(width - 1, int(start_x + length * math.cos(angle)))
                                end_y = min(height - 1, int(start_y + length * math.sin(angle)))
                                
                                # Draw the scratch with varying opacity
                                opacity = random.randint(100, 200)
                                draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 255, 255, opacity), width=1)
                            
                            # Convert original image to RGBA if needed
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Composite the dust layer onto the image
                            result = Image.alpha_composite(img, dust_layer)
                            
                            # Convert back to RGB for MoviePy
                            result = result.convert('RGB')
                            
                            # Add slight contrast to make it look more aged
                            result = ImageEnhance.Contrast(result).enhance(1.05)
                            
                            self.log("  - Dust and scratches effect applied successfully")
                            return np.array(result)
                        except Exception as e:
                            self.log(f"Error in add_dust_and_scratches function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    self.log("Applying dust and scratches effect to clip")
                    return clip.fl_image(add_dust_and_scratches)
                except Exception as e:
                    self.log(f"Error applying dust and scratches effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            elif overlay_type == "Film Grain":
                try:
                    self.log("Applying film grain overlay effect")
                    
                    def add_film_grain(image):
                        try:
                            img = Image.fromarray(image)
                            width, height = img.size
                            self.log(f"  - Processing film grain effect for image size {width}x{height}")
                            
                            # Create noise using numpy
                            grain_intensity = 20  # Adjust for more/less visible grain
                            grain = np.random.normal(0, grain_intensity, (height, width, 3)).astype(np.uint8)
                            grain_img = Image.fromarray(grain, mode='RGB')
                            
                            # Blend the grain with the original image
                            blend_factor = 0.15  # Adjust for stronger/weaker effect
                            self.log(f"  - Blending grain with factor {blend_factor}")
                            result = Image.blend(img, grain_img, blend_factor)
                            
                            # Add slight contrast enhancement
                            result = ImageEnhance.Contrast(result).enhance(1.1)
                            
                            self.log("  - Film grain effect applied successfully")
                            return np.array(result)
                        except Exception as e:
                            self.log(f"Error in add_film_grain function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    self.log("Applying film grain effect to clip")
                    return clip.fl_image(add_film_grain)
                except Exception as e:
                    self.log(f"Error applying film grain effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            elif overlay_type == "Sepia Tone":
                try:
                    self.log("Applying sepia tone overlay effect")
                    
                    def add_sepia_tone(image):
                        try:
                            img = Image.fromarray(image)
                            
                            # Convert to grayscale first
                            gray_img = img.convert('L')
                            
                            # Apply sepia tone
                            sepia_img = Image.merge('RGB', [
                                ImageEnhance.Brightness(gray_img).enhance(1.1),  # Red channel
                                ImageEnhance.Brightness(gray_img).enhance(0.9),  # Green channel
                                ImageEnhance.Brightness(gray_img).enhance(0.7)   # Blue channel
                            ])
                            
                            # Enhance contrast slightly
                            sepia_img = ImageEnhance.Contrast(sepia_img).enhance(1.1)
                            
                            return np.array(sepia_img)
                        except Exception as e:
                            self.log(f"Error in add_sepia_tone function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_sepia_tone)
                except Exception as e:
                    self.log(f"Error applying sepia tone effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            elif overlay_type == "Black and White":
                try:
                    self.log("Applying black and white overlay effect")
                    
                    def add_black_and_white(image):
                        try:
                            img = Image.fromarray(image)
                            
                            # Convert to grayscale with enhanced contrast
                            bw_img = img.convert('L')
                            bw_img = ImageEnhance.Contrast(bw_img).enhance(1.2)
                            
                            # Convert back to RGB for MoviePy
                            bw_img = bw_img.convert('RGB')
                            
                            return np.array(bw_img)
                        except Exception as e:
                            self.log(f"Error in add_black_and_white function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_black_and_white)
                except Exception as e:
                    self.log(f"Error applying black and white effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            elif overlay_type == "Film Noir":
                try:
                    self.log("Applying film noir overlay effect")
                    
                    def add_film_noir(image):
                        try:
                            img = Image.fromarray(image)
                            width, height = img.size
                            
                            # Convert to high contrast black and white
                            noir_img = img.convert('L')
                            noir_img = ImageEnhance.Contrast(noir_img).enhance(1.5)
                            noir_img = ImageEnhance.Brightness(noir_img).enhance(0.9)
                            
                            # Add strong vignette effect
                            mask = Image.new('L', (width, height), 0)
                            draw = ImageDraw.Draw(mask)
                            
                            # Draw a radial gradient for vignette (stronger than vintage)
                            for i in range(min(width, height) // 2, 0, -1):
                                # More aggressive falloff for film noir look
                                alpha = int(255 * (i / (min(width, height) // 2)) ** 1.5)
                                draw.ellipse(
                                    [(width//2 - i, height//2 - i), (width//2 + i, height//2 + i)],
                                    fill=alpha
                                )
                            
                            # Apply the vignette
                            noir_img = noir_img.filter(ImageFilter.SMOOTH)
                            
                            # Create a black background
                            black_bg = Image.new('L', img.size, 0)
                            
                            # Use the mask to blend the image with the black background
                            noir_img = Image.composite(noir_img, black_bg, mask)
                            
                            # Add film grain
                            grain = np.random.normal(0, 15, (height, width)).astype(np.uint8)
                            grain_img = Image.fromarray(grain, mode='L')
                            
                            # Blend grain with the image
                            noir_img = Image.blend(noir_img, grain_img, 0.1)
                            
                            # Convert back to RGB for MoviePy
                            noir_img = noir_img.convert('RGB')
                            
                            return np.array(noir_img)
                        except Exception as e:
                            self.log(f"Error in add_film_noir function: {str(e)}")
                            self.log(traceback.format_exc())
                            return image
                    
                    return clip.fl_image(add_film_noir)
                except Exception as e:
                    self.log(f"Error applying film noir effect: {str(e)}")
                    self.log(traceback.format_exc())
                    return clip
            
            else:
                self.log(f"Unsupported overlay type: {overlay_type}, returning original clip")
                return clip
                
        except Exception as e:
            self.log(f"ERROR in _apply_overlay_effect: {str(e)}")
            self.log(traceback.format_exc())
            print(f"Warning: Error applying overlay effect: {str(e)}")
            return clip 