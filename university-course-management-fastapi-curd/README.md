# Enhanced University Course Management System - FastAPI

A comprehensive RESTful API for managing university students, courses, professors, and enrollments with advanced features including data validation, business rule enforcement, analytics, and bulk operations.

## 🚀 Features

### Core Functionality
- **Complete CRUD Operations** for Students, Courses, Professors, and Enrollments
- **Advanced Data Validation** using Pydantic models
- **Business Rule Enforcement** (capacity management, prerequisites, teaching loads)
- **Proper HTTP Status Codes** (200, 201, 204, 400, 404, 409, 422)
- **Comprehensive Error Handling** with detailed error responses

### Advanced Features
- **Pagination & Filtering** for all GET endpoints
- **Analytics Dashboard** with GPA distribution, enrollment stats, and performance metrics
- **Bulk Operations** for students, enrollments, and grade updates
- **Academic Business Rules** including probation status and credit limits
- **Email Uniqueness** validation across all entities
- **Automatic GPA Calculation** with probation status tracking

## 📋 Requirements

- Python 3.8+
- FastAPI
- Pydantic[email]
- Uvicorn

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd university-course-management-fastapi-curd
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🎯 Data Models & Validation

### Student Model
```json
{
  "name": "string (1-100 chars)",
  "email": "valid email format",
  "major": "string (1-50 chars)",
  "year": "integer (1-4)",
  "gpa": "float (0.0-4.0)",
  "is_on_probation": "boolean (auto-calculated)"
}
```

### Course Model
```json
{
  "name": "string (1-100 chars)",
  "code": "string (DEPT###-### format, e.g., CS101-001)",
  "credits": "integer (1-6)",
  "department": "string (1-50 chars)",
  "professor_id": "integer (optional)",
  "max_capacity": "integer (1-500)",
  "prerequisites": "array of course codes"
}
```

### Professor Model
```json
{
  "name": "string (1-100 chars)",
  "email": "valid email format",
  "department": "string (1-50 chars)",
  "hire_date": "date (not in future, after 1950)",
  "current_teaching_load": "integer (auto-calculated)"
}
```

## 🔧 API Endpoints

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students` | Create a new student |
| GET | `/students` | Get all students with pagination & filtering |
| GET | `/students/{id}` | Get specific student |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |
| GET | `/students/{id}/courses` | Get student's enrolled courses |

**Filtering Parameters:**
- `major`: Filter by major
- `year`: Filter by academic year (1-4)
- `min_gpa` / `max_gpa`: GPA range filtering
- `on_probation`: Filter by probation status

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/courses` | Create a new course |
| GET | `/courses` | Get all courses with pagination & filtering |
| GET | `/courses/{id}` | Get specific course with students |
| PUT | `/courses/{id}` | Update course |
| DELETE | `/courses/{id}` | Delete course |
| GET | `/courses/{id}/students` | Get course's enrolled students |

**Filtering Parameters:**
- `department`: Filter by department
- `credits`: Filter by credit hours
- `professor_id`: Filter by assigned professor
- `has_capacity`: Filter courses with available spots

### Professors

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/professors` | Create a new professor |
| GET | `/professors` | Get all professors with pagination & filtering |
| GET | `/professors/{id}` | Get specific professor with courses |
| PUT | `/professors/{id}` | Update professor |
| DELETE | `/professors/{id}` | Delete professor |

**Filtering Parameters:**
- `department`: Filter by department
- `hire_year`: Filter by hire year

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollments` | Create enrollment (with business rule validation) |
| GET | `/enrollments` | Get all enrollments with pagination |
| PUT | `/enrollments/{student_id}/{course_id}` | Update grade |
| DELETE | `/enrollments/{student_id}/{course_id}` | Drop student from course |

### Bulk Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students/bulk` | Create multiple students (max 100) |
| POST | `/enrollments/bulk` | Create multiple enrollments (max 100) |
| PUT | `/enrollments/grades/bulk` | Update multiple grades (max 100) |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/students/gpa-distribution` | GPA distribution across ranges |
| GET | `/analytics/courses/enrollment-stats` | Course enrollment statistics |
| GET | `/analytics/professors/teaching-load` | Professor teaching load stats |
| GET | `/analytics/departments/performance` | Department performance metrics |

## 🎨 Usage Examples

### Creating a Student
```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@student.edu",
    "major": "Computer Science",
    "year": 2,
    "gpa": 3.5
  }'
```

### Creating a Course with Prerequisites
```bash
curl -X POST "http://localhost:8000/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Structures",
    "code": "CS201-001",
    "credits": 4,
    "department": "Computer Science",
    "professor_id": 1,
    "max_capacity": 30,
    "prerequisites": ["CS101-001"]
  }'
```

### Filtering Students by Major and Probation Status
```bash
curl "http://localhost:8000/students?major=Computer%20Science&on_probation=true&page=1&limit=10"
```

### Bulk Student Creation
```bash
curl -X POST "http://localhost:8000/students/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "students": [
      {
        "name": "Alice Smith",
        "email": "alice@student.edu",
        "major": "Mathematics",
        "year": 1,
        "gpa": 3.8
      },
      {
        "name": "Bob Wilson",
        "email": "bob@student.edu", 
        "major": "Physics",
        "year": 2,
        "gpa": 3.2
      }
    ]
  }'
