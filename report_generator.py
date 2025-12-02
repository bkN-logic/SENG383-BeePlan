"""
Report Generation Module
Creates validation reports with conflict details
"""
from typing import List, Dict
from scheduler import Scheduler


class ReportGenerator:
    """Generates validation and conflict reports"""
    
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        conflicts = self.scheduler.get_conflicts()
        schedule_grid = self.scheduler.get_schedule_grid()
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("SCHEDULE VALIDATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Summary
        total_courses = sum(1 for row in schedule_grid for cell in row if cell is not None)
        report_lines.append(f"Total Courses Scheduled: {total_courses}")
        report_lines.append(f"Total Conflicts Detected: {len(conflicts)}")
        report_lines.append("")
        
        if len(conflicts) == 0:
            report_lines.append("✓ No conflicts detected. Schedule is valid!")
            report_lines.append("")
        else:
            report_lines.append("⚠ CONFLICTS DETECTED:")
            report_lines.append("-" * 60)
            
            # Group conflicts by type
            conflict_types = {}
            for conflict in conflicts:
                conflict_type = conflict.get('type', 'unknown')
                if conflict_type not in conflict_types:
                    conflict_types[conflict_type] = []
                conflict_types[conflict_type].append(conflict)
            
            # Report each type
            for conflict_type, conflict_list in conflict_types.items():
                report_lines.append(f"\n{conflict_type.upper().replace('_', ' ')} ({len(conflict_list)}):")
                for conflict in conflict_list:
                    report_lines.append(f"  • {conflict.get('message', 'Unknown conflict')}")
                    if 'course' in conflict:
                        report_lines.append(f"    Course: {conflict['course']}")
                    if 'day' in conflict and 'time' in conflict:
                        report_lines.append(f"    Time: {conflict['day']} {conflict['time']}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("SCHEDULE DETAILS")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Detailed schedule
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = [
            "08:30 - 09:20", "09:30 - 10:20", "10:30 - 11:20", "11:30 - 12:20",
            "13:20 - 14:10", "14:20 - 15:10", "15:20 - 16:10", "16:20 - 17:10"
        ]
        
        for day in days:
            report_lines.append(f"\n{day}:")
            report_lines.append("-" * 40)
            for i, time_slot in enumerate(time_slots):
                row = schedule_grid[i]
                day_index = days.index(day)
                cell = row[day_index]
                
                if cell:
                    course = cell['course']
                    room = cell['room']
                    conflict_marker = " ⚠ CONFLICT" if cell['has_conflict'] else ""
                    report_lines.append(
                        f"  {time_slot}: {course.code} - {course.name} "
                        f"(Room: {room.id if room else 'N/A'}){conflict_marker}"
                    )
        
        return "\n".join(report_lines)
    
    def get_conflict_summary(self) -> str:
        """Get a brief summary of conflicts"""
        conflicts = self.scheduler.get_conflicts()
        
        if len(conflicts) == 0:
            return "✓ No conflicts detected. Schedule is valid!"
        
        summary = f"⚠ {len(conflicts)} conflict(s) detected:\n\n"
        
        conflict_types = {}
        for conflict in conflicts:
            conflict_type = conflict.get('type', 'unknown')
            if conflict_type not in conflict_types:
                conflict_types[conflict_type] = 0
            conflict_types[conflict_type] += 1
        
        for conflict_type, count in conflict_types.items():
            summary += f"• {conflict_type.replace('_', ' ').title()}: {count}\n"
        
        return summary

