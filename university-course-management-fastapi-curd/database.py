from typing import Dict, List, Optional
from datetime import datetime
from models import Student, Course, Professor, Enrollment, Grade


class Database:
    def __init__(self):
        # In-memory storage using dictionaries
        self.students: Dict[int, Student] = {}
        self.courses: Dict[int, Course] = {}
        self.professors: Dict[int, Professor] = {}
        self.enrollments: Dict[tuple, Enrollment] = {}  # key: (student_id, course_id)
        
        # Auto-increment counters for IDs
        self.student_counter = 1
        self.course_counter = 1
        self.professor_counter = 1
    
    def get_next_student_id(self) -> int:
        id_val = self.student_counter
        self.student_counter += 1
        return id_val
    
    def get_next_course_id(self) -> int:
        id_val = self.course_counter
        self.course_counter += 1
        return id_val
    
    def get_next_professor_id(self) -> int:
        id_val = self.professor_counter
        self.professor_counter += 1
        return id_val
    
    # Student operations
    def create_student(self, student_data: dict) -> Student:
        student_id = self.get_next_student_id()
        student = Student(id=student_id, **student_data)
        self.students[student_id] = student
        return student
    
    def get_student(self, student_id: int) -> Optional[Student]:
        return self.students.get(student_id)
    
    def get_all_students(self) -> List[Student]:
        return list(self.students.values())
    
    def update_student(self, student_id: int, update_data: dict) -> Optional[Student]:
        if student_id not in self.students:
            return None
        
        student = self.students[student_id]
        for field, value in update_data.items():
            if value is not None:
                setattr(student, field, value)
        
        return student
    
    def delete_student(self, student_id: int) -> bool:
        if student_id not in self.students:
            return False
        
        # Remove all enrollments for this student
        enrollments_to_remove = [(sid, cid) for sid, cid in self.enrollments.keys() if sid == student_id]
        for key in enrollments_to_remove:
            del self.enrollments[key]
            # Update course enrollment count
            course_id = key[1]
            if course_id in self.courses:
                self.courses[course_id].current_enrollment -= 1
        
        del self.students[student_id]
        return True
    
    # Course operations
    def create_course(self, course_data: dict) -> Course:
        course_id = self.get_next_course_id()
        course = Course(id=course_id, **course_data)
        self.courses[course_id] = course
        return course
    
    def get_course(self, course_id: int) -> Optional[Course]:
        return self.courses.get(course_id)
    
    def get_all_courses(self) -> List[Course]:
        return list(self.courses.values())
    
    def update_course(self, course_id: int, update_data: dict) -> Optional[Course]:
        if course_id not in self.courses:
            return None
        
        course = self.courses[course_id]
        for field, value in update_data.items():
            if value is not None:
                setattr(course, field, value)
        
        return course
    
    def delete_course(self, course_id: int) -> bool:
        if course_id not in self.courses:
            return False
        
        # Remove all enrollments for this course
        enrollments_to_remove = [(sid, cid) for sid, cid in self.enrollments.keys() if cid == course_id]
        for key in enrollments_to_remove:
            del self.enrollments[key]
        
        del self.courses[course_id]
        return True
    
    # Professor operations
    def create_professor(self, professor_data: dict) -> Professor:
        professor_id = self.get_next_professor_id()
        professor = Professor(id=professor_id, **professor_data)
        self.professors[professor_id] = professor
        return professor
    
    def get_professor(self, professor_id: int) -> Optional[Professor]:
        return self.professors.get(professor_id)
    
    def get_all_professors(self) -> List[Professor]:
        return list(self.professors.values())
    
    def update_professor(self, professor_id: int, update_data: dict) -> Optional[Professor]:
        if professor_id not in self.professors:
            return None
        
        professor = self.professors[professor_id]
        for field, value in update_data.items():
            if value is not None:
                setattr(professor, field, value)
        
        return professor
    
    def delete_professor(self, professor_id: int) -> bool:
        if professor_id not in self.professors:
            return False
        
        # Set professor_id to None for all courses taught by this professor
        for course in self.courses.values():
            if course.professor_id == professor_id:
                course.professor_id = None
        
        del self.professors[professor_id]
        return True
    
    # Enrollment operations
    def create_enrollment(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        # Check if student and course exist
        if student_id not in self.students or course_id not in self.courses:
            return None
        
        # Check if already enrolled
        if (student_id, course_id) in self.enrollments:
            return None
        
        # Check course capacity
        course = self.courses[course_id]
        if course.current_enrollment >= course.max_capacity:
            return None
        
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        self.enrollments[(student_id, course_id)] = enrollment
        course.current_enrollment += 1
        
        return enrollment
    
    def get_enrollment(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        return self.enrollments.get((student_id, course_id))
    
    def get_all_enrollments(self) -> List[Enrollment]:
        return list(self.enrollments.values())
    
    def update_enrollment(self, student_id: int, course_id: int, grade: Grade) -> Optional[Enrollment]:
        enrollment = self.enrollments.get((student_id, course_id))
        if enrollment is None:
            return None
        
        old_grade = enrollment.grade
        enrollment.grade = grade
        
        # Recalculate GPA if grade changed
        if old_grade != grade:
            self._recalculate_student_gpa(student_id)
        
        return enrollment
    
    def delete_enrollment(self, student_id: int, course_id: int) -> bool:
        key = (student_id, course_id)
        if key not in self.enrollments:
            return False
        
        del self.enrollments[key]
        
        # Update course enrollment count
        if course_id in self.courses:
            self.courses[course_id].current_enrollment -= 1
        
        # Recalculate GPA
        self._recalculate_student_gpa(student_id)
        
        return True
    
    # Helper methods
    def get_student_courses(self, student_id: int) -> List[Course]:
        courses = []
        for (sid, cid), enrollment in self.enrollments.items():
            if sid == student_id and cid in self.courses:
                courses.append(self.courses[cid])
        return courses
    
    def get_course_students(self, course_id: int) -> List[Student]:
        students = []
        for (sid, cid), enrollment in self.enrollments.items():
            if cid == course_id and sid in self.students:
                students.append(self.students[sid])
        return students
    
    def get_professor_courses(self, professor_id: int) -> List[Course]:
        return [course for course in self.courses.values() if course.professor_id == professor_id]
    
    def _recalculate_student_gpa(self, student_id: int):
        """Recalculate and update student's GPA based on completed courses"""
        if student_id not in self.students:
            return
        
        grade_points = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "F": 0.0
        }
        
        total_credits = 0
        total_points = 0
        
        for (sid, cid), enrollment in self.enrollments.items():
            if sid == student_id and enrollment.grade and enrollment.grade.value in grade_points:
                course = self.courses.get(cid)
                if course:
                    credits = course.credits
                    points = grade_points[enrollment.grade.value]
                    total_credits += credits
                    total_points += points * credits
        
        if total_credits > 0:
            gpa = round(total_points / total_credits, 2)
            self.students[student_id].gpa = gpa
        else:
            self.students[student_id].gpa = None


# Global database instance
db = Database() 