```

## 🔐 Business Rules & Validation

### Academic Rules
- **GPA Range**: 0.0 - 4.0
- **Academic Year**: 1-4 only
- **Academic Probation**: Automatic for GPA < 2.0
- **Credit Hour Limit**: Students cannot exceed 18 credits per semester
- **Course Capacity**: Enrollment rejected when capacity exceeded
- **Prerequisites**: Students must complete prerequisites before enrollment

### Professor Rules
- **Teaching Load**: Maximum 4 courses simultaneously
- **Hire Date**: Cannot be in the future or before 1950
- **Email Uniqueness**: Must be unique across all users

### Course Rules
- **Course Code Format**: Must follow DEPT###-### pattern (e.g., CS101-001)
- **Credit Hours**: 1-6 credits only
- **Capacity**: 1-500 students maximum

### Data Integrity
- **Email Uniqueness**: Enforced across students and professors
- **Enrollment Uniqueness**: Students cannot enroll in same course twice
- **Grade Calculation**: Automatic GPA recalculation on grade changes
- **Withdrawn Courses**: Excluded from GPA calculations

## 📊 HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET/PUT operations |
| 201 | Created | Successful POST operations |
| 204 | No Content | Successful DELETE operations |
| 400 | Bad Request | Invalid data/validation errors |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Business rule violations |
| 422 | Unprocessable Entity | Pydantic validation failures |

## 🚨 Error Response Format

```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": [
    {
      "field": "email",
      "message": "field required",
      "value": ""
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/students"
}
```

### Conflict Error Format
```json
{
  "error": "Conflict",
  "message": "Course is at maximum capacity (30)",
  "conflict_type": "capacity_exceeded",
  "existing_resource": {
    "course_id": 1,
    "current_enrollment": 30
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🧪 Testing

### Run the Test Suite
```bash
python test_api.py
```

The comprehensive test suite covers:
- ✅ API connectivity and health checks
- ✅ Data validation and error handling
- ✅ Business rule enforcement
- ✅ Email uniqueness constraints
- ✅ Course capacity management
- ✅ Prerequisite validation
- ✅ Professor teaching load limits
- ✅ Pagination and filtering
- ✅ Analytics endpoints
- ✅ Bulk operations
- ✅ Grade updates and GPA calculation

### Test Coverage
- **Validation Tests**: Invalid data formats, ranges, and constraints
- **Business Logic**: Enrollment conflicts, capacity limits, prerequisites
- **CRUD Operations**: Create, read, update, delete for all entities
- **Advanced Features**: Pagination, filtering, analytics, bulk operations
- **Error Handling**: Proper HTTP status codes and error messages

## 📈 Analytics & Reporting

### GPA Distribution
```json
[
  {
    "gpa_range": "4.0",
    "count": 12,
    "percentage": 15.38
  },
  {
    "gpa_range": "3.5-3.9", 
    "count": 25,
    "percentage": 32.05
  }
]
```

### Enrollment Statistics
```json
[
  {
    "course_id": 1,
    "course_name": "Introduction to Programming",
    "course_code": "CS101-001",
    "current_enrollment": 28,
    "max_capacity": 30,
    "utilization_rate": 93.33
  }
]
```

### Department Performance
```json
[
  {
    "department": "Computer Science",
    "total_students": 45,
    "average_gpa": 3.42,
    "total_courses": 8,
    "total_professors": 4
  }
]
```

## 🔄 Pagination

All list endpoints support pagination:

```
GET /students?page=1&limit=10
```

**Response Format:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 10,
  "pages": 15,
  "has_next": true,
  "has_prev": false
}
```

## 🎯 Key Improvements from Basic Version

### Enhanced Validation
- **Pydantic Field Validators**: Custom validation for course codes, dates, email formats
- **Business Rule Validation**: Prerequisites, capacity, teaching loads
- **Error Response Standardization**: Consistent error formats with detailed messages

### Advanced Features
- **Pagination & Filtering**: Efficient data retrieval with multiple filter options
- **Analytics Dashboard**: Real-time insights into academic performance and enrollment
- **Bulk Operations**: Efficient handling of large data sets
- **Automatic Calculations**: GPA recalculation and probation status updates

### Robust Architecture
- **Comprehensive Exception Handling**: Custom exceptions for different error types
- **HTTP Status Code Compliance**: Proper REST API conventions
- **Data Integrity**: Email uniqueness, enrollment constraints, capacity management
- **Academic Business Logic**: Real-world university rules and regulations

## 📝 Development Notes

### Database Design
- In-memory storage with dictionaries for simplicity
- Email tracking for uniqueness constraints
- Automatic ID generation and relationship management
- GPA calculation with grade point mapping

### Validation Strategy
- Pydantic models with custom validators
- Business rule checking at database layer
- Comprehensive error handling with detailed messages
- Type hints throughout for better code quality

### Testing Philosophy
- Comprehensive test coverage for all features
- Business rule validation testing
- Error scenario testing
- Real-world usage pattern simulation

## 🔮 Future Enhancements

- **Database Integration**: PostgreSQL or MongoDB support
- **Authentication & Authorization**: JWT-based user authentication
- **File Upload**: Student photo and document management
- **Notification System**: Email notifications for enrollment updates
- **Audit Logging**: Track all changes with timestamps and user information
- **Advanced Analytics**: Predictive modeling and trend analysis
- **API Rate Limiting**: Protection against abuse
- **Caching**: Redis integration for performance optimization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For questions or support, please open an issue in the repository or contact the development team.

---

**Enhanced University Course Management System** - Built with FastAPI, designed for academic excellence! 🎓 