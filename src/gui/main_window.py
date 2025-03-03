"""
Main Window for the Slideshow Video Maker application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QComboBox, 
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QScrollArea,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from src.core.image_item import ImageItem
from src.core.video_generator import VideoGenerator


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Slideshow Video Maker")
        self.setMinimumSize(1000, 700)
        
        self.image_items = []  # List to store ImageItem objects
        self.video_generator = VideoGenerator()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Image list and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.setMinimumWidth(200)
        self.image_list.currentRowChanged.connect(self.on_image_selected)
        
        # Image control buttons
        image_controls = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Images")
        self.add_btn.clicked.connect(self.add_images)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_image)
        self.remove_btn.setEnabled(False)
        
        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.clicked.connect(self.move_image_up)
        self.move_up_btn.setEnabled(False)
        
        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.clicked.connect(self.move_image_down)
        self.move_down_btn.setEnabled(False)
        
        image_controls.addWidget(self.add_btn)
        image_controls.addWidget(self.remove_btn)
        image_controls.addWidget(self.move_up_btn)
        image_controls.addWidget(self.move_down_btn)
        
        left_layout.addWidget(QLabel("<h3>Images</h3>"))
        left_layout.addWidget(self.image_list)
        left_layout.addLayout(image_controls)
        
        # Right panel - Settings and preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Settings tabs
        settings_tabs = QTabWidget()
        
        # Image settings tab
        image_settings = QWidget()
        image_layout = QVBoxLayout(image_settings)
        
        # Preview
        self.preview_label = QLabel("No image selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        
        # Image settings form
        image_form = QFormLayout()
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.5, 30.0)
        self.duration_spin.setValue(3.0)
        self.duration_spin.setSuffix(" seconds")
        self.duration_spin.setEnabled(False)
        self.duration_spin.valueChanged.connect(self.update_image_settings)
        
        # Start transition
        self.start_transition = QComboBox()
        self.start_transition.addItems(["None", "Fade In", "Slide In Left", "Slide In Right", "Slide In Top", "Slide In Bottom"])
        self.start_transition.setEnabled(False)
        self.start_transition.currentIndexChanged.connect(self.update_image_settings)
        
        # Start transition duration
        self.start_duration = QDoubleSpinBox()
        self.start_duration.setRange(0.1, 5.0)
        self.start_duration.setValue(1.0)
        self.start_duration.setSuffix(" seconds")
        self.start_duration.setEnabled(False)
        self.start_duration.valueChanged.connect(self.update_image_settings)
        
        # End transition
        self.end_transition = QComboBox()
        self.end_transition.addItems(["None", "Fade Out", "Slide Out Left", "Slide Out Right", "Slide Out Top", "Slide Out Bottom"])
        self.end_transition.setEnabled(False)
        self.end_transition.currentIndexChanged.connect(self.update_image_settings)
        
        # End transition duration
        self.end_duration = QDoubleSpinBox()
        self.end_duration.setRange(0.1, 5.0)
        self.end_duration.setValue(1.0)
        self.end_duration.setSuffix(" seconds")
        self.end_duration.setEnabled(False)
        self.end_duration.valueChanged.connect(self.update_image_settings)
        
        # Effect
        self.effect = QComboBox()
        self.effect.addItems(["None", "Zoom In", "Zoom Out", "Pan Left to Right", "Pan Right to Left", 
                             "Pan Top to Bottom", "Pan Bottom to Top", "Sepia", "Grayscale", "Blur"])
        self.effect.setEnabled(False)
        self.effect.currentIndexChanged.connect(self.update_image_settings)
        
        image_form.addRow("Duration:", self.duration_spin)
        image_form.addRow("Start Transition:", self.start_transition)
        image_form.addRow("Start Duration:", self.start_duration)
        image_form.addRow("End Transition:", self.end_transition)
        image_form.addRow("End Duration:", self.end_duration)
        image_form.addRow("Effect:", self.effect)
        
        image_layout.addWidget(self.preview_label)
        image_layout.addLayout(image_form)
        
        # Video settings tab
        video_settings = QWidget()
        video_layout = QFormLayout(video_settings)
        
        # Aspect ratio
        self.aspect_ratio = QComboBox()
        self.aspect_ratio.addItems(["16:9", "4:3", "1:1", "9:16", "21:9"])
        
        # Frame rate
        self.frame_rate = QSpinBox()
        self.frame_rate.setRange(15, 60)
        self.frame_rate.setValue(30)
        self.frame_rate.setSuffix(" fps")
        
        # Transition overlap
        self.transition_overlap = QDoubleSpinBox()
        self.transition_overlap.setRange(0.0, 1.0)
        self.transition_overlap.setValue(0.5)
        self.transition_overlap.setSingleStep(0.1)
        self.transition_overlap.setToolTip("0 = No overlap, 1 = Full overlap")
        
        # Output quality
        self.output_quality = QComboBox()
        self.output_quality.addItems(["Low", "Medium", "High", "Very High"])
        self.output_quality.setCurrentIndex(2)  # Default to High
        
        video_layout.addRow("Aspect Ratio:", self.aspect_ratio)
        video_layout.addRow("Frame Rate:", self.frame_rate)
        video_layout.addRow("Transition Overlap:", self.transition_overlap)
        video_layout.addRow("Output Quality:", self.output_quality)
        
        # Add tabs
        settings_tabs.addTab(image_settings, "Image Settings")
        settings_tabs.addTab(video_settings, "Video Settings")
        
        # Generate button
        self.generate_btn = QPushButton("Generate Video")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.clicked.connect(self.generate_video)
        self.generate_btn.setEnabled(False)
        
        right_layout.addWidget(settings_tabs)
        right_layout.addWidget(self.generate_btn)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        self.setCentralWidget(central_widget)
    
    def add_images(self):
        """Open file dialog to add images"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            
            for filename in filenames:
                # Create an ImageItem for each selected image
                image_item = ImageItem(filename)
                self.image_items.append(image_item)
                
                # Add to list widget
                item_name = image_item.get_filename()
                list_item = QListWidgetItem(item_name)
                
                # Create thumbnail
                pixmap = QPixmap(filename)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                    list_item.setIcon(QIcon(pixmap))
                
                self.image_list.addItem(list_item)
            
            # Enable generate button if we have images
            if self.image_items:
                self.generate_btn.setEnabled(True)
    
    def remove_image(self):
        """Remove the selected image from the list"""
        current_row = self.image_list.currentRow()
        if current_row >= 0:
            self.image_list.takeItem(current_row)
            self.image_items.pop(current_row)
            
            # Disable generate button if no images left
            if not self.image_items:
                self.generate_btn.setEnabled(False)
                self.remove_btn.setEnabled(False)
                self.move_up_btn.setEnabled(False)
                self.move_down_btn.setEnabled(False)
                self.preview_label.setText("No image selected")
                self.disable_image_controls()
            else:
                # Select another item if available
                if current_row < self.image_list.count():
                    self.image_list.setCurrentRow(current_row)
                else:
                    self.image_list.setCurrentRow(self.image_list.count() - 1)
    
    def move_image_up(self):
        """Move the selected image up in the list"""
        current_row = self.image_list.currentRow()
        if current_row > 0:
            # Swap items in the model
            self.image_items[current_row], self.image_items[current_row - 1] = \
                self.image_items[current_row - 1], self.image_items[current_row]
            
            # Swap items in the view
            item = self.image_list.takeItem(current_row)
            self.image_list.insertItem(current_row - 1, item)
            self.image_list.setCurrentRow(current_row - 1)
    
    def move_image_down(self):
        """Move the selected image down in the list"""
        current_row = self.image_list.currentRow()
        if current_row < self.image_list.count() - 1:
            # Swap items in the model
            self.image_items[current_row], self.image_items[current_row + 1] = \
                self.image_items[current_row + 1], self.image_items[current_row]
            
            # Swap items in the view
            item = self.image_list.takeItem(current_row)
            self.image_list.insertItem(current_row + 1, item)
            self.image_list.setCurrentRow(current_row + 1)
    
    def on_image_selected(self, row):
        """Handle image selection in the list"""
        if row >= 0 and row < len(self.image_items):
            # Enable controls
            self.remove_btn.setEnabled(True)
            self.move_up_btn.setEnabled(row > 0)
            self.move_down_btn.setEnabled(row < self.image_list.count() - 1)
            
            # Enable image settings controls
            self.enable_image_controls()
            
            # Load image settings
            image_item = self.image_items[row]
            self.duration_spin.setValue(image_item.duration)
            self.start_transition.setCurrentText(image_item.start_transition)
            self.start_duration.setValue(image_item.start_duration)
            self.end_transition.setCurrentText(image_item.end_transition)
            self.end_duration.setValue(image_item.end_duration)
            self.effect.setCurrentText(image_item.effect)
            
            # Update preview
            pixmap = QPixmap(image_item.filepath)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(self.preview_label.width(), self.preview_label.height(), 
                                      Qt.AspectRatioMode.KeepAspectRatio)
                self.preview_label.setPixmap(pixmap)
            else:
                self.preview_label.setText("Cannot load image preview")
        else:
            # Disable controls
            self.remove_btn.setEnabled(False)
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            self.disable_image_controls()
            self.preview_label.setText("No image selected")
    
    def enable_image_controls(self):
        """Enable image settings controls"""
        self.duration_spin.setEnabled(True)
        self.start_transition.setEnabled(True)
        self.start_duration.setEnabled(True)
        self.end_transition.setEnabled(True)
        self.end_duration.setEnabled(True)
        self.effect.setEnabled(True)
    
    def disable_image_controls(self):
        """Disable image settings controls"""
        self.duration_spin.setEnabled(False)
        self.start_transition.setEnabled(False)
        self.start_duration.setEnabled(False)
        self.end_transition.setEnabled(False)
        self.end_duration.setEnabled(False)
        self.effect.setEnabled(False)
    
    def update_image_settings(self):
        """Update the settings for the currently selected image"""
        current_row = self.image_list.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            image_item = self.image_items[current_row]
            
            # Update settings
            image_item.duration = self.duration_spin.value()
            image_item.start_transition = self.start_transition.currentText()
            image_item.start_duration = self.start_duration.value()
            image_item.end_transition = self.end_transition.currentText()
            image_item.end_duration = self.end_duration.value()
            image_item.effect = self.effect.currentText()
    
    def generate_video(self):
        """Generate the video from the images"""
        if not self.image_items:
            QMessageBox.warning(self, "No Images", "Please add at least one image before generating a video.")
            return
        
        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Video", "", "Video Files (*.mp4)"
        )
        
        if not output_path:
            return  # User cancelled
        
        if not output_path.lower().endswith('.mp4'):
            output_path += '.mp4'
        
        # Get video settings
        aspect_ratio = self.aspect_ratio.currentText()
        frame_rate = self.frame_rate.value()
        transition_overlap = self.transition_overlap.value()
        quality = self.output_quality.currentText()
        
        try:
            # Show progress message
            QMessageBox.information(self, "Processing", 
                                   "Video generation has started. This may take a while depending on the number of images and effects.")
            
            # Generate the video
            self.video_generator.generate_video(
                self.image_items,
                output_path,
                aspect_ratio,
                frame_rate,
                transition_overlap,
                quality
            )
            
            # Show success message
            QMessageBox.information(self, "Success", f"Video successfully generated and saved to:\n{output_path}")
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(self, "Error", f"An error occurred while generating the video:\n{str(e)}") 