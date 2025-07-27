"""
Comprehensive Test Suite for Enhanced University Course Management System API
This script tests all CRUD operations, validation, business rules, pagination, 
filtering, analytics, and bulk operations.
"""

import requests
import json
from datetime import date, datetime
from typing import Dict, List, Any
import time


class EnhancedUniversityAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_data = {
            "professor_ids": [],
            "student_ids": [],
            "course_ids": []
        }
    
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, passed: bool = True, details: str = ""):
        """Print test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
    
    def test_connection(self) -> bool:
        """Test if the API is running"""
        self.print_section("API CONNECTION TEST")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.print_test("API Connection", True, f"Version: {data.get('version', 'Unknown')}")
                return True
            else:
                self.print_test("API Connection", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("API Connection", False, "Cannot connect to API. Make sure server is running")
            return False
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        self.print_section("HEALTH CHECK")
        response = self.session.get(f"{self.base_url}/health")
        if response.status_code == 200:
            data = response.json()
            self.print_test("Health Check", True, f"Status: {data.get('status')}")
            print(f"    Database counts: {data.get('database', {})}")
        else:
            self.print_test("Health Check", False, f"Status: {response.status_code}")
    
    def test_validation_errors(self):
        """Test Pydantic validation and error handling"""
        self.print_section("VALIDATION & ERROR HANDLING TESTS")
        
        # Test invalid student data
        invalid_student = {
            "name": "",  # Too short
            "email": "invalid-email",  # Invalid format
            "major": "",  # Too short
            "year": 5,  # Out of range
            "gpa": 5.0  # Out of range
        }
        
        response = self.session.post(f"{self.base_url}/students", 
                                   data=json.dumps(invalid_student))
        
        if response.status_code == 422:
            self.print_test("Validation Error Handling", True, "422 Unprocessable Entity returned")
            error_data = response.json()
            print(f"    Error details: {len(error_data.get('details', []))} validation errors")
        else:
            self.print_test("Validation Error Handling", False, f"Expected 422, got {response.status_code}")
        
        # Test invalid course code format
        invalid_course = {
            "name": "Test Course",
            "code": "INVALID",  # Wrong format
            "credits": 3,
            "department": "CS",
            "max_capacity": 30
        }
        
        response = self.session.post(f"{self.base_url}/courses", 
                                   data=json.dumps(invalid_course))
        
        if response.status_code == 422:
            self.print_test("Course Code Validation", True, "Invalid course code rejected")
        else:
            self.print_test("Course Code Validation", False, f"Expected 422, got {response.status_code}")
        
        # Test future hire date
        invalid_professor = {
            "name": "Future Prof",
            "email": "future@test.edu",
            "department": "CS",
            "hire_date": "2030-01-01"  # Future date
        }
        
        response = self.session.post(f"{self.base_url}/professors", 
                                   data=json.dumps(invalid_professor))
        
        if response.status_code == 422:
            self.print_test("Hire Date Validation", True, "Future hire date rejected")
        else:
            self.print_test("Hire Date Validation", False, f"Expected 422, got {response.status_code}")
    
    def create_test_professors(self) -> List[int]:
        """Create test professors"""
        self.print_section("CREATING TEST PROFESSORS")
        
        professors = [
            {
                "name": "Dr. Alice Johnson",
                "email": "alice.johnson@university.edu",
                "department": "Computer Science",
                "hire_date": "2018-08-15"
            },
            {
                "name": "Prof. Bob Smith",
                "email": "bob.smith@university.edu",
                "department": "Mathematics",
                "hire_date": "2015-01-20"
            },
            {
                "name": "Dr. Carol Davis",
                "email": "carol.davis@university.edu",
                "department": "Physics",
                "hire_date": "2020-09-01"
            },
            {
                "name": "Dr. David Wilson",
                "email": "david.wilson@university.edu",
                "department": "Computer Science",
                "hire_date": "2019-06-10"
            }
        ]
        
        professor_ids = []
        for i, prof in enumerate(professors):
            response = self.session.post(f"{self.base_url}/professors", 
                                       data=json.dumps(prof))
            if response.status_code == 201:
                created_prof = response.json()
                professor_ids.append(created_prof['id'])
                self.print_test(f"Professor {i+1} Created", True, 
                              f"{created_prof['name']} (ID: {created_prof['id']})")
            else:
                self.print_test(f"Professor {i+1} Created", False, 
                              f"Status: {response.status_code}")
        
        self.test_data["professor_ids"] = professor_ids
        return professor_ids
    
    def test_email_uniqueness(self):
        """Test email uniqueness constraint"""
        self.print_section("EMAIL UNIQUENESS TESTS")
        
        if not self.test_data["professor_ids"]:
            self.print_test("Email Uniqueness", False, "No professors created for test")
            return
        
        # Try to create professor with duplicate email
        duplicate_prof = {
            "name": "Duplicate Prof",
            "email": "alice.johnson@university.edu",  # Same as first professor
            "department": "Math",
            "hire_date": "2021-01-01"
        }
        
        response = self.session.post(f"{self.base_url}/professors", 
                                   data=json.dumps(duplicate_prof))
        
        if response.status_code == 409:
            self.print_test("Professor Email Uniqueness", True, "409 Conflict returned")
        else:
            self.print_test("Professor Email Uniqueness", False, 
                          f"Expected 409, got {response.status_code}")
    
    def create_test_courses(self) -> List[int]:
        """Create test courses"""
        self.print_section("CREATING TEST COURSES")
        
        professor_ids = self.test_data["professor_ids"]
        
        courses = [
            {
                "name": "Introduction to Programming",
                "code": "CS101-001",
                "credits": 3,
                "department": "Computer Science",
                "professor_id": professor_ids[0] if professor_ids else None,
                "max_capacity": 5,  # Small capacity for testing
                "prerequisites": []
            },
            {
                "name": "Data Structures",
                "code": "CS201-001",
                "credits": 4,
                "department": "Computer Science",
                "professor_id": professor_ids[0] if professor_ids else None,
                "max_capacity": 3,
                "prerequisites": ["CS101-001"]
            },
            {
                "name": "Calculus I",
                "code": "MATH101-001",
                "credits": 4,
                "department": "Mathematics",
                "professor_id": professor_ids[1] if len(professor_ids) > 1 else None,
                "max_capacity": 4,
                "prerequisites": []
            },
            {
                "name": "Algorithms",
                "code": "CS301-001",
                "credits": 3,
                "department": "Computer Science",
                "professor_id": professor_ids[3] if len(professor_ids) > 3 else None,
                "max_capacity": 2,
                "prerequisites": ["CS201-001"]
            }
        ]
        
        course_ids = []
        for i, course in enumerate(courses):
            response = self.session.post(f"{self.base_url}/courses", 
                                       data=json.dumps(course))
            if response.status_code == 201:
                created_course = response.json()
                course_ids.append(created_course['id'])
                self.print_test(f"Course {i+1} Created", True, 
                              f"{created_course['name']} (ID: {created_course['id']})")
            else:
                self.print_test(f"Course {i+1} Created", False, 
                              f"Status: {response.status_code}")
        
        self.test_data["course_ids"] = course_ids
        return course_ids
    
    def test_professor_teaching_load(self):
        """Test professor teaching load restriction"""
        self.print_section("PROFESSOR TEACHING LOAD TESTS")
        
        if not self.test_data["professor_ids"]:
            self.print_test("Teaching Load Test", False, "No professors available")
            return
        
        professor_id = self.test_data["professor_ids"][0]
        
        # Try to assign more courses to exceed limit
        excess_courses = [
            {
                "name": "Extra Course 1",
                "code": "CS401-001",
                "credits": 3,
                "department": "Computer Science",
                "professor_id": professor_id,
                "max_capacity": 30
            },
            {
                "name": "Extra Course 2", 
                "code": "CS402-001",
                "credits": 3,
                "department": "Computer Science",
                "professor_id": professor_id,
                "max_capacity": 30
            }
        ]
        
        conflicts = 0
        for course in excess_courses:
            response = self.session.post(f"{self.base_url}/courses", 
                                       data=json.dumps(course))
            if response.status_code == 409:
                conflicts += 1
        
        if conflicts > 0:
            self.print_test("Teaching Load Restriction", True, 
                          f"{conflicts} courses rejected due to teaching load limit")
        else:
            self.print_test("Teaching Load Restriction", False, 
                          "No teaching load restrictions enforced")
    
    def create_test_students(self) -> List[int]:
        """Create test students"""
        self.print_section("CREATING TEST STUDENTS")
        
        students = [
            {
                "name": "John Doe",
                "email": "john.doe@student.edu",
                "major": "Computer Science",
                "year": 2,
                "gpa": 3.5
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@student.edu",
                "major": "Computer Science", 
                "year": 3,
                "gpa": 3.8
            },
            {
                "name": "Bob Wilson",
                "email": "bob.wilson@student.edu",
                "major": "Mathematics",
                "year": 1,
                "gpa": 2.9
            },
            {
                "name": "Alice Brown",
                "email": "alice.brown@student.edu",
                "major": "Physics",
                "year": 4,
                "gpa": 1.8  # Below 2.0 for probation test
            },
            {
                "name": "Charlie Davis",
                "email": "charlie.davis@student.edu",
                "major": "Computer Science",
                "year": 2,
                "gpa": 3.2
            }
        ]
        
        student_ids = []
        for i, student in enumerate(students):
            response = self.session.post(f"{self.base_url}/students", 
                                       data=json.dumps(student))
            if response.status_code == 201:
                created_student = response.json()
                student_ids.append(created_student['id'])
                probation_status = "ON PROBATION" if created_student.get('is_on_probation') else "GOOD STANDING"
                self.print_test(f"Student {i+1} Created", True, 
                              f"{created_student['name']} (ID: {created_student['id']}) - {probation_status}")
            else:
                self.print_test(f"Student {i+1} Created", False, 
                              f"Status: {response.status_code}")
        
        self.test_data["student_ids"] = student_ids
        return student_ids
    
    def test_enrollment_business_rules(self):
        """Test enrollment business rules"""
        self.print_section("ENROLLMENT BUSINESS RULES TESTS")
        
        student_ids = self.test_data["student_ids"]
        course_ids = self.test_data["course_ids"]
        
        if not student_ids or not course_ids:
            self.print_test("Business Rules Test", False, "Missing students or courses")
            return
        
        # Test normal enrollment
        enrollment_data = {
            "student_id": student_ids[0],
            "course_id": course_ids[0]  # CS101
        }
        
        response = self.session.post(f"{self.base_url}/enrollments", 
                                   data=json.dumps(enrollment_data))
        
        if response.status_code == 201:
            self.print_test("Normal Enrollment", True, "Student enrolled successfully")
        else:
            self.print_test("Normal Enrollment", False, f"Status: {response.status_code}")
        
        # Test duplicate enrollment
        response = self.session.post(f"{self.base_url}/enrollments", 
                                   data=json.dumps(enrollment_data))
        
        if response.status_code == 409:
            self.print_test("Duplicate Enrollment Prevention", True, "409 Conflict returned")
        else:
            self.print_test("Duplicate Enrollment Prevention", False, 
                          f"Expected 409, got {response.status_code}")
        
        # Test prerequisite checking (try to enroll in CS201 without CS101 completion)
        prereq_enrollment = {
            "student_id": student_ids[1],
            "course_id": course_ids[1]  # CS201 (requires CS101)
        }
        
        response = self.session.post(f"{self.base_url}/enrollments", 
                                   data=json.dumps(prereq_enrollment))
        
        if response.status_code == 409:
            self.print_test("Prerequisite Checking", True, "Prerequisites enforced")
        else:
            self.print_test("Prerequisite Checking", False, 
                          f"Expected 409, got {response.status_code}")
        
        # Fill up course capacity
        capacity_course_id = course_ids[2]  # MATH101 with capacity 4
        enrollments_created = 0
        
        for i in range(len(student_ids)):
            enroll_data = {
                "student_id": student_ids[i],
                "course_id": capacity_course_id
            }
            
            response = self.session.post(f"{self.base_url}/enrollments", 
                                       data=json.dumps(enroll_data))
            
            if response.status_code == 201:
                enrollments_created += 1
            elif response.status_code == 409 and "capacity" in response.text.lower():
                self.print_test("Capacity Management", True, 
                              f"Enrollment rejected when capacity exceeded after {enrollments_created} enrollments")
                break
        
        if enrollments_created >= 4:  # If we enrolled 4 or more without rejection
            self.print_test("Capacity Management", False, "Capacity limit not enforced")
    
    def test_pagination_and_filtering(self):
        """Test pagination and filtering functionality"""
        self.print_section("PAGINATION & FILTERING TESTS")
        
        # Test student pagination
        response = self.session.get(f"{self.base_url}/students?page=1&limit=2")
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and 'total' in data and 'page' in data:
                self.print_test("Student Pagination", True, 
                              f"Page 1 with {len(data['items'])} items, total: {data['total']}")
            else:
                self.print_test("Student Pagination", False, "Invalid pagination response format")
        else:
            self.print_test("Student Pagination", False, f"Status: {response.status_code}")
        
        # Test student filtering by major
        response = self.session.get(f"{self.base_url}/students?major=Computer Science")
        
        if response.status_code == 200:
            data = response.json()
            cs_students = len(data.get('items', []))
            self.print_test("Student Filtering by Major", True, 
                          f"Found {cs_students} Computer Science students")
        else:
            self.print_test("Student Filtering by Major", False, f"Status: {response.status_code}")
        
        # Test student filtering by probation status
        response = self.session.get(f"{self.base_url}/students?on_probation=true")
        
        if response.status_code == 200:
            data = response.json()
            probation_students = len(data.get('items', []))
            self.print_test("Student Filtering by Probation", True, 
                          f"Found {probation_students} students on probation")
        else:
            self.print_test("Student Filtering by Probation", False, f"Status: {response.status_code}")
        
        # Test course filtering by department
        response = self.session.get(f"{self.base_url}/courses?department=Computer Science")
        
        if response.status_code == 200:
            data = response.json()
            cs_courses = len(data.get('items', []))
            self.print_test("Course Filtering by Department", True, 
                          f"Found {cs_courses} Computer Science courses")
        else:
            self.print_test("Course Filtering by Department", False, f"Status: {response.status_code}")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        self.print_section("ANALYTICS ENDPOINTS TESTS")
        
        # Test GPA distribution
        response = self.session.get(f"{self.base_url}/analytics/students/gpa-distribution")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.print_test("GPA Distribution Analytics", True, 
                              f"Retrieved {len(data)} GPA ranges")
                # Print distribution summary
                for item in data:
                    if item.get('count', 0) > 0:
                        print(f"    {item['gpa_range']}: {item['count']} students ({item['percentage']}%)")
            else:
                self.print_test("GPA Distribution Analytics", False, "No data returned")
        else:
            self.print_test("GPA Distribution Analytics", False, f"Status: {response.status_code}")
        
        # Test enrollment statistics
        response = self.session.get(f"{self.base_url}/analytics/courses/enrollment-stats")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.print_test("Enrollment Statistics", True, 
                              f"Retrieved stats for {len(data)} courses")
                # Print top enrolled courses
                for i, course in enumerate(data[:3]):
                    print(f"    {course['course_code']}: {course['current_enrollment']}/{course['max_capacity']} ({course['utilization_rate']}%)")
            else:
                self.print_test("Enrollment Statistics", False, "Invalid data format")
        else:
            self.print_test("Enrollment Statistics", False, f"Status: {response.status_code}")
        
        # Test teaching load statistics
        response = self.session.get(f"{self.base_url}/analytics/professors/teaching-load")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.print_test("Teaching Load Statistics", True, 
                              f"Retrieved stats for {len(data)} professors")
                for prof in data:
                    print(f"    {prof['professor_name']}: {prof['courses_count']} courses, {prof['total_students']} students")
            else:
                self.print_test("Teaching Load Statistics", False, "Invalid data format")
        else:
            self.print_test("Teaching Load Statistics", False, f"Status: {response.status_code}")
        
        # Test department performance
        response = self.session.get(f"{self.base_url}/analytics/departments/performance")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.print_test("Department Performance", True, 
                              f"Retrieved stats for {len(data)} departments")
                for dept in data:
                    print(f"    {dept['department']}: Avg GPA {dept['average_gpa']}, {dept['total_students']} students")
            else:
                self.print_test("Department Performance", False, "Invalid data format")
        else:
            self.print_test("Department Performance", False, f"Status: {response.status_code}")
    
    def test_bulk_operations(self):
        """Test bulk operations"""
        self.print_section("BULK OPERATIONS TESTS")
        
        # Test bulk student creation
        bulk_students = {
            "students": [
                {
                    "name": "Bulk Student 1",
                    "email": "bulk1@student.edu",
                    "major": "Engineering",
                    "year": 1,
                    "gpa": 3.0
                },
                {
                    "name": "Bulk Student 2",
                    "email": "bulk2@student.edu",
                    "major": "Engineering",
                    "year": 2,
                    "gpa": 3.5
                }
            ]
        }
        
        response = self.session.post(f"{self.base_url}/students/bulk", 
                                   data=json.dumps(bulk_students))
        
        if response.status_code == 201:
            data = response.json()
            self.print_test("Bulk Student Creation", True, f"Created {len(data)} students")
        else:
            self.print_test("Bulk Student Creation", False, f"Status: {response.status_code}")
        
        # Test bulk grade updates (if we have enrollments)
        if self.test_data["student_ids"] and self.test_data["course_ids"]:
            bulk_grades = {
                "grade_updates": [
                    {
                        "student_id": self.test_data["student_ids"][0],
                        "course_id": self.test_data["course_ids"][0],
                        "grade": "A"
                    }
                ]
            }
            
            response = self.session.put(f"{self.base_url}/enrollments/grades/bulk", 
                                      data=json.dumps(bulk_grades))
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Bulk Grade Updates", True, f"Updated {len(data)} grades")
            else:
                self.print_test("Bulk Grade Updates", False, f"Status: {response.status_code}")
    
    def test_grade_updates_and_gpa_calculation(self):
        """Test grade updates and GPA recalculation"""
        self.print_section("GRADE & GPA CALCULATION TESTS")
        
        student_ids = self.test_data["student_ids"]
        course_ids = self.test_data["course_ids"]
        
        if not student_ids or not course_ids:
            self.print_test("Grade Update Test", False, "Missing test data")
            return
        
        # Update a grade
        grade_update = {"grade": "A"}
        
        response = self.session.put(
            f"{self.base_url}/enrollments/{student_ids[0]}/{course_ids[0]}", 
            data=json.dumps(grade_update)
        )
        
        if response.status_code == 200:
            self.print_test("Grade Update", True, "Grade updated successfully")
            
            # Check if GPA was recalculated
            student_response = self.session.get(f"{self.base_url}/students/{student_ids[0]}")
            if student_response.status_code == 200:
                student = student_response.json()
                self.print_test("GPA Recalculation", True, 
                              f"Updated GPA: {student.get('gpa', 'N/A')}")
            else:
                self.print_test("GPA Recalculation", False, "Could not retrieve updated student")
        else:
            self.print_test("Grade Update", False, f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("🎓 Enhanced University Course Management System API - Comprehensive Test Suite")
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Basic connectivity
        if not self.test_connection():
            print("\n❌ Cannot connect to API. Exiting tests.")
            return
        
        # Test sequence
        self.test_health_endpoint()
        self.test_validation_errors()
        
        # Create test data
        self.create_test_professors()
        self.test_email_uniqueness()
        self.create_test_courses()
        self.test_professor_teaching_load()
        self.create_test_students()
        
        # Test business rules
        self.test_enrollment_business_rules()
        
        # Test advanced features
        self.test_pagination_and_filtering()
        self.test_analytics_endpoints()
        self.test_bulk_operations()
        self.test_grade_updates_and_gpa_calculation()
        
        # Final summary
        self.print_section("TEST SUMMARY")
        print("✅ Comprehensive test suite completed!")
        print("📊 Check analytics endpoints for detailed system statistics")
        print(f"🏁 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show final system state
        health_response = self.session.get(f"{self.base_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"\n📈 Final System State:")
            for entity, count in health_data.get('database', {}).items():
                print(f"    {entity.capitalize()}: {count}")


def main():
    """Main test runner"""
    tester = EnhancedUniversityAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main() 