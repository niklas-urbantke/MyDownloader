"""
Main Entry Point for MyDownloader Application
"""

import sys
import tkinter as tk
from .utils.logger import setup_logging
from .core.ffmpeg import ffmpeg_manager
from .gui.main_window import MainWindow
from .constants import APP_NAME, APP_VERSION

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Check FFmpeg
    if not ffmpeg_manager.check_availability():
        print("Warning: FFmpeg not available. Some features may not work.")
    
    # Create main window
    root = tk.Tk()
    app = MainWindow(root)
    
    # Start application
    root.mainloop()

if __name__ == '__main__':
    main()
