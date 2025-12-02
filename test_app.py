#!/usr/bin/env python3
"""
Test script to verify PyQt5 works before running main app
"""
import sys
import os
import platform

# Set environment variables before importing Qt
if platform.system() == "Darwin":
    os.environ.setdefault('QT_MAC_WANTS_LAYER', '1')
    os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import Qt
    
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("BeePlan Test")
    
    print("Creating window...")
    window = QMainWindow()
    window.setWindowTitle("BeePlan Test Window")
    window.setGeometry(100, 100, 400, 300)
    
    label = QLabel("If you see this, PyQt5 is working!", window)
    label.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(label)
    
    print("Showing window...")
    window.show()
    
    print("✅ Test successful! Window should be visible.")
    print("Close the window to exit.")
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


