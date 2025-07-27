from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    major: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1, le=8)  # 1-8 years for various degree programs
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class Student(StudentCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    major: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1, le=8)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=3, max_length=10)
    credits: int = Field(..., ge=1, le=6)
    professor_id: Optional[int] = None
    max_capacity: int = Field(..., ge=1, le=500)


class Course(CourseCreate):
    id: int
    current_enrollment: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=3, max_length=10)
    credits: Optional[int] = Field(None, ge=1, le=6)
    professor_id: Optional[int] = None
    max_capacity: Optional[int] = Field(None, ge=1, le=500)


class ProfessorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=50)
    hire_date: date


class Professor(ProfessorCreate):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)


class ProfessorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    hire_date: Optional[date] = None


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
    student_id: int
    course_id: int


class Enrollment(EnrollmentCreate):
    enrollment_date: datetime = Field(default_factory=datetime.now)
    grade: Optional[Grade] = None


class EnrollmentUpdate(BaseModel):
    grade: Optional[Grade] = None


# Response models for complex queries
class StudentWithCourses(Student):
    enrolled_courses: List[Course] = []


class CourseWithStudents(Course):
    enrolled_students: List[Student] = []
    professor: Optional[Professor] = None


class ProfessorWithCourses(Professor):
    assigned_courses: List[Course] = []


# Utility models
class GradeUpdate(BaseModel):
    grade: Grade 