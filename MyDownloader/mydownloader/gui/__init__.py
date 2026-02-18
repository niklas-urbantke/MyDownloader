"""
GUI Package - User Interface Components

NOTE: This is a modular structure. The actual implementation
would be split into multiple tab files, but for now we use
the monolithic version from app_tkinter_v3.py

To fully modularize, create:
- main_window.py: Main application window
- tabs/download_tab.py: Download tab
- tabs/queue_tab.py: Queue management tab
- tabs/history_tab.py: History tab
- tabs/settings_tab.py: Settings tab
- tabs/about_tab.py: About/Info tab
- widgets/custom_widgets.py: Custom UI widgets
- themes.py: Theme management
"""

# For now, import the complete GUI from the original file
# This can be refactored later into proper modules

__all__ = ['MainWindow']

# Placeholder - in production, this would import from main_window.py
# from .main_window import MainWindow
