"""
Main Window for the Slideshow Video Maker application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QComboBox, 
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QScrollArea,
    QListWidgetItem, QCheckBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import random

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
        
        # Default profile settings
        self.default_duration = 3.0
        self.default_start_transition = "Fade In"
        self.default_start_duration = 1.0
        self.default_end_transition = "Fade Out"
        self.default_end_duration = 1.0
        self.default_effect = "Zoom In"
        
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
        self.duration_spin.setValue(self.default_duration)
        self.duration_spin.setSuffix(" seconds")
        self.duration_spin.setEnabled(False)
        self.duration_spin.valueChanged.connect(self.update_image_settings)
        
        # Start transition
        self.start_transition = QComboBox()
        self.start_transition.addItems([
            "None", "Fade In", "Slide In Left", "Slide In Right", "Slide In Top", "Slide In Bottom",
            "Zoom In", "Expand", "Wipe In Left", "Wipe In Right", "Wipe In Top", "Wipe In Bottom",
            "Rotate In"
        ])
        self.start_transition.setCurrentText(self.default_start_transition)
        self.start_transition.setEnabled(False)
        self.start_transition.currentIndexChanged.connect(self.update_image_settings)
        
        # Start transition duration
        self.start_duration = QDoubleSpinBox()
        self.start_duration.setRange(0.1, 5.0)
        self.start_duration.setValue(self.default_start_duration)
        self.start_duration.setSuffix(" seconds")
        self.start_duration.setEnabled(False)
        self.start_duration.valueChanged.connect(self.update_image_settings)
        
        # End transition
        self.end_transition = QComboBox()
        self.end_transition.addItems([
            "None", "Fade Out", "Slide Out Left", "Slide Out Right", "Slide Out Top", "Slide Out Bottom",
            "Zoom Out", "Shrink", "Wipe Out Left", "Wipe Out Right", "Wipe Out Top", "Wipe Out Bottom",
            "Rotate Out"
        ])
        self.end_transition.setCurrentText(self.default_end_transition)
        self.end_transition.setEnabled(False)
        self.end_transition.currentIndexChanged.connect(self.update_image_settings)
        
        # End transition duration
        self.end_duration = QDoubleSpinBox()
        self.end_duration.setRange(0.1, 5.0)
        self.end_duration.setValue(self.default_end_duration)
        self.end_duration.setSuffix(" seconds")
        self.end_duration.setEnabled(False)
        self.end_duration.valueChanged.connect(self.update_image_settings)
        
        # Effect
        self.effect = QComboBox()
        self.effect.addItems([
            "None", "Zoom In", "Zoom Out", "Pan Left to Right", "Pan Right to Left", 
            "Pan Top to Bottom", "Pan Bottom to Top", "Sepia", "Grayscale", "Blur",
            "Brightness Pulse", "Color Boost", "Vignette", "Mirror X", "Mirror Y",
            "Rotate Clockwise", "Rotate Counter-Clockwise"
        ])
        self.effect.setCurrentText(self.default_effect)
        self.effect.setEnabled(False)
        self.effect.currentIndexChanged.connect(self.update_image_settings)
        
        # Overlay effect
        self.overlay_effect = QComboBox()
        self.overlay_effect.addItems([
            "None", "Watermark", "Text Caption", "Border", "Frame", "Gradient Overlay",
            "Light Leak", "Film Grain", "Dust and Scratches", "Vintage"
        ])
        self.overlay_effect.setEnabled(False)
        self.overlay_effect.currentIndexChanged.connect(self.update_image_settings)
        
        image_form.addRow("Duration:", self.duration_spin)
        image_form.addRow("Start Transition:", self.start_transition)
        image_form.addRow("Start Duration:", self.start_duration)
        image_form.addRow("End Transition:", self.end_transition)
        image_form.addRow("End Duration:", self.end_duration)
        image_form.addRow("Effect:", self.effect)
        image_form.addRow("Overlay:", self.overlay_effect)
        
        image_layout.addWidget(self.preview_label)
        image_layout.addLayout(image_form)
        
        # Video settings tab
        video_settings = QWidget()
        video_layout = QVBoxLayout(video_settings)
        
        # Global settings group
        global_group = QGroupBox("Global Settings")
        global_layout = QFormLayout(global_group)
        
        # Aspect ratio
        self.aspect_ratio = QComboBox()
        self.aspect_ratio.addItems(["16:9", "9:16", "4:3"])
        
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
        
        global_layout.addRow("Aspect Ratio:", self.aspect_ratio)
        global_layout.addRow("Frame Rate:", self.frame_rate)
        global_layout.addRow("Transition Overlap:", self.transition_overlap)
        global_layout.addRow("Output Quality:", self.output_quality)
        
        # Global transition and effect settings group
        transition_group = QGroupBox("Global Transition and Effect Settings")
        transition_layout = QVBoxLayout(transition_group)
        
        # Apply settings to all images
        self.apply_to_all_check = QCheckBox("Apply these settings to all images")
        self.apply_to_all_check.setChecked(False)
        
        # Settings mode
        settings_mode_group = QButtonGroup(self)
        settings_mode_layout = QHBoxLayout()
        
        self.manual_mode = QRadioButton("Manual")
        self.manual_mode.setChecked(True)
        settings_mode_group.addButton(self.manual_mode)
        
        self.random_mode = QRadioButton("Random")
        settings_mode_group.addButton(self.random_mode)
        
        self.profile_mode = QRadioButton("Default Profile")
        settings_mode_group.addButton(self.profile_mode)
        
        settings_mode_layout.addWidget(self.manual_mode)
        settings_mode_layout.addWidget(self.random_mode)
        settings_mode_layout.addWidget(self.profile_mode)
        
        # Global settings form
        global_settings_form = QFormLayout()
        
        # Global duration
        self.global_duration = QDoubleSpinBox()
        self.global_duration.setRange(0.5, 30.0)
        self.global_duration.setValue(self.default_duration)
        self.global_duration.setSuffix(" seconds")
        
        # Global start transition
        self.global_start_transition = QComboBox()
        self.global_start_transition.addItems([
            "None", "Fade In", "Slide In Left", "Slide In Right", "Slide In Top", "Slide In Bottom",
            "Zoom In", "Expand", "Wipe In Left", "Wipe In Right", "Wipe In Top", "Wipe In Bottom",
            "Rotate In"
        ])
        self.global_start_transition.setCurrentText(self.default_start_transition)
        
        # Global start transition duration
        self.global_start_duration = QDoubleSpinBox()
        self.global_start_duration.setRange(0.1, 5.0)
        self.global_start_duration.setValue(self.default_start_duration)
        self.global_start_duration.setSuffix(" seconds")
        
        # Global end transition
        self.global_end_transition = QComboBox()
        self.global_end_transition.addItems([
            "None", "Fade Out", "Slide Out Left", "Slide Out Right", "Slide Out Top", "Slide Out Bottom",
            "Zoom Out", "Shrink", "Wipe Out Left", "Wipe Out Right", "Wipe Out Top", "Wipe Out Bottom",
            "Rotate Out"
        ])
        self.global_end_transition.setCurrentText(self.default_end_transition)
        
        # Global end transition duration
        self.global_end_duration = QDoubleSpinBox()
        self.global_end_duration.setRange(0.1, 5.0)
        self.global_end_duration.setValue(self.default_end_duration)
        self.global_end_duration.setSuffix(" seconds")
        
        # Global effect
        self.global_effect = QComboBox()
        self.global_effect.addItems([
            "None", "Zoom In", "Zoom Out", "Pan Left to Right", "Pan Right to Left", 
            "Pan Top to Bottom", "Pan Bottom to Top", "Sepia", "Grayscale", "Blur",
            "Brightness Pulse", "Color Boost", "Vignette", "Mirror X", "Mirror Y",
            "Rotate Clockwise", "Rotate Counter-Clockwise"
        ])
        self.global_effect.setCurrentText(self.default_effect)
        
        # Global overlay effect
        self.global_overlay_effect = QComboBox()
        self.global_overlay_effect.addItems([
            "None", "Watermark", "Text Caption", "Border", "Frame", "Gradient Overlay",
            "Light Leak", "Film Grain", "Dust and Scratches", "Vintage"
        ])
        
        global_settings_form.addRow("Duration:", self.global_duration)
        global_settings_form.addRow("Start Transition:", self.global_start_transition)
        global_settings_form.addRow("Start Duration:", self.global_start_duration)
        global_settings_form.addRow("End Transition:", self.global_end_transition)
        global_settings_form.addRow("End Duration:", self.global_end_duration)
        global_settings_form.addRow("Effect:", self.global_effect)
        global_settings_form.addRow("Overlay:", self.global_overlay_effect)
        
        # Apply global settings button
        self.apply_global_btn = QPushButton("Apply Global Settings")
        self.apply_global_btn.clicked.connect(self.apply_global_settings)
        
        transition_layout.addWidget(self.apply_to_all_check)
        transition_layout.addLayout(settings_mode_layout)
        transition_layout.addLayout(global_settings_form)
        transition_layout.addWidget(self.apply_global_btn)
        
        # Add groups to video settings layout
        video_layout.addWidget(global_group)
        video_layout.addWidget(transition_group)
        video_layout.addStretch()
        
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
        
        # Connect radio buttons to enable/disable appropriate controls
        self.manual_mode.toggled.connect(self.update_settings_mode)
        self.random_mode.toggled.connect(self.update_settings_mode)
        self.profile_mode.toggled.connect(self.update_settings_mode)
    
    def update_settings_mode(self):
        """Update the UI based on the selected settings mode"""
        if self.manual_mode.isChecked():
            # Enable all global settings
            self.global_duration.setEnabled(True)
            self.global_start_transition.setEnabled(True)
            self.global_start_duration.setEnabled(True)
            self.global_end_transition.setEnabled(True)
            self.global_end_duration.setEnabled(True)
            self.global_effect.setEnabled(True)
            self.global_overlay_effect.setEnabled(True)
        elif self.random_mode.isChecked():
            # Disable all global settings as they'll be randomized
            self.global_duration.setEnabled(False)
            self.global_start_transition.setEnabled(False)
            self.global_start_duration.setEnabled(False)
            self.global_end_transition.setEnabled(False)
            self.global_end_duration.setEnabled(False)
            self.global_effect.setEnabled(False)
            self.global_overlay_effect.setEnabled(False)
        elif self.profile_mode.isChecked():
            # Disable all global settings as they'll use default profile
            self.global_duration.setEnabled(False)
            self.global_start_transition.setEnabled(False)
            self.global_start_duration.setEnabled(False)
            self.global_end_transition.setEnabled(False)
            self.global_end_duration.setEnabled(False)
            self.global_effect.setEnabled(False)
            self.global_overlay_effect.setEnabled(False)
            
            # Set the values to match the default profile
            self.global_duration.setValue(self.default_duration)
            self.global_start_transition.setCurrentText(self.default_start_transition)
            self.global_start_duration.setValue(self.default_start_duration)
            self.global_end_transition.setCurrentText(self.default_end_transition)
            self.global_end_duration.setValue(self.default_end_duration)
            self.global_effect.setCurrentText(self.default_effect)
            self.global_overlay_effect.setCurrentText("None")
    
    def apply_global_settings(self):
        """Apply global settings to all images"""
        if not self.image_items:
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self, 
            "Apply Global Settings", 
            "This will override individual settings for all images. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        for image_item in self.image_items:
            if self.random_mode.isChecked():
                # Apply random settings
                image_item.duration = random.uniform(2.0, 5.0)
                image_item.start_transition = random.choice(
                    [item for item in [self.start_transition.itemText(i) for i in range(self.start_transition.count())] if item != "None"]
                )
                image_item.start_duration = random.uniform(0.5, 1.5)
                image_item.end_transition = random.choice(
                    [item for item in [self.end_transition.itemText(i) for i in range(self.end_transition.count())] if item != "None"]
                )
                image_item.end_duration = random.uniform(0.5, 1.5)
                image_item.effect = random.choice(
                    [item for item in [self.effect.itemText(i) for i in range(self.effect.count())] if item != "None"]
                )
                image_item.overlay_effect = random.choice(
                    [self.overlay_effect.itemText(i) for i in range(self.overlay_effect.count())]
                )
            elif self.profile_mode.isChecked():
                # Apply default profile settings
                image_item.duration = self.default_duration
                image_item.start_transition = self.default_start_transition
                image_item.start_duration = self.default_start_duration
                image_item.end_transition = self.default_end_transition
                image_item.end_duration = self.default_end_duration
                image_item.effect = self.default_effect
                image_item.overlay_effect = "None"
            else:
                # Apply manual global settings
                image_item.duration = self.global_duration.value()
                image_item.start_transition = self.global_start_transition.currentText()
                image_item.start_duration = self.global_start_duration.value()
                image_item.end_transition = self.global_end_transition.currentText()
                image_item.end_duration = self.global_end_duration.value()
                image_item.effect = self.global_effect.currentText()
                image_item.overlay_effect = self.global_overlay_effect.currentText()
        
        # Update the UI if an image is selected
        current_row = self.image_list.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            self.on_image_selected(current_row)
        
        QMessageBox.information(self, "Settings Applied", "Global settings have been applied to all images.")
    
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
                
                # Apply global settings if enabled
                if self.apply_to_all_check.isChecked():
                    if self.random_mode.isChecked():
                        # Apply random settings
                        image_item.duration = random.uniform(2.0, 5.0)
                        image_item.start_transition = random.choice(
                            [item for item in [self.start_transition.itemText(i) for i in range(self.start_transition.count())] if item != "None"]
                        )
                        image_item.start_duration = random.uniform(0.5, 1.5)
                        image_item.end_transition = random.choice(
                            [item for item in [self.end_transition.itemText(i) for i in range(self.end_transition.count())] if item != "None"]
                        )
                        image_item.end_duration = random.uniform(0.5, 1.5)
                        image_item.effect = random.choice(
                            [item for item in [self.effect.itemText(i) for i in range(self.effect.count())] if item != "None"]
                        )
                        image_item.overlay_effect = random.choice(
                            [self.overlay_effect.itemText(i) for i in range(self.overlay_effect.count())]
                        )
                    elif self.profile_mode.isChecked():
                        # Apply default profile settings
                        image_item.duration = self.default_duration
                        image_item.start_transition = self.default_start_transition
                        image_item.start_duration = self.default_start_duration
                        image_item.end_transition = self.default_end_transition
                        image_item.end_duration = self.default_end_duration
                        image_item.effect = self.default_effect
                        image_item.overlay_effect = "None"
                    else:
                        # Apply manual global settings
                        image_item.duration = self.global_duration.value()
                        image_item.start_transition = self.global_start_transition.currentText()
                        image_item.start_duration = self.global_start_duration.value()
                        image_item.end_transition = self.global_end_transition.currentText()
                        image_item.end_duration = self.global_end_duration.value()
                        image_item.effect = self.global_effect.currentText()
                        image_item.overlay_effect = self.global_overlay_effect.currentText()
                
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
            
            # Set overlay effect if it exists
            if hasattr(image_item, 'overlay_effect'):
                self.overlay_effect.setCurrentText(image_item.overlay_effect)
            else:
                self.overlay_effect.setCurrentText("None")
                image_item.overlay_effect = "None"
            
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
        self.overlay_effect.setEnabled(True)
    
    def disable_image_controls(self):
        """Disable image settings controls"""
        self.duration_spin.setEnabled(False)
        self.start_transition.setEnabled(False)
        self.start_duration.setEnabled(False)
        self.end_transition.setEnabled(False)
        self.end_duration.setEnabled(False)
        self.effect.setEnabled(False)
        self.overlay_effect.setEnabled(False)
    
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
            image_item.overlay_effect = self.overlay_effect.currentText()
    
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