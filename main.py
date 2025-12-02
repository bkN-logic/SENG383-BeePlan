import sys
from dataclasses import dataclass, field
from typing import List, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QHeaderView, QMessageBox)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

# ==========================================
# BÖLÜM 1: DATA STRUCTURES (VERİ YAPILARI)
# PDF Referans: Core Requirements [Cite: 5-10]
# ==========================================

@dataclass
class Instructor:
    id: int
    name: str
    availability: List[str] = field(default_factory=list) # Örn: ["Monday", "Tuesday"]

@dataclass
class Room:
    id: str
    capacity: int
    is_lab: bool  # Lab kapasitesi ve türü [Cite: 10, 29]

@dataclass
class Course:
    code: str
    name: str
    instructor_id: int
    duration_hours: int
    is_lab: bool
    requires_projector: bool = False
    year: int = 1 # 1st-4th year [Cite: 12]

@dataclass
class ScheduleSlot:
    day: str
    time_slot: str
    course: Optional[Course] = None
    room: Optional[Room] = None
    has_conflict: bool = False # Görsel uyarı için [Cite: 20]

# ==========================================
# BÖLÜM 2: GUI (KULLANICI ARAYÜZÜ)
# PDF Referans: Implementation & Layout [Cite: 17, 19, 21, 22]
# ==========================================

class BeePlanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BeePlan - Course Scheduler")
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Üst Başlık
        self.header_label = QLabel("Department Course Schedule")
        self.header_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Tablo (Weekly Timetable View) [Cite: 19]
        self.schedule_table = QTableWidget()
        self.setup_table()
        self.layout.addWidget(self.schedule_table)

        # Kontrol Butonları Alanı
        self.button_layout = QHBoxLayout()
        
        # Generate Schedule Butonu [Cite: 21]
        self.btn_generate = QPushButton("Generate Schedule")
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_generate.clicked.connect(self.handle_generate)
        
        # View Report Butonu [Cite: 22]
        self.btn_report = QPushButton("View Report")
        self.btn_report.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.btn_report.clicked.connect(self.handle_report)

        self.button_layout.addWidget(self.btn_generate)
        self.button_layout.addWidget(self.btn_report)
        self.layout.addLayout(self.button_layout)

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

    def handle_generate(self):
        """Backend'e bağlanacak tetikleyici fonksiyon"""
        # Burada algoritma çalışacak. Şimdilik dummy veri gösterelim.
        print("Algoritma çalıştırılıyor...") 
        # Örnek: Pazartesi 08:30'a ders atama simülasyonu
        self.add_course_to_grid(0, 0, "CS101 - Intro to CS\nLab 1")

    def handle_report(self):
        """Çakışma raporlarını gösterecek fonksiyon [Cite: 13]"""
        QMessageBox.information(self, "Validation Report", "No conflicts detected yet.\n(Backend implementation pending)")

    def add_course_to_grid(self, row, col, text, has_conflict=False):
        """Tabloya ders ekler ve gerekirse renklendirir [Cite: 20]"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        if has_conflict:
            item.setBackground(QColor(255, 100, 100)) # Kırmızı uyarı
        else:
            item.setBackground(QColor(220, 240, 255)) # Açık mavi
        self.schedule_table.setItem(row, col, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeePlanApp()
    window.show()
    sys.exit(app.exec_())