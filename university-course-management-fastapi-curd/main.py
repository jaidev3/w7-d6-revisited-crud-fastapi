from fastapi import FastAPI, HTTPException, status, Query, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import math

from models import (
    StudentCreate, Student, StudentUpdate, StudentWithCourses,
    CourseCreate, Course, CourseUpdate, CourseWithStudents,
    ProfessorCreate, Professor, ProfessorUpdate, ProfessorWithCourses,
    EnrollmentCreate, Enrollment, EnrollmentUpdate, Grade,
    PaginationParams, PaginatedResponse, StudentFilter, CourseFilter, ProfessorFilter,
    BulkStudentCreate, BulkEnrollmentCreate, BulkGradeUpdate,
    GPADistribution, EnrollmentStats, TeachingLoad, DepartmentPerformance,
    ErrorResponse, ConflictError as ConflictErrorModel, ValidationError
)
from database import db, ConflictError, DatabaseError

app = FastAPI(
    title="Enhanced University Course Management System",
    description="A comprehensive RESTful API for managing university students, courses, professors, and enrollments with advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with 422 status"""
    errors = []
    for error in exc.errors():
        errors.append(ValidationError(
            field=".".join(str(x) for x in error["loc"]),
            message=error["msg"],
            value=error.get("input", "")
        ))
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            message="Request validation failed",
            details=errors,
            path=str(request.url.path)
        ).dict()
    )


@app.exception_handler(ConflictError)
async def conflict_exception_handler(request: Request, exc: ConflictError):
    """Handle business rule conflicts with 409 status"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ConflictErrorModel(
            message=exc.message,
            conflict_type=exc.conflict_type,
            existing_resource=exc.existing_resource
        ).dict()
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle database errors with 400 status"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="Database Error",
            message=str(exc),
            path=str(request.url.path)
        ).dict()
    )


# Helper functions
def create_paginated_response(items: List[Any], total: int, page: int, limit: int) -> Dict[str, Any]:
    """Create paginated response structure"""
    pages = math.ceil(total / limit) if limit > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1
    }


# Student endpoints
@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED,
          summary="Create a new student",
          description="Create a new student with validation for email uniqueness, GPA range, and academic year")
def create_student(student: StudentCreate):
    """Create a new student"""
    try:
        return db.create_student(student.dict())
    except ConflictError:
        raise  # Re-raise to be handled by exception handler


@app.get("/students", response_model=Dict[str, Any], status_code=status.HTTP_200_OK,
         summary="Get all students with filtering and pagination",
         description="Retrieve students with optional filtering by major, year, GPA range, and probation status")
def get_all_students(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    major: Optional[str] = Query(None, description="Filter by major"),
    year: Optional[int] = Query(None, ge=1, le=4, description="Filter by academic year"),
    min_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Minimum GPA"),
    max_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Maximum GPA"),
    on_probation: Optional[bool] = Query(None, description="Filter by probation status")
):
    """Get all students with filtering and pagination"""
    filters = {
        "major": major,
        "year": year,
        "min_gpa": min_gpa,
        "max_gpa": max_gpa,
        "on_probation": on_probation
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    students, total = db.get_all_students(filters=filters, page=page, limit=limit)
    return create_paginated_response(students, total, page, limit)


@app.get("/students/{student_id}", response_model=Student, status_code=status.HTTP_200_OK,
         summary="Get a specific student",
         description="Retrieve a student by ID with full details")
def get_student(student_id: int):
    """Get a specific student by ID"""
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    return student


@app.put("/students/{student_id}", response_model=Student, status_code=status.HTTP_200_OK,
         summary="Update a student",
         description="Update student information with validation")
def update_student(student_id: int, student_update: StudentUpdate):
    """Update a student's information"""
    update_data = student_update.dict(exclude_unset=True)
    try:
        updated_student = db.update_student(student_id, update_data)
        if not updated_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
        return updated_student
    except ConflictError:
        raise  # Re-raise to be handled by exception handler


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a student",
            description="Delete a student and all associated enrollments")
def delete_student(student_id: int):
    """Delete a student"""
    if not db.delete_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )


@app.get("/students/{student_id}/courses", response_model=List[Course], status_code=status.HTTP_200_OK,
         summary="Get student's enrolled courses",
         description="Get all courses a student is enrolled in")
def get_student_courses(student_id: int):
    """Get all courses a student is enrolled in"""
    if not db.get_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    return db.get_student_courses(student_id)


# Course endpoints
@app.post("/courses", response_model=Course, status_code=status.HTTP_201_CREATED,
          summary="Create a new course",
          description="Create a new course with validation for course code format and professor teaching load")
def create_course(course: CourseCreate):
    """Create a new course"""
    # Validate professor exists and teaching load if provided
    if course.professor_id:
        if not db.get_professor(course.professor_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Professor with ID {course.professor_id} not found"
            )
        if not db.validate_professor_teaching_load(course.professor_id, 1):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Professor cannot teach more than 4 courses simultaneously"
            )
    
    return db.create_course(course.dict())


