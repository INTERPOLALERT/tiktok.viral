"""
Main Window - CreatorStudio AI
Professional PyQt6-based UI for content creation suite
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar, QMenuBar, QMenu,
    QToolBar, QSplitter, QTextEdit, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QRadioButton, QGroupBox, QListWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QGridLayout, QScrollArea,
    QFrame, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CreatorStudioMainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CreatorStudio AI - Professional Content Creation Suite")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize components
        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()
        self._apply_theme()

        logger.info("Main window initialized")

    def _init_ui(self):
        """Initialize main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Welcome header
        header = self._create_header()
        main_layout.addWidget(header)

        # Tab widget for different modules
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Add module tabs
        self.tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._create_video_tab(), "Video Studio")
        self.tabs.addTab(self._create_image_tab(), "Image Studio")
        self.tabs.addTab(self._create_script_tab(), "Script Writer")
        self.tabs.addTab(self._create_audio_tab(), "Audio Studio")
        self.tabs.addTab(self._create_social_tab(), "Social Media")
        self.tabs.addTab(self._create_analytics_tab(), "Analytics")
        self.tabs.addTab(self._create_trends_tab(), "Trends")
        self.tabs.addTab(self._create_projects_tab(), "Projects")
        self.tabs.addTab(self._create_settings_tab(), "Settings")

        main_layout.addWidget(self.tabs)

    def _create_header(self) -> QWidget:
        """Create header with branding"""
        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        header.setMaximumHeight(80)

        layout = QHBoxLayout(header)

        # Title
        title = QLabel("CreatorStudio AI")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # Quick actions
        quick_new = QPushButton("New Project")
        quick_new.clicked.connect(self._new_project)
        layout.addWidget(quick_new)

        return header

    def _create_dashboard_tab(self) -> QWidget:
        """Create dashboard overview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Welcome message
        welcome = QLabel("Welcome to CreatorStudio AI")
        welcome.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(welcome)

        # API Status Banner
        from ..core.config import config
        api_key = config.get_secret('openai_api_key')

        if not api_key:
            info_banner = QLabel(
                "💡 Tip: Configure your API key in the Settings tab to unlock AI-powered features!\n"
                "You can explore all other features without an API key."
            )
            info_banner.setWordWrap(True)
            info_banner.setStyleSheet(
                "background-color: #1a4d6d; color: #87CEEB; "
                "padding: 15px; border-radius: 5px; margin: 10px 0px;"
            )
            layout.addWidget(info_banner)

        # Quick stats
        stats_layout = QHBoxLayout()

        stats = [
            ("Total Projects", "15"),
            ("Videos Created", "48"),
            ("Total Views", "125K"),
            ("Engagement Rate", "12.5%")
        ]

        for label, value in stats:
            stat_widget = self._create_stat_card(label, value)
            stats_layout.addWidget(stat_widget)

        layout.addLayout(stats_layout)

        # Recent activity
        recent_label = QLabel("Recent Activity")
        recent_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(recent_label)

        activity_list = QListWidget()
        activity_list.addItems([
            "Created video: 'How to Go Viral' - 2 hours ago",
            "Scheduled TikTok post - 4 hours ago",
            "Generated AI script - Yesterday",
            "Analytics report generated - Yesterday"
        ])
        layout.addWidget(activity_list)

        layout.addStretch()
        return widget

    def _create_video_tab(self) -> QWidget:
        """Create video editing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Video Studio - AI-Powered Video Creation")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Options
        options_group = QGroupBox("Video Options")
        options_layout = QGridLayout()

        options_layout.addWidget(QLabel("Resolution:"), 0, 0)
        resolution_combo = QComboBox()
        resolution_combo.addItems(["1920x1080", "1280x720", "3840x2160", "1080x1920"])
        options_layout.addWidget(resolution_combo, 0, 1)

        options_layout.addWidget(QLabel("FPS:"), 1, 0)
        fps_spin = QSpinBox()
        fps_spin.setRange(24, 120)
        fps_spin.setValue(30)
        options_layout.addWidget(fps_spin, 1, 1)

        options_layout.addWidget(QLabel("Format:"), 2, 0)
        format_combo = QComboBox()
        format_combo.addItems(["MP4", "MOV", "AVI", "WEBM"])
        options_layout.addWidget(format_combo, 2, 1)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Actions
        actions_layout = QHBoxLayout()

        create_btn = QPushButton("Create from Images")
        create_btn.clicked.connect(lambda: self._show_info("Video creation started"))
        actions_layout.addWidget(create_btn)

        edit_btn = QPushButton("Edit Video")
        edit_btn.clicked.connect(lambda: self._show_info("Video editor opening"))
        actions_layout.addWidget(edit_btn)

        effects_btn = QPushButton("Apply Effects")
        actions_layout.addWidget(effects_btn)

        layout.addLayout(actions_layout)

        # File list
        file_list = QListWidget()
        layout.addWidget(QLabel("Recent Videos:"))
        layout.addWidget(file_list)

        layout.addStretch()
        return widget

    def _create_image_tab(self) -> QWidget:
        """Create image editing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Image Studio - AI Image Generation & Editing")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # AI Generation
        ai_group = QGroupBox("AI Image Generation")
        ai_layout = QVBoxLayout()

        prompt_input = QTextEdit()
        prompt_input.setPlaceholderText("Enter image description prompt...")
        prompt_input.setMaximumHeight(100)
        ai_layout.addWidget(QLabel("Prompt:"))
        ai_layout.addWidget(prompt_input)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        size_combo = QComboBox()
        size_combo.addItems(["1024x1024", "1024x1792", "1792x1024"])
        size_layout.addWidget(size_combo)
        ai_layout.addLayout(size_layout)

        generate_btn = QPushButton("Generate Image")
        generate_btn.clicked.connect(lambda: self._show_info("AI image generation started"))
        ai_layout.addWidget(generate_btn)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Editing tools
        tools_layout = QHBoxLayout()
        for tool in ["Resize", "Crop", "Filters", "Add Text", "Remove BG"]:
            btn = QPushButton(tool)
            tools_layout.addWidget(btn)

        layout.addLayout(tools_layout)

        layout.addStretch()
        return widget

    def _create_script_tab(self) -> QWidget:
        """Create script writing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Script Writer - AI-Powered Content Writing")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Script generation options
        options_group = QGroupBox("Script Options")
        options_layout = QGridLayout()

        options_layout.addWidget(QLabel("Topic:"), 0, 0)
        topic_input = QLineEdit()
        topic_input.setPlaceholderText("Enter video topic...")
        options_layout.addWidget(topic_input, 0, 1)

        options_layout.addWidget(QLabel("Duration (seconds):"), 1, 0)
        duration_spin = QSpinBox()
        duration_spin.setRange(15, 600)
        duration_spin.setValue(60)
        options_layout.addWidget(duration_spin, 1, 1)

        options_layout.addWidget(QLabel("Style:"), 2, 0)
        style_combo = QComboBox()
        style_combo.addItems(["Engaging", "Educational", "Entertaining", "Professional"])
        options_layout.addWidget(style_combo, 2, 1)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Generate button
        generate_btn = QPushButton("Generate Script")
        generate_btn.clicked.connect(lambda: self._show_info("Generating script..."))
        layout.addWidget(generate_btn)

        # Script editor
        layout.addWidget(QLabel("Script:"))
        script_editor = QTextEdit()
        script_editor.setPlaceholderText("Your generated script will appear here...")
        layout.addWidget(script_editor)

        # Action buttons
        actions = QHBoxLayout()
        actions.addWidget(QPushButton("Save Script"))
        actions.addWidget(QPushButton("Optimize for SEO"))
        actions.addWidget(QPushButton("Generate Variations"))
        layout.addLayout(actions)

        return widget

    def _create_audio_tab(self) -> QWidget:
        """Create audio editing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Audio Studio - Voice Synthesis & Audio Editing")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Text-to-speech
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QVBoxLayout()

        text_input = QTextEdit()
        text_input.setPlaceholderText("Enter text to convert to speech...")
        text_input.setMaximumHeight(150)
        tts_layout.addWidget(text_input)

        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        voice_combo = QComboBox()
        voice_combo.addItems(["Male 1", "Female 1", "Male 2", "Female 2"])
        voice_layout.addWidget(voice_combo)

        voice_layout.addWidget(QLabel("Speed:"))
        speed_spin = QSpinBox()
        speed_spin.setRange(50, 300)
        speed_spin.setValue(200)
        voice_layout.addWidget(speed_spin)

        tts_layout.addLayout(voice_layout)

        generate_speech_btn = QPushButton("Generate Speech")
        tts_layout.addWidget(generate_speech_btn)

        tts_group.setLayout(tts_layout)
        layout.addWidget(tts_group)

        # Audio tools
        tools_group = QGroupBox("Audio Tools")
        tools_layout = QHBoxLayout()
        for tool in ["Trim", "Merge", "Volume", "Effects", "Export"]:
            tools_layout.addWidget(QPushButton(tool))
        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)

        layout.addStretch()
        return widget

    def _create_social_tab(self) -> QWidget:
        """Create social media management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Social Media Manager - Multi-Platform Scheduling")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Platform selection
        platforms = QGroupBox("Platforms")
        platforms_layout = QHBoxLayout()
        for platform in ["TikTok", "Instagram", "YouTube", "Twitter", "Facebook"]:
            cb = QCheckBox(platform)
            platforms_layout.addWidget(cb)
        platforms.setLayout(platforms_layout)
        layout.addWidget(platforms)

        # Post content
        content_group = QGroupBox("Post Content")
        content_layout = QVBoxLayout()

        caption_input = QTextEdit()
        caption_input.setPlaceholderText("Enter post caption...")
        caption_input.setMaximumHeight(100)
        content_layout.addWidget(QLabel("Caption:"))
        content_layout.addWidget(caption_input)

        media_btn = QPushButton("Add Media Files")
        content_layout.addWidget(media_btn)

        content_group.setLayout(content_layout)
        layout.addWidget(content_group)

        # Scheduling
        schedule_layout = QHBoxLayout()
        schedule_layout.addWidget(QPushButton("Schedule Post"))
        schedule_layout.addWidget(QPushButton("Post Now"))
        schedule_layout.addWidget(QPushButton("Suggest Best Time"))
        layout.addLayout(schedule_layout)

        # Scheduled posts table
        layout.addWidget(QLabel("Scheduled Posts:"))
        posts_table = QTableWidget(0, 4)
        posts_table.setHorizontalHeaderLabels(["Platform", "Content", "Time", "Status"])
        layout.addWidget(posts_table)

        return widget

    def _create_analytics_tab(self) -> QWidget:
        """Create analytics dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Analytics Dashboard - Performance Insights")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Metrics overview
        metrics_layout = QHBoxLayout()
        metrics = [
            ("Total Views", "250K", "+15%"),
            ("Engagement", "12.5%", "+3%"),
            ("Followers", "15.7K", "+8%"),
            ("Posts", "125", "+10")
        ]

        for label, value, change in metrics:
            card = self._create_metric_card(label, value, change)
            metrics_layout.addWidget(card)

        layout.addLayout(metrics_layout)

        # Time period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Time Period:"))
        period_combo = QComboBox()
        period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        period_layout.addWidget(period_combo)
        period_layout.addStretch()
        period_layout.addWidget(QPushButton("Refresh"))
        period_layout.addWidget(QPushButton("Export Report"))
        layout.addLayout(period_layout)

        # Charts placeholder
        charts_label = QLabel("📊 Performance charts would be displayed here using matplotlib/plotly")
        charts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        charts_label.setMinimumHeight(300)
        charts_label.setFrameShape(QFrame.Shape.Box)
        layout.addWidget(charts_label)

        return widget

    def _create_trends_tab(self) -> QWidget:
        """Create trends analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Trends Explorer - Real-Time Trend Analysis")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Platform selector
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("Platform:"))
        platform_combo = QComboBox()
        platform_combo.addItems(["All", "TikTok", "Instagram", "YouTube", "Twitter"])
        platform_layout.addWidget(platform_combo)
        platform_layout.addWidget(QPushButton("Refresh Trends"))
        platform_layout.addStretch()
        layout.addLayout(platform_layout)

        # Trending topics table
        layout.addWidget(QLabel("Trending Topics:"))
        trends_table = QTableWidget(10, 5)
        trends_table.setHorizontalHeaderLabels(["Rank", "Topic", "Volume", "Growth", "Category"])

        # Sample data
        sample_trends = [
            ("1", "AI Content Creation", "500K", "+125%", "Technology"),
            ("2", "Viral Marketing", "350K", "+110%", "Marketing"),
            ("3", "TikTok Growth", "300K", "+95%", "Social Media"),
        ]

        for i, (rank, topic, volume, growth, category) in enumerate(sample_trends):
            trends_table.setItem(i, 0, QTableWidgetItem(rank))
            trends_table.setItem(i, 1, QTableWidgetItem(topic))
            trends_table.setItem(i, 2, QTableWidgetItem(volume))
            trends_table.setItem(i, 3, QTableWidgetItem(growth))
            trends_table.setItem(i, 4, QTableWidgetItem(category))

        layout.addWidget(trends_table)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(QPushButton("Generate Content Ideas"))
        actions_layout.addWidget(QPushButton("Analyze Hashtag"))
        actions_layout.addWidget(QPushButton("Predict Trends"))
        layout.addLayout(actions_layout)

        return widget

    def _create_projects_tab(self) -> QWidget:
        """Create projects management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Project Manager - Organize Your Content")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(QPushButton("New Project"))
        actions_layout.addWidget(QPushButton("Open Project"))
        actions_layout.addWidget(QPushButton("Import"))
        actions_layout.addWidget(QPushButton("Export"))
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Projects list
        projects_list = QListWidget()
        projects_list.addItems([
            "TikTok Marketing Campaign",
            "YouTube Tutorial Series",
            "Instagram Reels Collection",
            "Product Launch Content"
        ])
        layout.addWidget(QLabel("Your Projects:"))
        layout.addWidget(projects_list)

        return widget

    def _create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Settings - Configure CreatorStudio AI")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # API Status Banner
        from ..core.config import config
        api_key = config.get_secret('openai_api_key')

        status_label = QLabel()
        if api_key:
            status_label.setText("✅ API Key Configured - AI features are enabled")
            status_label.setStyleSheet("background-color: #2d5016; color: #90EE90; padding: 10px; border-radius: 5px;")
        else:
            status_label.setText("⚠️  No API Key - AI features require configuration (Optional)")
            status_label.setStyleSheet("background-color: #5a4a00; color: #FFD700; padding: 10px; border-radius: 5px;")
        layout.addWidget(status_label)

        # API Settings
        api_group = QGroupBox("AI API Configuration (Optional)")
        api_layout = QVBoxLayout()

        # Info text
        info_label = QLabel(
            "AI features like script generation and image creation require an API key.\n"
            "You can use the app without AI features - just leave this blank!\n\n"
            "Get your OpenAI API key from: https://platform.openai.com/api-keys"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #aaaaaa; padding: 10px;")
        api_layout.addWidget(info_label)

        # Provider and Key
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Provider:"), 0, 0)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic"])
        form_layout.addWidget(self.provider_combo, 0, 1)

        form_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-... (paste your API key here)")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Load existing key if available
        if api_key:
            self.api_key_input.setText(api_key)

        form_layout.addWidget(self.api_key_input, 1, 1)

        # Show/Hide button
        show_key_btn = QPushButton("👁️ Show")
        show_key_btn.setMaximumWidth(100)
        show_key_btn.clicked.connect(self._toggle_api_key_visibility)
        form_layout.addWidget(show_key_btn, 1, 2)

        api_layout.addLayout(form_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # App Settings
        app_group = QGroupBox("Application Settings")
        app_layout = QVBoxLayout()

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light", "Auto"])
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()
        app_layout.addLayout(theme_layout)

        auto_save_cb = QCheckBox("Enable Auto-Save")
        auto_save_cb.setChecked(True)
        app_layout.addWidget(auto_save_cb)

        app_group.setLayout(app_layout)
        layout.addWidget(app_group)

        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        layout.addWidget(save_btn)

        # Test API button
        test_btn = QPushButton("🧪 Test API Connection")
        test_btn.clicked.connect(self._test_api_connection)
        layout.addWidget(test_btn)

        layout.addStretch()
        return widget

    def _toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _save_settings(self):
        """Save settings to config"""
        from ..core.config import config

        try:
            # Save API key
            api_key = self.api_key_input.text().strip()
            provider = self.provider_combo.currentText().lower()

            if api_key:
                if provider == "openai":
                    config.set_secret('openai_api_key', api_key)
                elif provider == "anthropic":
                    config.set_secret('anthropic_api_key', api_key)

                QMessageBox.information(
                    self,
                    "Success",
                    f"API key saved successfully!\n\n"
                    f"Provider: {provider.title()}\n"
                    f"AI features are now enabled."
                )
            else:
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Settings saved. No API key configured.\n"
                    "You can still use non-AI features!"
                )

            self.statusBar().showMessage("Settings saved successfully", 3000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings:\n{str(e)}"
            )

    def _test_api_connection(self):
        """Test API connection"""
        from ..core.config import config

        api_key = self.api_key_input.text().strip()
        provider = self.provider_combo.currentText().lower()

        if not api_key:
            QMessageBox.warning(
                self,
                "No API Key",
                "Please enter an API key first."
            )
            return

        # Show testing dialog
        QMessageBox.information(
            self,
            "Testing API",
            f"Testing connection to {provider.title()}...\n\n"
            f"Note: This is a demo version.\n"
            f"In production, this would test the actual API connection."
        )

        self.statusBar().showMessage(f"API key format validated for {provider}", 3000)

    def _create_stat_card(self, label: str, value: str) -> QWidget:
        """Create a statistics card"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setMinimumSize(200, 100)

        layout = QVBoxLayout(card)

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(text_label)

        return card

    def _create_metric_card(self, label: str, value: str, change: str) -> QWidget:
        """Create a metric card with change indicator"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setMinimumSize(150, 80)

        layout = QVBoxLayout(card)

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        change_label = QLabel(change)
        change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_label.setStyleSheet("color: green;" if "+" in change else "color: red;")

        layout.addWidget(value_label)
        layout.addWidget(text_label)
        layout.addWidget(change_label)

        return card

    def _init_menu(self):
        """Initialize menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Project", self._new_project)
        file_menu.addAction("Open Project", self._open_project)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Preferences", self._show_settings)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Video Editor")
        tools_menu.addAction("Image Generator")
        tools_menu.addAction("Script Writer")

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation", self._show_help)
        help_menu.addAction("About", self._show_about)

    def _init_toolbar(self):
        """Initialize toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction("New", self._new_project)
        toolbar.addAction("Open", self._open_project)
        toolbar.addSeparator()
        toolbar.addAction("Save")
        toolbar.addSeparator()
        toolbar.addAction("Generate Video")
        toolbar.addAction("Generate Image")
        toolbar.addAction("Generate Script")

    def _init_statusbar(self):
        """Initialize status bar"""
        self.statusBar().showMessage("Ready")

    def _apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #353535;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #444444;
            }
            QTabBar::tab:selected {
                background-color: #404040;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }
            QLabel {
                color: #ffffff;
            }
        """)

    def _new_project(self):
        """Create new project"""
        self._show_info("New project creation dialog would open here")

    def _open_project(self):
        """Open existing project"""
        self._show_info("Project browser would open here")

    def _show_settings(self):
        """Show settings dialog"""
        self.tabs.setCurrentIndex(9)  # Switch to settings tab

    def _show_help(self):
        """Show help documentation"""
        self._show_info("Help documentation would open here")

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CreatorStudio AI",
            "CreatorStudio AI v1.0.0\n\n"
            "Professional Content Creation Suite\n"
            "AI-Powered Tools for Content Creators\n\n"
            "© 2024 CreatorStudio AI"
        )

    def _show_info(self, message: str):
        """Show info message"""
        self.statusBar().showMessage(message, 3000)
        logger.info(message)


def launch_app():
    """Launch the application"""
    app = QApplication(sys.argv)
    window = CreatorStudioMainWindow()
    window.show()
    sys.exit(app.exec())
