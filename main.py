#!/usr/bin/env python3
"""
BeePlan - Course Scheduling Application
A Python-based GUI application for generating conflict-free course schedules
"""
import sys
import os
from typing import List, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QHeaderView, QMessageBox,
                             QFileDialog, QTextEdit, QDialog)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

# Backend modules
from scheduler import Scheduler
from data_manager import DataManager
from report_generator import ReportGenerator

# ==========================================
# BÖLÜM 2: GUI (KULLANICI ARAYÜZÜ)
# PDF Referans: Implementation & Layout [Cite: 17, 19, 21, 22]
# ==========================================

class BeePlanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BeePlan - Course Scheduler")
        self.setGeometry(100, 100, 1400, 900)  # Larger window for better visibility
        
        # Backend components
        self.scheduler: Optional[Scheduler] = None
        self.report_generator: Optional[ReportGenerator] = None
        self.courses = []
        self.rooms = []
        self.instructors = []
        
        # Ana Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Üst Başlık
        self.header_label = QLabel("Department Course Schedule")
        self.header_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        self.layout.addWidget(self.header_label)
        
        # Legend for color coding
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Legend: ")
        legend_label.setFont(QFont("Arial", 9))
        legend_layout.addWidget(legend_label)
        
        # Theory course color indicator
        theory_indicator = QLabel("Theory")
        theory_indicator.setStyleSheet("background-color: #f0f8ff; color: #00008b; padding: 5px 10px; border-radius: 3px;")
        theory_indicator.setFont(QFont("Arial", 9))
        legend_layout.addWidget(theory_indicator)
        
        # Lab course color indicator
        lab_indicator = QLabel("Lab")
        lab_indicator.setStyleSheet("background-color: #f0fff0; color: #006400; padding: 5px 10px; border-radius: 3px;")
        lab_indicator.setFont(QFont("Arial", 9))
        legend_layout.addWidget(lab_indicator)
        
        # Conflict color indicator
        conflict_indicator = QLabel("Conflict")
        conflict_indicator.setStyleSheet("background-color: #ffc8c8; color: #8b0000; padding: 5px 10px; border-radius: 3px;")
        conflict_indicator.setFont(QFont("Arial", 9))
        legend_layout.addWidget(conflict_indicator)
        
        legend_layout.addStretch()  # Push legend to left
        self.layout.addLayout(legend_layout)

        # Tablo (Weekly Timetable View) [Cite: 19]
        self.schedule_table = QTableWidget()
        self.setup_table()
        self.layout.addWidget(self.schedule_table)

        # Kontrol Butonları Alanı
        self.button_layout = QHBoxLayout()
        
        # Load Data Button
        self.btn_load = QPushButton("Load Data")
        self.btn_load.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        self.btn_load.clicked.connect(self.handle_load_data)
        
        # Generate Schedule Butonu [Cite: 21]
        self.btn_generate = QPushButton("Generate Schedule")
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_generate.clicked.connect(self.handle_generate)
        
        # View Report Butonu [Cite: 22]
        self.btn_report = QPushButton("View Report")
        self.btn_report.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.btn_report.clicked.connect(self.handle_report)

        # Export Schedule Button
        self.btn_export = QPushButton("Export Schedule")
        self.btn_export.setStyleSheet("background-color: #9C27B0; color: white; padding: 10px;")
        self.btn_export.clicked.connect(self.handle_export_schedule)
        
        # Import Schedule Button
        self.btn_import = QPushButton("Import Schedule")
        self.btn_import.setStyleSheet("background-color: #607D8B; color: white; padding: 10px;")
        self.btn_import.clicked.connect(self.handle_import_schedule)

        self.button_layout.addWidget(self.btn_load)
        self.button_layout.addWidget(self.btn_generate)
        self.button_layout.addWidget(self.btn_report)
        self.button_layout.addWidget(self.btn_export)
        self.button_layout.addWidget(self.btn_import)
        self.layout.addLayout(self.button_layout)
        
        # Load sample data on startup
        self.load_sample_data()

    def setup_table(self):
        """Haftalık Ders Programı Tablosunu Oluşturur"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = [
            "08:30 - 09:20", "09:30 - 10:20", "10:30 - 11:20", "11:30 - 12:20",
            "13:20 - 14:10", "14:20 - 15:10", "15:20 - 16:10", "16:20 - 17:10"
        ]
        
        self.schedule_table.setRowCount(len(time_slots))
        self.schedule_table.setColumnCount(len(days))
        
        self.schedule_table.setHorizontalHeaderLabels(days)
        self.schedule_table.setVerticalHeaderLabels(time_slots)
        
        # Tablo ayarları: Hücreleri ekrana yay
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Set row height for better readability
        self.schedule_table.verticalHeader().setDefaultSectionSize(100)
        
        # Enable word wrap for better text display
        self.schedule_table.setWordWrap(True)
        
        # Cuma günü Sınav Bloğunu İşaretle (Kural: 13:20-15:10 Friday) [Cite: 24]
        # 13:20 (Index 4) ve 14:20 (Index 5), Cuma (Sütun 4)
        self.mark_exam_block(4, 4)
        self.mark_exam_block(5, 4)

    def mark_exam_block(self, row, col):
        """Cuma öğleden sonrasını 'Exam Block' olarak işaretler"""
        item = QTableWidgetItem("EXAM BLOCK")
        item.setBackground(QColor(200, 200, 200)) # Gri renk
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(Qt.ItemIsEnabled) # Düzenlemeyi engelle
        self.schedule_table.setItem(row, col, item)

    def load_sample_data(self):
        """Load sample data for testing"""
        try:
            data_manager = DataManager()
            # Try to load from sample_data.json first, fallback to create_sample_data
            json_path = os.path.join(os.path.dirname(__file__), "sample_data.json")
            if os.path.exists(json_path):
                data = data_manager.load_from_json(json_path)
            else:
                # Fallback to generated sample data
                data = data_manager.create_sample_data()
            
            self.courses = data_manager.parse_courses(data)
            self.rooms = data_manager.parse_rooms(data)
            self.instructors = data_manager.parse_instructors(data)
            
            # Initialize scheduler
            self.scheduler = Scheduler(self.courses, self.rooms, self.instructors)
            self.report_generator = ReportGenerator(self.scheduler)
            
            QMessageBox.information(self, "Data Loaded", 
                                  f"Loaded {len(self.courses)} course sessions, "
                                  f"{len(self.rooms)} rooms, "
                                  f"{len(self.instructors)} instructors")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load sample data: {str(e)}")
    
    def handle_load_data(self):
        """Load data from JSON or CSV file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Data", "", "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            data_manager = DataManager()
            
            if filepath.endswith('.json'):
                data = data_manager.load_from_json(filepath)
            else:
                # For CSV, you would need to implement CSV parsing
                QMessageBox.warning(self, "Not Implemented", "CSV loading not fully implemented. Using JSON.")
                return
            
            self.courses = data_manager.parse_courses(data)
            self.rooms = data_manager.parse_rooms(data)
            self.instructors = data_manager.parse_instructors(data)
            
            # Initialize scheduler
            self.scheduler = Scheduler(self.courses, self.rooms, self.instructors)
            self.report_generator = ReportGenerator(self.scheduler)
            
            QMessageBox.information(self, "Data Loaded", 
                                  f"Loaded {len(self.courses)} courses, "
                                  f"{len(self.rooms)} rooms, "
                                  f"{len(self.instructors)} instructors")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def handle_generate(self):
        """Generate schedule using backend algorithm"""
        if not self.scheduler:
            QMessageBox.warning(self, "No Data", "Please load data first.")
            return
        
        # Clear previous schedule
        self.clear_schedule_table()
        
        # Generate schedule
        success = self.scheduler.generate_schedule()
        
        # Display schedule in table
        self.display_schedule()
        
        # Show result message
        if success:
            QMessageBox.information(self, "Schedule Generated", 
                                  "Schedule generated successfully!\nNo conflicts detected.")
        else:
            conflicts = self.scheduler.get_conflicts()
            QMessageBox.warning(self, "Schedule Generated with Conflicts", 
                              f"Schedule generated but {len(conflicts)} conflict(s) detected.\n"
                              "Click 'View Report' for details.")

    def handle_report(self):
        """Display validation report [Cite: 13]"""
        if not self.report_generator:
            QMessageBox.warning(self, "No Schedule", "Please generate a schedule first.")
            return
        
        # Create report dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Validation Report")
        dialog.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(dialog)
        
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setFont(QFont("Courier", 10))
        report_text.setText(self.report_generator.generate_report())
        
        layout.addWidget(report_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def handle_export_schedule(self):
        """Export current schedule to JSON or CSV file"""
        if not self.scheduler:
            QMessageBox.warning(self, "No Schedule", "Please generate a schedule first.")
            return
        
        # Ask user to choose file format
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Export Schedule", 
            "", 
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            data_manager = DataManager()
            
            if selected_filter.startswith("JSON") or filepath.endswith('.json'):
                if not filepath.endswith('.json'):
                    filepath += '.json'
                data_manager.export_schedule_to_json(self.scheduler, filepath)
                QMessageBox.information(self, "Export Successful", 
                                      f"Schedule exported to:\n{filepath}")
            elif selected_filter.startswith("CSV") or filepath.endswith('.csv'):
                if not filepath.endswith('.csv'):
                    filepath += '.csv'
                data_manager.export_schedule_to_csv(self.scheduler, filepath)
                QMessageBox.information(self, "Export Successful", 
                                      f"Schedule exported to:\n{filepath}")
            else:
                QMessageBox.warning(self, "Invalid Format", "Please choose JSON or CSV format.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export schedule:\n{str(e)}")
    
    def handle_import_schedule(self):
        """Import schedule from JSON file"""
        if not self.scheduler:
            QMessageBox.warning(self, "No Scheduler", "Please load data and initialize scheduler first.")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Schedule", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            data_manager = DataManager()
            schedule_data = data_manager.load_from_json(filepath)
            
            # Validate schedule data structure
            if 'schedule' not in schedule_data:
                raise ValueError("Invalid schedule file format")
            
            # Clear current schedule
            for day in self.scheduler.days:
                for time_slot in self.scheduler.time_slots:
                    slot = self.scheduler.schedule[day][time_slot]
                    if slot.course:
                        slot.course = None
                        slot.room = None
                        slot.has_conflict = False
            
            # Import schedule from JSON
            imported_count = 0
            for day in schedule_data.get('schedule', {}):
                if day not in self.scheduler.days:
                    continue
                for time_slot, slot_data in schedule_data['schedule'][day].items():
                    if time_slot not in self.scheduler.time_slots:
                        continue
                    if slot_data is None:
                        continue
                    
                    # Find course by code
                    course_code = slot_data.get('course_code')
                    course = None
                    for c in self.courses:
                        if c.code == course_code:
                            course = c
                            break
                    
                    if not course:
                        continue
                    
                    # Find room by ID
                    room_id = slot_data.get('room_id')
                    room = None
                    if room_id:
                        for r in self.rooms:
                            if r.id == room_id:
                                room = r
                                break
                    
                    # Place course in schedule
                    slot = self.scheduler.schedule[day][time_slot]
                    slot.course = course
                    slot.room = room
                    slot.has_conflict = slot_data.get('has_conflict', False)
                    imported_count += 1
            
            # Refresh display
            self.display_schedule()
            
            QMessageBox.information(self, "Import Successful", 
                                  f"Imported {imported_count} course sessions from:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import schedule:\n{str(e)}")
    
    def clear_schedule_table(self):
        """Clear all course entries from table (keep exam blocks)"""
        for row in range(self.schedule_table.rowCount()):
            for col in range(self.schedule_table.columnCount()):
                item = self.schedule_table.item(row, col)
                # Don't clear exam blocks (Friday 13:20-15:10)
                if item and item.text() == "EXAM BLOCK":
                    continue
                self.schedule_table.setItem(row, col, None)
    
    def display_schedule(self):
        """Display schedule from scheduler in the table"""
        if not self.scheduler:
            return
        
        schedule_grid = self.scheduler.get_schedule_grid()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for row_idx, row in enumerate(schedule_grid):
            for col_idx, cell in enumerate(row):
                if cell:
                    course = cell['course']
                    room = cell['room']
                    instructor = cell.get('instructor', 'N/A')
                    has_conflict = cell['has_conflict']
                    
                    # Format text with better layout
                    # Course code and name
                    text = f"📚 {course.code}\n{course.name}"
                    
                    # Room information
                    if room:
                        room_type = "🔬 LAB" if room.is_lab else "🏫 Room"
                        text += f"\n\n{room_type}: {room.id}"
                    
                    # Instructor information
                    text += f"\n👤 {instructor}"
                    
                    # Lab indicator
                    if course.is_lab:
                        text += "\n[LAB SESSION]"
                    
                    self.add_course_to_grid(row_idx, col_idx, text, has_conflict)

    def add_course_to_grid(self, row, col, text, has_conflict=False):
        """Tabloya ders ekler ve gerekirse renklendirir [Cite: 20]"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        # Set font for better readability
        font = QFont("Arial", 9)
        item.setFont(font)
        
        # Color coding
        if has_conflict:
            item.setBackground(QColor(255, 200, 200))  # Light red for conflicts
            item.setForeground(QColor(139, 0, 0))  # Dark red text
        else:
            # Different colors for labs vs theory
            if "[LAB SESSION]" in text:
                item.setBackground(QColor(240, 255, 240))  # Light green for labs
                item.setForeground(QColor(0, 100, 0))  # Dark green text
            else:
                item.setBackground(QColor(240, 248, 255))  # Light blue for theory
                item.setForeground(QColor(0, 0, 139))  # Dark blue text
        
        # Make item selectable but not editable
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        
        self.schedule_table.setItem(row, col, item)

if __name__ == "__main__":
    # macOS-specific fixes for PyQt5
    import platform
    
    # Set environment variables BEFORE importing Qt (critical for macOS)
    if platform.system() == "Darwin":  # macOS
        os.environ.setdefault('QT_MAC_WANTS_LAYER', '1')
        os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')
        # Force Cocoa backend on macOS
        os.environ.setdefault('QT_QPA_PLATFORM', 'cocoa')
    
    try:
        # Set high DPI attributes BEFORE creating QApplication
        # Note: These must be set before QApplication is instantiated
        try:
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except (AttributeError, TypeError):
            # Attributes not available in this PyQt5 version, skip
            pass
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("BeePlan")
        app.setOrganizationName("BeePlan")
        
        # Create and show window
        window = BeePlanApp()
        window.show()
        
        # Run event loop
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("TROUBLESHOOTING TIPS:")
        print("="*60)
        print("1. Make sure you're running from Terminal (not SSH)")
        print("2. Try running: export QT_MAC_WANTS_LAYER=1 && python3 main.py")
        print("3. Check PyQt5: python3 -c 'import PyQt5.QtWidgets; print(\"OK\")'")
        print("4. If issues persist, try: pip3 install --upgrade --force-reinstall PyQt5")
        print("="*60)
        sys.exit(1)