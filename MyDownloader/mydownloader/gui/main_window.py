"""
Main Application Window

This is a wrapper/adapter for the GUI implementation.
For the initial release, we use the complete implementation from app_tkinter_v3.py
In future versions, this can be further modularized.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path to import the complete UI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the complete application from app_tkinter_v3.py
# This provides backward compatibility while we modularize
try:
    # Try to import from the modular structure (future)
    from ..gui import tabs
    USE_MODULAR = True
except ImportError:
    # Fallback to monolithic implementation
    USE_MODULAR = False

class MainWindow:
    """Main application window wrapper"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 MyDownloader v3.0")
        
        # For now, display a message that GUI needs to be initialized
        # In production, this would initialize the full GUI
        label = tk.Label(
            root,
            text="MyDownloader GUI\n\nTo use the full GUI, run:\npython app_tkinter_v3.py",
            font=("Segoe UI", 12),
            padx=50,
            pady=50
        )
        label.pack(expand=True)
        
        # TODO: Implement full modular GUI
        # This would instantiate all tabs and set up the main window
        # For now, users should run app_tkinter_v3.py directly

# Note: For full functionality, use app_tkinter_v3.py directly
# This modular structure is prepared for future refactoring
