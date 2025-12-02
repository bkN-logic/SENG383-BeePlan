"""
Data Management Module
Handles import/export from JSON and CSV
"""
import json
import csv
from typing import List, Dict
from models import Course, Room, Instructor


class DataManager:
    """Manages data import/export operations"""
    
    @staticmethod
    def load_from_json(filepath: str) -> Dict:
        """Load data from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_to_json(data: Dict, filepath: str):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_from_csv(filepath: str) -> List[Dict]:
        """Load data from CSV file"""
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def save_to_csv(data: List[Dict], filepath: str, fieldnames: List[str]):
        """Save data to CSV file"""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def parse_courses(data: Dict) -> List[Course]:
        """Parse courses from data dictionary"""
        courses = []
        for course_data in data.get('courses', []):
            course = Course(
                code=course_data['code'],
                name=course_data['name'],
                instructor_id=course_data['instructor_id'],
                duration_hours=course_data.get('duration_hours', 1),
                is_lab=course_data.get('is_lab', False),
                requires_projector=course_data.get('requires_projector', False),
                year=course_data.get('year', 1)
            )
            courses.append(course)
        return courses
    
    @staticmethod
    def parse_rooms(data: Dict) -> List[Room]:
        """Parse rooms from data dictionary"""
        rooms = []
        for room_data in data.get('rooms', []):
            room = Room(
                id=room_data['id'],
                capacity=room_data['capacity'],
                is_lab=room_data.get('is_lab', False)
            )
            rooms.append(room)
        return rooms
    
    @staticmethod
    def parse_instructors(data: Dict) -> List[Instructor]:
        """Parse instructors from data dictionary"""
        instructors = []
        for inst_data in data.get('instructors', []):
            instructor = Instructor(
                id=inst_data['id'],
                name=inst_data['name'],
                availability=inst_data.get('availability', [])
            )
            instructors.append(instructor)
        return instructors
    
    @staticmethod
    def export_schedule_to_json(scheduler, filepath: str):
        """Export schedule to JSON file"""
        schedule_data = {
            "days": scheduler.days,
            "time_slots": scheduler.time_slots,
            "schedule": {}
        }
        
        for day in scheduler.days:
            schedule_data["schedule"][day] = {}
            for time_slot in scheduler.time_slots:
                slot = scheduler.schedule[day][time_slot]
                if slot.course:
                    schedule_data["schedule"][day][time_slot] = {
                        "course_code": slot.course.code,
                        "course_name": slot.course.name,
                        "instructor_id": slot.course.instructor_id,
                        "instructor_name": scheduler.instructors.get(slot.course.instructor_id).name if scheduler.instructors.get(slot.course.instructor_id) else f"Instructor {slot.course.instructor_id}",
                        "room_id": slot.room.id if slot.room else None,
                        "room_capacity": slot.room.capacity if slot.room else None,
                        "is_lab": slot.course.is_lab,
                        "year": slot.course.year,
                        "has_conflict": slot.has_conflict
                    }
                else:
                    schedule_data["schedule"][day][time_slot] = None
        
        DataManager.save_to_json(schedule_data, filepath)
    
    @staticmethod
    def export_schedule_to_csv(scheduler, filepath: str):
        """Export schedule to CSV file"""
        rows = []
        for day in scheduler.days:
            for time_slot in scheduler.time_slots:
                slot = scheduler.schedule[day][time_slot]
                if slot.course:
                    instructor = scheduler.instructors.get(slot.course.instructor_id)
                    instructor_name = instructor.name if instructor else f"Instructor {slot.course.instructor_id}"
                    
                    rows.append({
                        "Day": day,
                        "Time": time_slot,
                        "Course Code": slot.course.code,
                        "Course Name": slot.course.name,
                        "Instructor": instructor_name,
                        "Room": slot.room.id if slot.room else "N/A",
                        "Room Type": "Lab" if slot.room.is_lab else "Classroom" if slot.room else "N/A",
                        "Year": slot.course.year,
                        "Type": "Lab" if slot.course.is_lab else "Theory",
                        "Conflict": "Yes" if slot.has_conflict else "No"
                    })
        
        fieldnames = ["Day", "Time", "Course Code", "Course Name", "Instructor", "Room", "Room Type", "Year", "Type", "Conflict"]
        DataManager.save_to_csv(rows, filepath, fieldnames)
    
    @staticmethod
    def create_sample_data() -> Dict:
        """Create sample data for testing"""
        return {
            "instructors": [
                {"id": 1, "name": "Dr. Smith", "availability": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
                {"id": 2, "name": "Dr. Jones", "availability": ["Monday", "Wednesday", "Friday"]},
                {"id": 3, "name": "Dr. Brown", "availability": ["Tuesday", "Thursday"]}
            ],
            "rooms": [
                {"id": "A101", "capacity": 50, "is_lab": False},
                {"id": "A102", "capacity": 60, "is_lab": False},
                {"id": "LAB1", "capacity": 30, "is_lab": True},
                {"id": "LAB2", "capacity": 35, "is_lab": True}
            ],
            "courses": [
                {"code": "CS101", "name": "Introduction to Computer Science", "instructor_id": 1, 
                 "duration_hours": 1, "is_lab": False, "year": 1},
                {"code": "CS101L", "name": "CS101 Lab", "instructor_id": 1, 
                 "duration_hours": 2, "is_lab": True, "year": 1},
                {"code": "CS201", "name": "Data Structures", "instructor_id": 2, 
                 "duration_hours": 1, "is_lab": False, "year": 2},
                {"code": "CS301", "name": "Algorithms", "instructor_id": 3, 
                 "duration_hours": 1, "is_lab": False, "year": 3},
                {"code": "CENG401", "name": "Computer Engineering Elective", "instructor_id": 1, 
                 "duration_hours": 1, "is_lab": False, "year": 4}
            ]
        }

