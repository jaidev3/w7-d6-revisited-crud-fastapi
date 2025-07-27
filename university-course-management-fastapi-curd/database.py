from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from models import Student, Course, Professor, Enrollment, Grade
import math


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


class ConflictError(Exception):
    """Custom exception for business rule violations"""
    def __init__(self, message: str, conflict_type: str = "general", existing_resource=None):
        self.message = message
        self.conflict_type = conflict_type
        self.existing_resource = existing_resource
        super().__init__(self.message)


class Database:
    def __init__(self):
        # In-memory storage using dictionaries
        self.students: Dict[int, Student] = {}
        self.courses: Dict[int, Course] = {}
        self.professors: Dict[int, Professor] = {}
        self.enrollments: Dict[tuple, Enrollment] = {}  # key: (student_id, course_id)
        
        # Email uniqueness tracking
        self.student_emails: Dict[str, int] = {}  # email -> student_id
        self.professor_emails: Dict[str, int] = {}  # email -> professor_id
        
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
        # Check email uniqueness
        email = student_data.get('email')
        if email and (email in self.student_emails or email in self.professor_emails):
            raise ConflictError(
                f"Email {email} is already in use",
                conflict_type="duplicate_email",
                existing_resource={"email": email}
            )
        
        student_id = self.get_next_student_id()
        student = Student(id=student_id, **student_data)
        
        # Set academic probation status based on GPA
        if student.gpa is not None and student.gpa < 2.0:
            student.is_on_probation = True
        
        self.students[student_id] = student
        if email:
            self.student_emails[email] = student_id
        
        return student
    
    def get_student(self, student_id: int) -> Optional[Student]:
        return self.students.get(student_id)
    
    def get_all_students(self, filters: Dict = None, page: int = 1, limit: int = 10) -> Tuple[List[Student], int]:
        students = list(self.students.values())
        
        # Apply filters
        if filters:
            if filters.get('major'):
                students = [s for s in students if s.major.lower() == filters['major'].lower()]
            if filters.get('year'):
                students = [s for s in students if s.year == filters['year']]
            if filters.get('min_gpa') is not None:
                students = [s for s in students if s.gpa is not None and s.gpa >= filters['min_gpa']]
            if filters.get('max_gpa') is not None:
                students = [s for s in students if s.gpa is not None and s.gpa <= filters['max_gpa']]
            if filters.get('on_probation') is not None:
                students = [s for s in students if s.is_on_probation == filters['on_probation']]
        
        total = len(students)
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_students = students[start:end]
        
        return paginated_students, total
    
    def update_student(self, student_id: int, update_data: dict) -> Optional[Student]:
        if student_id not in self.students:
            return None
        
        student = self.students[student_id]
        old_email = student.email
        
        # Check email uniqueness if email is being updated
        new_email = update_data.get('email')
        if new_email and new_email != old_email:
            if new_email in self.student_emails or new_email in self.professor_emails:
                raise ConflictError(
                    f"Email {new_email} is already in use",
                    conflict_type="duplicate_email"
                )
        
        for field, value in update_data.items():
            if value is not None:
                setattr(student, field, value)
        
        # Update academic probation status
        if student.gpa is not None:
            student.is_on_probation = student.gpa < 2.0
        
        # Update email tracking
        if new_email and new_email != old_email:
            if old_email in self.student_emails:
                del self.student_emails[old_email]
            self.student_emails[new_email] = student_id
        
        return student
    
    def delete_student(self, student_id: int) -> bool:
        if student_id not in self.students:
            return False
        
        student = self.students[student_id]
        
        # Remove email from tracking
        if student.email in self.student_emails:
            del self.student_emails[student.email]
        
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
    
    def validate_student_credit_limit(self, student_id: int, new_course_credits: int = 0) -> bool:
        """Check if student would exceed 18 credit hour limit"""
        current_credits = self.get_student_total_credits(student_id)
        return (current_credits + new_course_credits) <= 18
    
    def get_student_total_credits(self, student_id: int) -> int:
        """Calculate total credit hours for a student"""
        total_credits = 0
        for (sid, cid), enrollment in self.enrollments.items():
            if sid == student_id and cid in self.courses:
                # Don't count withdrawn courses
                if enrollment.grade != Grade.WITHDRAW:
                    course = self.courses[cid]
                    total_credits += course.credits
        return total_credits
    
    # Course operations
    def create_course(self, course_data: dict) -> Course:
        course_id = self.get_next_course_id()
        course = Course(id=course_id, **course_data)
        self.courses[course_id] = course
        
        # Update professor teaching load
        if course.professor_id:
            self._update_professor_teaching_load(course.professor_id)
        
        return course
    
    def get_course(self, course_id: int) -> Optional[Course]:
        return self.courses.get(course_id)
    
    def get_all_courses(self, filters: Dict = None, page: int = 1, limit: int = 10) -> Tuple[List[Course], int]:
        courses = list(self.courses.values())
        
        # Apply filters
        if filters:
            if filters.get('department'):
                courses = [c for c in courses if c.department.lower() == filters['department'].lower()]
            if filters.get('credits'):
                courses = [c for c in courses if c.credits == filters['credits']]
            if filters.get('professor_id'):
                courses = [c for c in courses if c.professor_id == filters['professor_id']]
            if filters.get('has_capacity'):
                courses = [c for c in courses if c.current_enrollment < c.max_capacity]
        
        total = len(courses)
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_courses = courses[start:end]
        
        return paginated_courses, total
    
    def update_course(self, course_id: int, update_data: dict) -> Optional[Course]:
        if course_id not in self.courses:
            return None
        
        course = self.courses[course_id]
        old_professor_id = course.professor_id
        
        for field, value in update_data.items():
            if value is not None:
                setattr(course, field, value)
        
        # Update professor teaching loads if professor changed
        new_professor_id = course.professor_id
        if old_professor_id != new_professor_id:
            if old_professor_id:
                self._update_professor_teaching_load(old_professor_id)
            if new_professor_id:
                self._update_professor_teaching_load(new_professor_id)
        
        return course
    
    def delete_course(self, course_id: int) -> bool:
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        
        # Update professor teaching load
        if course.professor_id:
            self._update_professor_teaching_load(course.professor_id)
        
        # Remove all enrollments for this course
        enrollments_to_remove = [(sid, cid) for sid, cid in self.enrollments.keys() if cid == course_id]
        for key in enrollments_to_remove:
            del self.enrollments[key]
        
        del self.courses[course_id]
        return True
    
    def check_prerequisites(self, student_id: int, course_id: int) -> bool:
        """Check if student has completed all prerequisites for a course"""
        course = self.courses.get(course_id)
        if not course or not course.prerequisites:
            return True
        
        # Get student's completed courses with passing grades
        completed_courses = set()
        for (sid, cid), enrollment in self.enrollments.items():
            if sid == student_id and enrollment.grade:
                if enrollment.grade.value in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']:
                    if cid in self.courses:
                        completed_courses.add(self.courses[cid].code)
        
        # Check if all prerequisites are completed
        for prereq in course.prerequisites:
            if prereq not in completed_courses:
                return False
        
        return True
    
    # Professor operations
    def create_professor(self, professor_data: dict) -> Professor:
        # Check email uniqueness
        email = professor_data.get('email')
        if email and (email in self.student_emails or email in self.professor_emails):
            raise ConflictError(
                f"Email {email} is already in use",
                conflict_type="duplicate_email",
                existing_resource={"email": email}
            )
        
        professor_id = self.get_next_professor_id()
        professor = Professor(id=professor_id, **professor_data)
        self.professors[professor_id] = professor
        
        if email:
            self.professor_emails[email] = professor_id
        
        return professor
    
    def get_professor(self, professor_id: int) -> Optional[Professor]:
        return self.professors.get(professor_id)
    
    def get_all_professors(self, filters: Dict = None, page: int = 1, limit: int = 10) -> Tuple[List[Professor], int]:
        professors = list(self.professors.values())
        
        # Apply filters
        if filters:
            if filters.get('department'):
                professors = [p for p in professors if p.department.lower() == filters['department'].lower()]
            if filters.get('hire_year'):
                professors = [p for p in professors if p.hire_date.year == filters['hire_year']]
        
        total = len(professors)
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_professors = professors[start:end]
        
        return paginated_professors, total
    
    def update_professor(self, professor_id: int, update_data: dict) -> Optional[Professor]:
        if professor_id not in self.professors:
            return None
        
        professor = self.professors[professor_id]
        old_email = professor.email
        
        # Check email uniqueness if email is being updated
        new_email = update_data.get('email')
        if new_email and new_email != old_email:
            if new_email in self.student_emails or new_email in self.professor_emails:
                raise ConflictError(
                    f"Email {new_email} is already in use",
                    conflict_type="duplicate_email"
                )
        
        for field, value in update_data.items():
            if value is not None:
                setattr(professor, field, value)
        
        # Update email tracking
        if new_email and new_email != old_email:
            if old_email in self.professor_emails:
                del self.professor_emails[old_email]
            self.professor_emails[new_email] = professor_id
        
        return professor
    
    def delete_professor(self, professor_id: int) -> bool:
        if professor_id not in self.professors:
            return False
        
        professor = self.professors[professor_id]
        
        # Remove email from tracking
        if professor.email in self.professor_emails:
            del self.professor_emails[professor.email]
        
        # Set professor_id to None for all courses taught by this professor
        for course in self.courses.values():
            if course.professor_id == professor_id:
                course.professor_id = None
        
        del self.professors[professor_id]
        return True
    
    def validate_professor_teaching_load(self, professor_id: int, additional_courses: int = 0) -> bool:
        """Check if professor would exceed 4 course limit"""
        current_load = len(self.get_professor_courses(professor_id))
        return (current_load + additional_courses) <= 4
    
    def _update_professor_teaching_load(self, professor_id: int):
        """Update professor's current teaching load"""
        if professor_id in self.professors:
            courses_count = len(self.get_professor_courses(professor_id))
            self.professors[professor_id].current_teaching_load = courses_count
    
    # Enrollment operations
    def create_enrollment(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        # Check if student and course exist
        if student_id not in self.students or course_id not in self.courses:
            return None
        
        # Check if already enrolled
        if (student_id, course_id) in self.enrollments:
            return None
        
        course = self.courses[course_id]
        
        # Check course capacity
        if course.current_enrollment >= course.max_capacity:
            raise ConflictError(
                f"Course {course.name} is at maximum capacity ({course.max_capacity})",
                conflict_type="capacity_exceeded",
                existing_resource={"course_id": course_id, "current_enrollment": course.current_enrollment}
            )
        
        # Check prerequisites
        if not self.check_prerequisites(student_id, course_id):
            raise ConflictError(
                f"Student does not meet prerequisites for course {course.name}",
                conflict_type="prerequisites_not_met",
                existing_resource={"course_id": course_id, "prerequisites": course.prerequisites}
            )
        
        # Check credit hour limit
        if not self.validate_student_credit_limit(student_id, course.credits):
            raise ConflictError(
                f"Enrollment would exceed 18 credit hour limit",
                conflict_type="credit_limit_exceeded",
                existing_resource={"student_id": student_id, "current_credits": self.get_student_total_credits(student_id)}
            )
        
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        self.enrollments[(student_id, course_id)] = enrollment
        course.current_enrollment += 1
        
        return enrollment
    
    def get_enrollment(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        return self.enrollments.get((student_id, course_id))
    
    def get_all_enrollments(self, page: int = 1, limit: int = 10) -> Tuple[List[Enrollment], int]:
        enrollments = list(self.enrollments.values())
        total = len(enrollments)
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_enrollments = enrollments[start:end]
        
        return paginated_enrollments, total
    
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
    
    # Bulk operations
    def bulk_create_students(self, students_data: List[dict]) -> List[Student]:
        """Create multiple students in bulk"""
        created_students = []
        errors = []
        
        for i, student_data in enumerate(students_data):
            try:
                student = self.create_student(student_data)
                created_students.append(student)
            except ConflictError as e:
                errors.append(f"Student {i}: {e.message}")
        
        if errors:
            raise DatabaseError(f"Bulk creation failed for some students: {'; '.join(errors)}")
        
        return created_students
    
    def bulk_create_enrollments(self, enrollments_data: List[dict]) -> List[Enrollment]:
        """Create multiple enrollments in bulk"""
        created_enrollments = []
        errors = []
        
        for i, enrollment_data in enumerate(enrollments_data):
            try:
                enrollment = self.create_enrollment(
                    enrollment_data['student_id'],
                    enrollment_data['course_id']
                )
                if enrollment:
                    created_enrollments.append(enrollment)
                else:
                    errors.append(f"Enrollment {i}: Failed to create")
            except ConflictError as e:
                errors.append(f"Enrollment {i}: {e.message}")
        
        if errors:
            raise DatabaseError(f"Bulk enrollment failed for some entries: {'; '.join(errors)}")
        
        return created_enrollments
    
    def bulk_update_grades(self, grade_updates: List[dict]) -> List[Enrollment]:
        """Update multiple grades in bulk"""
        updated_enrollments = []
        errors = []
        
        for i, update_data in enumerate(grade_updates):
            try:
                enrollment = self.update_enrollment(
                    update_data['student_id'],
                    update_data['course_id'],
                    Grade(update_data['grade'])
                )
                if enrollment:
                    updated_enrollments.append(enrollment)
                else:
                    errors.append(f"Grade update {i}: Enrollment not found")
            except Exception as e:
                errors.append(f"Grade update {i}: {str(e)}")
        
        if errors:
            raise DatabaseError(f"Bulk grade update failed for some entries: {'; '.join(errors)}")
        
        return updated_enrollments
    
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
            # Update probation status
            self.students[student_id].is_on_probation = gpa < 2.0
        else:
            self.students[student_id].gpa = None
            self.students[student_id].is_on_probation = False
    
    # Analytics methods
    def get_gpa_distribution(self) -> List[dict]:
        """Get GPA distribution analytics"""
        gpa_ranges = {
            "4.0": 0,
            "3.5-3.9": 0,
            "3.0-3.4": 0,
            "2.5-2.9": 0,
            "2.0-2.4": 0,
            "Below 2.0": 0,
            "No GPA": 0
        }
        
        total_students = len(self.students)
        
        for student in self.students.values():
            if student.gpa is None:
                gpa_ranges["No GPA"] += 1
            elif student.gpa == 4.0:
                gpa_ranges["4.0"] += 1
            elif student.gpa >= 3.5:
                gpa_ranges["3.5-3.9"] += 1
            elif student.gpa >= 3.0:
                gpa_ranges["3.0-3.4"] += 1
            elif student.gpa >= 2.5:
                gpa_ranges["2.5-2.9"] += 1
            elif student.gpa >= 2.0:
                gpa_ranges["2.0-2.4"] += 1
            else:
                gpa_ranges["Below 2.0"] += 1
        
        distribution = []
        for range_name, count in gpa_ranges.items():
            percentage = (count / total_students * 100) if total_students > 0 else 0
            distribution.append({
                "gpa_range": range_name,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        return distribution
    
    def get_enrollment_stats(self) -> List[dict]:
        """Get course enrollment statistics"""
        stats = []
        for course in self.courses.values():
            utilization_rate = (course.current_enrollment / course.max_capacity * 100) if course.max_capacity > 0 else 0
            stats.append({
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "current_enrollment": course.current_enrollment,
                "max_capacity": course.max_capacity,
                "utilization_rate": round(utilization_rate, 2)
            })
        
        return sorted(stats, key=lambda x: x["utilization_rate"], reverse=True)
    
    def get_teaching_load_stats(self) -> List[dict]:
        """Get professor teaching load statistics"""
        stats = []
        for professor in self.professors.values():
            courses = self.get_professor_courses(professor.id)
            total_students = sum(course.current_enrollment for course in courses)
            
            stats.append({
                "professor_id": professor.id,
                "professor_name": professor.name,
                "department": professor.department,
                "courses_count": len(courses),
                "total_students": total_students
            })
        
        return sorted(stats, key=lambda x: x["courses_count"], reverse=True)
    
    def get_department_performance(self) -> List[dict]:
        """Get department performance analytics"""
        departments = {}
        
        # Collect department data
        for professor in self.professors.values():
            dept = professor.department
            if dept not in departments:
                departments[dept] = {
                    "total_students": set(),
                    "total_courses": 0,
                    "total_professors": 0,
                    "gpa_sum": 0,
                    "gpa_count": 0
                }
            departments[dept]["total_professors"] += 1
        
        for course in self.courses.values():
            dept = course.department
            if dept not in departments:
                departments[dept] = {
                    "total_students": set(),
                    "total_courses": 0,
                    "total_professors": 0,
                    "gpa_sum": 0,
                    "gpa_count": 0
                }
            departments[dept]["total_courses"] += 1
            
            # Count students in this department
            for (sid, cid), enrollment in self.enrollments.items():
                if cid == course.id and sid in self.students:
                    departments[dept]["total_students"].add(sid)
                    student = self.students[sid]
                    if student.gpa is not None:
                        departments[dept]["gpa_sum"] += student.gpa
                        departments[dept]["gpa_count"] += 1
        
        # Convert to final format
        performance = []
        for dept_name, data in departments.items():
            avg_gpa = (data["gpa_sum"] / data["gpa_count"]) if data["gpa_count"] > 0 else 0
            performance.append({
                "department": dept_name,
                "total_students": len(data["total_students"]),
                "average_gpa": round(avg_gpa, 2),
                "total_courses": data["total_courses"],
                "total_professors": data["total_professors"]
            })
        
        return sorted(performance, key=lambda x: x["average_gpa"], reverse=True)


# Global database instance
db = Database() 