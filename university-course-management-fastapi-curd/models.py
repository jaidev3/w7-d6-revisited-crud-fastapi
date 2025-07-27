from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import re


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    email: EmailStr = Field(..., description="Valid email address")
    major: str = Field(..., min_length=1, max_length=50, description="Student's major field of study")
    year: int = Field(..., ge=1, le=4, description="Academic year (1-4)")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="Grade Point Average (0.0-4.0)")

    @field_validator('email')
    def validate_email_uniqueness(cls, v):
        # This will be handled at the database level for uniqueness
        return v


class Student(StudentCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    is_on_probation: bool = Field(default=False, description="Academic probation status")


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    major: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1, le=4)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Course name")
    code: str = Field(..., description="Course code in format DEPT###-### (e.g., CS101-001)")
    credits: int = Field(..., ge=1, le=6, description="Credit hours (1-6)")
    department: str = Field(..., min_length=1, max_length=50, description="Department offering the course")
    professor_id: Optional[int] = Field(None, description="Assigned professor ID")
    max_capacity: int = Field(..., ge=1, le=500, description="Maximum enrollment capacity")
    prerequisites: Optional[List[str]] = Field(default=[], description="List of prerequisite course codes")

    @field_validator('code')
    def validate_course_code(cls, v):
        pattern = r'^[A-Z]{2,4}\d{3}-\d{3}$'
        if not re.match(pattern, v):
            raise ValueError('Course code must follow format DEPT###-### (e.g., CS101-001)')
        return v


class Course(CourseCreate):
    id: int
    current_enrollment: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="Course code in format DEPT###-###")
    credits: Optional[int] = Field(None, ge=1, le=6)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    professor_id: Optional[int] = None
    max_capacity: Optional[int] = Field(None, ge=1, le=500)
    prerequisites: Optional[List[str]] = None

    @field_validator('code')
    def validate_course_code(cls, v):
        if v is not None:
            pattern = r'^[A-Z]{2,4}\d{3}-\d{3}$'
            if not re.match(pattern, v):
                raise ValueError('Course code must follow format DEPT###-### (e.g., CS101-001)')
        return v


class ProfessorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the professor")
    email: EmailStr = Field(..., description="Valid email address")
    department: str = Field(..., min_length=1, max_length=50, description="Department")
    hire_date: date = Field(..., description="Date of hire")

    @field_validator('hire_date')
    def validate_hire_date(cls, v):
        if v > date.today():
            raise ValueError('Hire date cannot be in the future')
        if v < date(1950, 1, 1):
            raise ValueError('Hire date must be after 1950')
        return v


class Professor(ProfessorCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    current_teaching_load: int = Field(default=0, description="Number of courses currently teaching")


class ProfessorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    hire_date: Optional[date] = None

    @field_validator('hire_date')
    def validate_hire_date(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError('Hire date cannot be in the future')
            if v < date(1950, 1, 1):
                raise ValueError('Hire date must be after 1950')
        return v


class Grade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    F = "F"
    INCOMPLETE = "I"
    WITHDRAW = "W"


class EnrollmentCreate(BaseModel):
    student_id: int = Field(..., description="Student ID")
    course_id: int = Field(..., description="Course ID")
    enrollment_date: Optional[datetime] = Field(None, description="Enrollment date")

    @field_validator('enrollment_date')
    def validate_enrollment_date(cls, v):
        if v is not None and v > datetime.now():
            raise ValueError('Enrollment date cannot be in the future')
        return v


class Enrollment(EnrollmentCreate):
    enrollment_date: datetime = Field(default_factory=datetime.now)
    grade: Optional[Grade] = None


class EnrollmentUpdate(BaseModel):
    grade: Optional[Grade] = Field(None, description="Grade for the course")


# Response models for complex queries
class StudentWithCourses(Student):
    enrolled_courses: List[Course] = []
    total_credits: int = Field(default=0, description="Total credit hours enrolled")


class CourseWithStudents(Course):
    enrolled_students: List[Student] = []
    professor: Optional[Professor] = None


class ProfessorWithCourses(Professor):
    assigned_courses: List[Course] = []


# Utility models
class GradeUpdate(BaseModel):
    grade: Grade = Field(..., description="Grade to assign")


# Pagination models
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int


# Filter models
class StudentFilter(BaseModel):
    major: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=4)
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    max_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    on_probation: Optional[bool] = None


class CourseFilter(BaseModel):
    department: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=6)
    professor_id: Optional[int] = None
    has_capacity: Optional[bool] = None


class ProfessorFilter(BaseModel):
    department: Optional[str] = None
    hire_year: Optional[int] = Field(None, ge=1950, le=date.today().year)


# Bulk operation models
class BulkStudentCreate(BaseModel):
    students: List[StudentCreate] = Field(..., min_items=1, max_items=100)


class BulkEnrollmentCreate(BaseModel):
    enrollments: List[EnrollmentCreate] = Field(..., min_items=1, max_items=100)


class BulkGradeUpdate(BaseModel):
    grade_updates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)


# Analytics models
class GPADistribution(BaseModel):
    gpa_range: str
    count: int
    percentage: float


class EnrollmentStats(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    current_enrollment: int
    max_capacity: int
    utilization_rate: float


class TeachingLoad(BaseModel):
    professor_id: int
    professor_name: str
    department: str
    courses_count: int
    total_students: int


class DepartmentPerformance(BaseModel):
    department: str
    total_students: int
    average_gpa: float
    total_courses: int
    total_professors: int


# Error response models
class ValidationError(BaseModel):
    field: str
    message: str
    value: Any


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[List[ValidationError]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None


class ConflictError(BaseModel):
    error: str = "Conflict"
    message: str
    conflict_type: str
    existing_resource: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now) 