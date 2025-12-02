"""
Data Models Module
Contains all data structures for the scheduling system
"""
from dataclasses import dataclass, field
from typing import List, Optional

# ==========================================
# DATA STRUCTURES (VERİ YAPILARI)
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