@app.get("/courses", response_model=Dict[str, Any], status_code=status.HTTP_200_OK,
         summary="Get all courses with filtering and pagination",
         description="Retrieve courses with optional filtering by department, credits, professor, and capacity")
def get_all_courses(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    credits: Optional[int] = Query(None, ge=1, le=6, description="Filter by credit hours"),
    professor_id: Optional[int] = Query(None, description="Filter by professor ID"),
    has_capacity: Optional[bool] = Query(None, description="Filter courses with available capacity")
):
    """Get all courses with filtering and pagination"""
    filters = {
        "department": department,
        "credits": credits,
        "professor_id": professor_id,
        "has_capacity": has_capacity
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    courses, total = db.get_all_courses(filters=filters, page=page, limit=limit)
    return create_paginated_response(courses, total, page, limit)


@app.get("/courses/{course_id}", response_model=CourseWithStudents, status_code=status.HTTP_200_OK,
         summary="Get a specific course with details",
         description="Retrieve a course by ID with enrolled students and professor information")
def get_course(course_id: int):
    """Get a specific course by ID with enrolled students and professor info"""
    course = db.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
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


@app.put("/courses/{course_id}", response_model=Course, status_code=status.HTTP_200_OK,
         summary="Update a course",
         description="Update course information with validation")
def update_course(course_id: int, course_update: CourseUpdate):
    """Update a course's information"""
    # Validate professor exists and teaching load if provided
    update_data = course_update.dict(exclude_unset=True)
    if "professor_id" in update_data and update_data["professor_id"]:
        if not db.get_professor(update_data["professor_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Professor with ID {update_data['professor_id']} not found"
            )
        # Check if this would exceed teaching load (excluding current assignment)
        current_course = db.get_course(course_id)
        if current_course and current_course.professor_id != update_data["professor_id"]:
            if not db.validate_professor_teaching_load(update_data["professor_id"], 1):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Professor cannot teach more than 4 courses simultaneously"
                )
    
    updated_course = db.update_course(course_id, update_data)
    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return updated_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a course",
            description="Delete a course and all associated enrollments")
def delete_course(course_id: int):
    """Delete a course"""
    if not db.delete_course(course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )


@app.get("/courses/{course_id}/students", response_model=List[Student], status_code=status.HTTP_200_OK,
         summary="Get course's enrolled students",
         description="Get all students enrolled in a course")
def get_course_students(course_id: int):
    """Get all students enrolled in a course"""
    if not db.get_course(course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return db.get_course_students(course_id)


# Professor endpoints
@app.post("/professors", response_model=Professor, status_code=status.HTTP_201_CREATED,
          summary="Create a new professor",
          description="Create a new professor with validation for email uniqueness and hire date")
def create_professor(professor: ProfessorCreate):
    """Create a new professor"""
    try:
        return db.create_professor(professor.dict())
    except ConflictError:
        raise  # Re-raise to be handled by exception handler


@app.get("/professors", response_model=Dict[str, Any], status_code=status.HTTP_200_OK,
         summary="Get all professors with filtering and pagination",
         description="Retrieve professors with optional filtering by department and hire year")
def get_all_professors(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    hire_year: Optional[int] = Query(None, ge=1950, description="Filter by hire year")
):
    """Get all professors with filtering and pagination"""
    filters = {
        "department": department,
        "hire_year": hire_year
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    professors, total = db.get_all_professors(filters=filters, page=page, limit=limit)
    return create_paginated_response(professors, total, page, limit)


@app.get("/professors/{professor_id}", response_model=ProfessorWithCourses, status_code=status.HTTP_200_OK,
         summary="Get a specific professor with courses",
         description="Retrieve a professor by ID with assigned courses")
def get_professor(professor_id: int):
    """Get a specific professor by ID with assigned courses"""
    professor = db.get_professor(professor_id)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with ID {professor_id} not found"
        )
    
    assigned_courses = db.get_professor_courses(professor_id)
    
    return ProfessorWithCourses(
        **professor.dict(),
        assigned_courses=assigned_courses
    )


@app.put("/professors/{professor_id}", response_model=Professor, status_code=status.HTTP_200_OK,
         summary="Update a professor",
         description="Update professor information with validation")
def update_professor(professor_id: int, professor_update: ProfessorUpdate):
    """Update a professor's information"""
    update_data = professor_update.dict(exclude_unset=True)
    try:
        updated_professor = db.update_professor(professor_id, update_data)
        if not updated_professor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Professor with ID {professor_id} not found"
            )
        return updated_professor
    except ConflictError:
        raise  # Re-raise to be handled by exception handler


@app.delete("/professors/{professor_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a professor",
            description="Delete a professor and unassign from all courses")
def delete_professor(professor_id: int):
    """Delete a professor"""
    if not db.delete_professor(professor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with ID {professor_id} not found"
        )


# Enrollment endpoints
@app.post("/enrollments", response_model=Enrollment, status_code=status.HTTP_201_CREATED,
          summary="Create a new enrollment",
          description="Enroll a student in a course with business rule validation")
