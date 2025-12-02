"""
Scheduling Algorithm Module
Implements constraint-based scheduling with conflict detection
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from models import Course, Room, Instructor, ScheduleSlot


class Scheduler:
    """Main scheduling engine with constraint checking"""
    
    def __init__(self, courses: List[Course], rooms: List[Room], instructors: List[Instructor]):
        self.courses = courses
        self.rooms = rooms
        self.instructors = {inst.id: inst for inst in instructors}
        self.schedule: Dict[str, Dict[str, ScheduleSlot]] = {}
        self.conflicts: List[Dict] = []
        
        # Initialize schedule grid
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.time_slots = [
            "08:30 - 09:20", "09:30 - 10:20", "10:30 - 11:20", "11:30 - 12:20",
            "13:20 - 14:10", "14:20 - 15:10", "15:20 - 16:10", "16:20 - 17:10"
        ]
        
        for day in self.days:
            self.schedule[day] = {}
            for time_slot in self.time_slots:
                self.schedule[day][time_slot] = ScheduleSlot(day=day, time_slot=time_slot)
    
    def generate_schedule(self) -> bool:
        """
        Main scheduling algorithm using heuristic approach
        Returns True if successful, False if conflicts remain
        """
        # Sort courses by priority: 
        # 1. Theory courses before labs (so labs can follow their theory)
        # 2. Lower year courses first (more fundamental courses scheduled first)
        # 3. Courses with more constraints scheduled first
        sorted_courses = sorted(
            self.courses, 
            key=lambda c: (
                c.is_lab,  # False (theory) comes before True (lab)
                c.year,    # Lower years first (1, 2, 3, 4)
            )
        )
        
        # Track instructor daily hours
        instructor_daily_hours: Dict[int, Dict[str, int]] = {}
        
        for course in sorted_courses:
            placed = False
            
            # Find theory course first if this is a lab
            theory_course = None
            if course.is_lab:
                theory_course = self._find_theory_course(course)
            
            # Try to place course
            for day in self.days:
                if not self._is_instructor_available(course.instructor_id, day):
                    continue
                
                for i, time_slot in enumerate(self.time_slots):
                    # Check Friday exam block constraint
                    if day == "Friday" and i in [4, 5]:  # 13:20-15:10
                        continue
                    
                    # Check if slot is free
                    if self.schedule[day][time_slot].course is not None:
                        continue
                    
                    # Check lab must follow theory constraint
                    if course.is_lab:
                        if theory_course:
                            if not self._lab_follows_theory(day, i, theory_course):
                                continue
                        # If no theory course found, still allow lab (relaxed constraint)
                    
                    # Find suitable room
                    room = self._find_suitable_room(course, day, time_slot)
                    if not room:
                        continue
                    
                    # Check instructor daily hours limit (max 4 theory hours per day)
                    if not course.is_lab:
                        if not self._check_instructor_daily_limit(course.instructor_id, day, instructor_daily_hours):
                            continue
                    
                    # Check elective overlap constraints
                    if not self._check_elective_constraints(course, day, time_slot):
                        continue
                    
                    # Place the course
                    self.schedule[day][time_slot].course = course
                    self.schedule[day][time_slot].room = room
                    
                    # Update instructor hours
                    if not course.is_lab:
                        if course.instructor_id not in instructor_daily_hours:
                            instructor_daily_hours[course.instructor_id] = {}
                        if day not in instructor_daily_hours[course.instructor_id]:
                            instructor_daily_hours[course.instructor_id][day] = 0
                        instructor_daily_hours[course.instructor_id][day] += 1
                    
                    placed = True
                    break
                
                if placed:
                    break
            
            if not placed:
                # Could not place course - will be reported as conflict
                self.conflicts.append({
                    "type": "unplaced_course",
                    "course": course.code,
                    "message": f"Could not place {course.code}"
                })
        
        # Validate and detect conflicts
        self._validate_schedule()
        
        return len(self.conflicts) == 0
    
    def _find_theory_course(self, lab_course: Course) -> Optional[Course]:
        """Find corresponding theory course for a lab"""
        # Find theory course with same base code (e.g., CS101 for CS101L)
        lab_code_base = lab_course.code.replace('L', '').strip()
        for course in self.courses:
            if (not course.is_lab and 
                course.code == lab_code_base and
                course.instructor_id == lab_course.instructor_id):
                return course
        # If exact match not found, try partial match
        for course in self.courses:
            if (not course.is_lab and 
                course.code.startswith(lab_code_base) and
                course.instructor_id == lab_course.instructor_id):
                return course
        return None
    
    def _lab_follows_theory(self, day: str, time_index: int, theory_course: Course) -> bool:
        """Check if lab can follow theory course on same day"""
        # Find theory course position
        for i, time_slot in enumerate(self.time_slots):
            slot = self.schedule[day][time_slot]
            if slot.course == theory_course:
                # Lab should be after theory (time_index > i)
                return time_index > i
        return False
    
    def _is_instructor_available(self, instructor_id: int, day: str) -> bool:
        """Check if instructor is available on given day"""
        instructor = self.instructors.get(instructor_id)
        if not instructor:
            return False
        return day in instructor.availability
    
    def _find_suitable_room(self, course: Course, day: str, time_slot: str) -> Optional[Room]:
        """Find a suitable room for the course"""
        for room in self.rooms:
            # Check if room type matches
            if course.is_lab != room.is_lab:
                continue
            
            # Check lab capacity constraint (≤ 40 students)
            if course.is_lab and room.capacity > 40:
                continue
            
            # Check if room is free at this time
            if self._is_room_available(room, day, time_slot):
                return room
        return None
    
    def _is_room_available(self, room: Room, day: str, time_slot: str) -> bool:
        """Check if room is available at given time"""
        slot = self.schedule[day][time_slot]
        # Room is available if no course is scheduled in this slot
        return slot.course is None
    
    def _check_instructor_daily_limit(self, instructor_id: int, day: str, 
                                     instructor_hours: Dict[int, Dict[str, int]]) -> bool:
        """Check if instructor hasn't exceeded 4 theory hours per day"""
        if instructor_id not in instructor_hours:
            return True
        if day not in instructor_hours[instructor_id]:
            return True
        return instructor_hours[instructor_id][day] < 4
    
    def _check_elective_constraints(self, course: Course, day: str, time_slot: str) -> bool:
        """Check 3rd-year and elective overlap constraints"""
        slot = self.schedule[day][time_slot]
        
        # If slot is empty, no constraint violation
        if slot.course is None:
            return True
        
        other_course = slot.course
        
        # Rule: 3rd-year courses should not overlap with electives (4th year)
        if course.year == 3 and other_course.year == 4:
            return False
        if course.year == 4 and other_course.year == 3:
            return False
        
        # Rule: CENG and SENG electives must not overlap
        course_code_upper = course.code.upper()
        other_code_upper = other_course.code.upper()
        
        is_ceng = "CENG" in course_code_upper
        is_seng = "SENG" in course_code_upper
        other_is_ceng = "CENG" in other_code_upper
        other_is_seng = "SENG" in other_code_upper
        
        # If one is CENG and other is SENG, they cannot overlap
        if (is_ceng and other_is_seng) or (is_seng and other_is_ceng):
            return False
        
        return True
    
    def _validate_schedule(self):
        """Validate schedule and detect all conflicts"""
        self.conflicts = []
        
        # Track instructor schedules
        instructor_schedule: Dict[int, List[Tuple[str, str]]] = {}
        
        for day in self.days:
            for time_slot in self.time_slots:
                slot = self.schedule[day][time_slot]
                
                if slot.course is None:
                    continue
                
                course = slot.course
                room = slot.room
                
                # Check instructor double booking
                if course.instructor_id not in instructor_schedule:
                    instructor_schedule[course.instructor_id] = []
                else:
                    # Check if instructor already has a course at this time
                    for other_day, other_time in instructor_schedule[course.instructor_id]:
                        if day == other_day and time_slot == other_time:
                            self.conflicts.append({
                                "type": "instructor_overlap",
                                "course": course.code,
                                "instructor": course.instructor_id,
                                "day": day,
                                "time": time_slot,
                                "message": f"Instructor {course.instructor_id} double-booked at {day} {time_slot}"
                            })
                            break
                
                instructor_schedule[course.instructor_id].append((day, time_slot))
                
                # Check room capacity
                if room and course.is_lab and room.capacity > 40:
                    self.conflicts.append({
                        "type": "capacity_violation",
                        "course": course.code,
                        "room": room.id,
                        "capacity": room.capacity,
                        "message": f"Lab room {room.id} exceeds 40 student capacity"
                    })
                
                # Check room double booking (same room at same time)
                if room:
                    # Check if another course uses the same room at the same time
                    for other_day in self.days:
                        for other_time in self.time_slots:
                            if other_day == day and other_time == time_slot:
                                continue  # Skip current slot
                            other_slot = self.schedule[other_day][other_time]
                            if (other_slot.room and other_slot.room.id == room.id and
                                other_slot.course and other_slot.course.code != course.code):
                                # Same room used at different time - this is OK
                                # Only conflict if same time, which we skip above
                                pass
                
                # Mark conflicts in schedule
                if self.conflicts:
                    slot.has_conflict = True
    
    def get_schedule_grid(self) -> List[List[Optional[Dict]]]:
        """Get schedule as 2D grid for GUI display"""
        grid = []
        for time_slot in self.time_slots:
            row = []
            for day in self.days:
                slot = self.schedule[day][time_slot]
                if slot.course:
                    # Get instructor information
                    instructor = self.instructors.get(slot.course.instructor_id)
                    instructor_name = instructor.name if instructor else f"Instructor {slot.course.instructor_id}"
                    
                    row.append({
                        "course": slot.course,
                        "room": slot.room,
                        "instructor": instructor_name,
                        "has_conflict": slot.has_conflict
                    })
                else:
                    row.append(None)
            grid.append(row)
        return grid
    
    def get_conflicts(self) -> List[Dict]:
        """Get list of all detected conflicts"""
        return self.conflicts

