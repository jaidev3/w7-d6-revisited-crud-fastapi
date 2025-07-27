from fastapi import FastAPI, HTTPException, status
from typing import List
from datetime import datetime

from models import (
    StudentCreate, Student, StudentUpdate, StudentWithCourses,
    CourseCreate, Course, CourseUpdate, CourseWithStudents,
    ProfessorCreate, Professor, ProfessorUpdate, ProfessorWithCourses,
    EnrollmentCreate, Enrollment, EnrollmentUpdate, Grade
)
from database import db

app = FastAPI(
    title="University Course Management System",
    description="A comprehensive RESTful API for managing university students, courses, professors, and enrollments",
    version="1.0.0"
)


# Student endpoints
@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    """Create a new student"""
    return db.create_student(student.dict())


@app.get("/students", response_model=List[Student])
def get_all_students():
    """Get all students"""
    return db.get_all_students()


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """Get a specific student by ID"""
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student_update: StudentUpdate):
    """Update a student's information"""
    update_data = student_update.dict(exclude_unset=True)
    updated_student = db.update_student(student_id, update_data)
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return updated_student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    """Delete a student"""
    if not db.delete_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )


@app.get("/students/{student_id}/courses", response_model=List[Course])
def get_student_courses(student_id: int):
    """Get all courses a student is enrolled in"""
    if not db.get_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return db.get_student_courses(student_id)


# Course endpoints
@app.post("/courses", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    """Create a new course"""
    # Validate professor exists if provided
    if course.professor_id and not db.get_professor(course.professor_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professor not found"
        )
    return db.create_course(course.dict())


@app.get("/courses", response_model=List[Course])
def get_all_courses():
    """Get all courses"""
    return db.get_all_courses()


@app.get("/courses/{course_id}", response_model=CourseWithStudents)
def get_course(course_id: int):
    """Get a specific course by ID with enrolled students and professor info"""
    course = db.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get enrolled students
    enrolled_students = db.get_course_students(course_id)
    
    # Get professor info
    professor = None
    if course.professor_id:
        professor = db.get_professor(course.professor_id)
    
    return CourseWithStudents(
        **course.dict(),
        enrolled_students=enrolled_students,
        professor=professor
    )


@app.put("/courses/{course_id}", response_model=Course)
def update_course(course_id: int, course_update: CourseUpdate):
    """Update a course's information"""
    # Validate professor exists if provided
    update_data = course_update.dict(exclude_unset=True)
    if "professor_id" in update_data and update_data["professor_id"] and not db.get_professor(update_data["professor_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professor not found"
        )
    
    updated_course = db.update_course(course_id, update_data)
    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return updated_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int):
    """Delete a course"""
    if not db.delete_course(course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )


@app.get("/courses/{course_id}/students", response_model=List[Student])
def get_course_students(course_id: int):
    """Get all students enrolled in a course"""
    if not db.get_course(course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return db.get_course_students(course_id)


# Professor endpoints
@app.post("/professors", response_model=Professor, status_code=status.HTTP_201_CREATED)
def create_professor(professor: ProfessorCreate):
    """Create a new professor"""
    return db.create_professor(professor.dict())


@app.get("/professors", response_model=List[Professor])
def get_all_professors():
    """Get all professors"""
    return db.get_all_professors()


@app.get("/professors/{professor_id}", response_model=ProfessorWithCourses)
def get_professor(professor_id: int):
    """Get a specific professor by ID with assigned courses"""
    professor = db.get_professor(professor_id)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor not found"
        )
    
    assigned_courses = db.get_professor_courses(professor_id)
    
    return ProfessorWithCourses(
        **professor.dict(),
        assigned_courses=assigned_courses
    )


@app.put("/professors/{professor_id}", response_model=Professor)
def update_professor(professor_id: int, professor_update: ProfessorUpdate):
    """Update a professor's information"""
    update_data = professor_update.dict(exclude_unset=True)
    updated_professor = db.update_professor(professor_id, update_data)
    if not updated_professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor not found"
        )
    return updated_professor


@app.delete("/professors/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: int):
    """Delete a professor"""
    if not db.delete_professor(professor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor not found"
        )


# Enrollment endpoints
@app.post("/enrollments", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: EnrollmentCreate):
    """Enroll a student in a course"""
    # Check if student exists
    if not db.get_student(enrollment.student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if course exists
    course = db.get_course(enrollment.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    if db.get_enrollment(enrollment.student_id, enrollment.course_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this course"
        )
    
    # Check course capacity
    if course.current_enrollment >= course.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is at maximum capacity"
        )
    
    new_enrollment = db.create_enrollment(enrollment.student_id, enrollment.course_id)
    if not new_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create enrollment"
        )
    
    return new_enrollment


@app.get("/enrollments", response_model=List[Enrollment])
def get_all_enrollments():
    """Get all enrollments"""
    return db.get_all_enrollments()


@app.put("/enrollments/{student_id}/{course_id}", response_model=Enrollment)
def update_enrollment_grade(student_id: int, course_id: int, grade_update: EnrollmentUpdate):
    """Update a student's grade for a course"""
    if not grade_update.grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade is required"
        )
    
    enrollment = db.get_enrollment(student_id, course_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    updated_enrollment = db.update_enrollment(student_id, course_id, grade_update.grade)
    return updated_enrollment


@app.delete("/enrollments/{student_id}/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(student_id: int, course_id: int):
    """Drop a student from a course"""
    if not db.delete_enrollment(student_id, course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )


# Root endpoint
@app.get("/")
def read_root():
    """Welcome message and API information"""
    return {
        "message": "Welcome to the University Course Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 