def create_enrollment(enrollment: EnrollmentCreate):
    """Enroll a student in a course"""
    # Check if student exists
    if not db.get_student(enrollment.student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {enrollment.student_id} not found"
        )
    
    # Check if course exists
    course = db.get_course(enrollment.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {enrollment.course_id} not found"
        )
    
    # Check if already enrolled
    if db.get_enrollment(enrollment.student_id, enrollment.course_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student is already enrolled in this course"
        )
    
    try:
        new_enrollment = db.create_enrollment(enrollment.student_id, enrollment.course_id)
        if not new_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create enrollment"
            )
        return new_enrollment
    except ConflictError:
        raise  # Re-raise to be handled by exception handler


@app.get("/enrollments", response_model=Dict[str, Any], status_code=status.HTTP_200_OK,
         summary="Get all enrollments with pagination",
         description="Retrieve all enrollments with pagination")
def get_all_enrollments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get all enrollments with pagination"""
    enrollments, total = db.get_all_enrollments(page=page, limit=limit)
    return create_paginated_response(enrollments, total, page, limit)


@app.put("/enrollments/{student_id}/{course_id}", response_model=Enrollment, status_code=status.HTTP_200_OK,
         summary="Update enrollment grade",
         description="Update a student's grade for a course")
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
            detail=f"Enrollment not found for student {student_id} and course {course_id}"
        )
    
    updated_enrollment = db.update_enrollment(student_id, course_id, grade_update.grade)
    return updated_enrollment


@app.delete("/enrollments/{student_id}/{course_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete an enrollment",
            description="Drop a student from a course")
def delete_enrollment(student_id: int, course_id: int):
    """Drop a student from a course"""
    if not db.delete_enrollment(student_id, course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment not found for student {student_id} and course {course_id}"
        )


# Bulk operations endpoints
@app.post("/students/bulk", response_model=List[Student], status_code=status.HTTP_201_CREATED,
          summary="Create multiple students",
          description="Create multiple students in bulk (max 100)")
def bulk_create_students(bulk_data: BulkStudentCreate):
    """Create multiple students in bulk"""
    try:
        return db.bulk_create_students([student.dict() for student in bulk_data.students])
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/enrollments/bulk", response_model=List[Enrollment], status_code=status.HTTP_201_CREATED,
          summary="Create multiple enrollments",
          description="Create multiple enrollments in bulk (max 100)")
def bulk_create_enrollments(bulk_data: BulkEnrollmentCreate):
    """Create multiple enrollments in bulk"""
    try:
        return db.bulk_create_enrollments([enrollment.dict() for enrollment in bulk_data.enrollments])
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.put("/enrollments/grades/bulk", response_model=List[Enrollment], status_code=status.HTTP_200_OK,
         summary="Update multiple grades",
         description="Update multiple grades in bulk (max 100)")
def bulk_update_grades(bulk_data: BulkGradeUpdate):
    """Update multiple grades in bulk"""
    try:
        return db.bulk_update_grades(bulk_data.grade_updates)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Analytics endpoints
@app.get("/analytics/students/gpa-distribution", response_model=List[GPADistribution], status_code=status.HTTP_200_OK,
         summary="Get GPA distribution analytics",
         description="Get student GPA distribution across different ranges")
def get_gpa_distribution():
    """Get GPA distribution analytics"""
    return db.get_gpa_distribution()


@app.get("/analytics/courses/enrollment-stats", response_model=List[EnrollmentStats], status_code=status.HTTP_200_OK,
         summary="Get course enrollment statistics",
         description="Get enrollment statistics for all courses")
def get_enrollment_stats():
    """Get course enrollment statistics"""
    return db.get_enrollment_stats()


@app.get("/analytics/professors/teaching-load", response_model=List[TeachingLoad], status_code=status.HTTP_200_OK,
         summary="Get professor teaching load statistics",
         description="Get teaching load statistics for all professors")
def get_teaching_load_stats():
    """Get professor teaching load statistics"""
    return db.get_teaching_load_stats()


@app.get("/analytics/departments/performance", response_model=List[DepartmentPerformance], status_code=status.HTTP_200_OK,
         summary="Get department performance analytics",
         description="Get performance analytics for all departments")
def get_department_performance():
    """Get department performance analytics"""
    return db.get_department_performance()


# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK,
         summary="API information",
         description="Get API information and status")
def read_root():
    """Welcome message and API information"""
    return {
        "message": "Welcome to the Enhanced University Course Management System API",
        "version": "2.0.0",
        "features": [
            "Comprehensive data validation",
            "Business rule enforcement",
            "Pagination and filtering",
            "Advanced analytics",
            "Bulk operations",
            "Proper HTTP status codes",
            "Error handling"
        ],
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.now().isoformat()
    }


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK,
         summary="Health check",
         description="Check API health status")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "students": len(db.students),
            "courses": len(db.courses),
            "professors": len(db.professors),
            "enrollments": len(db.enrollments)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 