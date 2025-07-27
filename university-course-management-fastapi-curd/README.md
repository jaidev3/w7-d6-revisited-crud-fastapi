# University Course Management System - FastAPI CRUD

A comprehensive RESTful API for managing university students, courses, professors, and enrollments built with FastAPI and in-memory dictionary-based storage.

## Features

- **Complete CRUD Operations** for Students, Courses, Professors, and Enrollments
- **Automatic GPA Calculation** based on course grades
- **Course Capacity Management** with enrollment limits
- **Business Logic Validation** (prevent duplicate enrollments, capacity checking, etc.)
- **Cascading Operations** (proper handling of deletions)
- **Comprehensive API Documentation** with OpenAPI/Swagger
- **Data Validation** with Pydantic models

## Entities

### Students
- ID, name, email, major, year, GPA
- Automatic GPA calculation based on course grades

### Courses
- ID, name, code, credits, professor_id, max_capacity
- Current enrollment tracking

### Professors
- ID, name, email, department, hire_date
- Course assignment tracking

### Enrollments
- student_id, course_id, enrollment_date, grade
- Grade-based GPA calculation

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd university-course-management-fastapi-curd
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

## API Endpoints

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students` | Create new student |
| GET | `/students` | Get all students |
| GET | `/students/{id}` | Get specific student |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |
| GET | `/students/{id}/courses` | Get student's courses |

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/courses` | Create new course |
| GET | `/courses` | Get all courses |
| GET | `/courses/{id}` | Get specific course with students and professor |
| PUT | `/courses/{id}` | Update course |
| DELETE | `/courses/{id}` | Delete course |
| GET | `/courses/{id}/students` | Get course roster |

### Professors

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/professors` | Create new professor |
| GET | `/professors` | Get all professors |
| GET | `/professors/{id}` | Get specific professor with assigned courses |
| PUT | `/professors/{id}` | Update professor |
| DELETE | `/professors/{id}` | Delete professor |

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollments` | Enroll student in course |
| GET | `/enrollments` | Get all enrollments |
| PUT | `/enrollments/{student_id}/{course_id}` | Update grade |
| DELETE | `/enrollments/{student_id}/{course_id}` | Drop course |

## Sample Usage

### Create a Professor
```bash
curl -X POST "http://localhost:8000/professors" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Dr. Jane Smith",
       "email": "jane.smith@university.edu",
       "department": "Computer Science",
       "hire_date": "2020-08-15"
     }'
```

### Create a Course
```bash
curl -X POST "http://localhost:8000/courses" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Introduction to Programming",
       "code": "CS101",
       "credits": 3,
       "professor_id": 1,
       "max_capacity": 30
     }'
```

### Create a Student
```bash
curl -X POST "http://localhost:8000/students" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john.doe@student.university.edu",
       "major": "Computer Science",
       "year": 1
     }'
```

### Enroll Student in Course
```bash
curl -X POST "http://localhost:8000/enrollments" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": 1,
       "course_id": 1
     }'
```

### Update Grade
```bash
curl -X PUT "http://localhost:8000/enrollments/1/1" \
     -H "Content-Type: application/json" \
     -d '{
       "grade": "A"
     }'
```

## Business Logic

### Course Enrollment Rules
- Students cannot enroll in the same course twice
- Courses have maximum capacity limits
- Enrollment is prevented if course is at capacity

### GPA Calculation
- Automatically calculated when grades are updated
- Based on standard 4.0 scale:
  - A+/A: 4.0, A-: 3.7
  - B+: 3.3, B: 3.0, B-: 2.7
  - C+: 2.3, C: 2.0, C-: 1.7
  - D+: 1.3, D: 1.0, F: 0.0

### Cascading Operations
- Deleting a student removes all their enrollments
- Deleting a course removes all enrollments for that course
- Deleting a professor unassigns them from all courses (courses remain)

## Data Models

### Grade System
Available grades: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, F, I (Incomplete), W (Withdraw)

### Validation Rules
- Student year: 1-8 (supports various degree programs)
- Course credits: 1-6
- GPA: 0.0-4.0
- Email validation for students and professors
- Name and code length restrictions

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:
- **400 Bad Request**: Invalid data, capacity exceeded, duplicate enrollments
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **In-Memory Storage**: Dictionary-based database for simplicity
- **Modular Design**: Separate models, database, and main application files

## Future Enhancements

- Persistent database integration (PostgreSQL, MongoDB)
- Authentication and authorization
- Advanced reporting and analytics
- Email notifications
- Course prerequisites management
- Semester/term management
- Grade history tracking

## Development

To extend the application:

1. **Models**: Add new Pydantic models in `models.py`
2. **Database**: Extend database operations in `database.py`
3. **Endpoints**: Add new API endpoints in `main.py`

## Testing

Use the interactive API documentation at `/docs` to test all endpoints, or use tools like Postman, curl, or write automated tests with pytest.

## License

This project is open source and available under the MIT License. 