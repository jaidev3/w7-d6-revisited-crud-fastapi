"""
Test script to demonstrate the University Course Management System API functionality.
This script creates sample data and tests all CRUD operations.
"""

import requests
import json
from datetime import date, datetime


class UniversityAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_connection(self):
        """Test if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ API is running successfully!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ API connection failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
            return False
    
    def create_professors(self):
        """Create sample professors"""
        print("\n📚 Creating Professors...")
        
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
            }
        ]
        
        professor_ids = []
        for prof in professors:
            response = self.session.post(f"{self.base_url}/professors", 
                                       data=json.dumps(prof))
            if response.status_code == 201:
                created_prof = response.json()
                professor_ids.append(created_prof['id'])
                print(f"✅ Created Professor: {created_prof['name']} (ID: {created_prof['id']})")
            else:
                print(f"❌ Failed to create professor: {response.text}")
        
        return professor_ids
    
    def create_courses(self, professor_ids):
        """Create sample courses"""
        print("\n📖 Creating Courses...")
        
        courses = [
            {
                "name": "Introduction to Programming",
                "code": "CS101",
                "credits": 3,
                "professor_id": professor_ids[0] if professor_ids else None,
                "max_capacity": 30
            },
            {
                "name": "Data Structures",
                "code": "CS201",
                "credits": 4,
                "professor_id": professor_ids[0] if professor_ids else None,
                "max_capacity": 25
            },
            {
                "name": "Calculus I",
                "code": "MATH101",
                "credits": 4,
                "professor_id": professor_ids[1] if len(professor_ids) > 1 else None,
                "max_capacity": 40
            },
            {
                "name": "General Physics",
                "code": "PHYS101",
                "credits": 3,
                "professor_id": professor_ids[2] if len(professor_ids) > 2 else None,
                "max_capacity": 35
            }
        ]
        
        course_ids = []
        for course in courses:
            response = self.session.post(f"{self.base_url}/courses", 
                                       data=json.dumps(course))
            if response.status_code == 201:
                created_course = response.json()
                course_ids.append(created_course['id'])
                print(f"✅ Created Course: {created_course['name']} (ID: {created_course['id']})")
            else:
                print(f"❌ Failed to create course: {response.text}")
        
        return course_ids
    
    def create_students(self):
        """Create sample students"""
        print("\n👨‍🎓 Creating Students...")
        
        students = [
            {
                "name": "John Doe",
                "email": "john.doe@student.university.edu",
                "major": "Computer Science",
                "year": 1
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@student.university.edu",
                "major": "Mathematics",
                "year": 2
            },
            {
                "name": "Mike Johnson",
                "email": "mike.johnson@student.university.edu",
                "major": "Physics",
                "year": 1
            },
            {
                "name": "Sarah Williams",
                "email": "sarah.williams@student.university.edu",
                "major": "Computer Science",
                "year": 3
            }
        ]
        
        student_ids = []
        for student in students:
            response = self.session.post(f"{self.base_url}/students", 
                                       data=json.dumps(student))
            if response.status_code == 201:
                created_student = response.json()
                student_ids.append(created_student['id'])
                print(f"✅ Created Student: {created_student['name']} (ID: {created_student['id']})")
            else:
                print(f"❌ Failed to create student: {response.text}")
        
        return student_ids
    
    def create_enrollments(self, student_ids, course_ids):
        """Create sample enrollments"""
        print("\n📝 Creating Enrollments...")
        
        enrollments = [
            {"student_id": student_ids[0], "course_id": course_ids[0]},  # John -> CS101
            {"student_id": student_ids[0], "course_id": course_ids[2]},  # John -> MATH101
            {"student_id": student_ids[1], "course_id": course_ids[2]},  # Jane -> MATH101
            {"student_id": student_ids[1], "course_id": course_ids[0]},  # Jane -> CS101
            {"student_id": student_ids[2], "course_id": course_ids[3]},  # Mike -> PHYS101
            {"student_id": student_ids[3], "course_id": course_ids[1]},  # Sarah -> CS201
        ]
        
        created_enrollments = []
        for enrollment in enrollments:
            response = self.session.post(f"{self.base_url}/enrollments", 
                                       data=json.dumps(enrollment))
            if response.status_code == 201:
                created_enrollment = response.json()
                created_enrollments.append(created_enrollment)
                print(f"✅ Enrolled Student {enrollment['student_id']} in Course {enrollment['course_id']}")
            else:
                print(f"❌ Failed to create enrollment: {response.text}")
        
        return created_enrollments
    
    def assign_grades(self, student_ids, course_ids):
        """Assign grades to demonstrate GPA calculation"""
        print("\n📊 Assigning Grades...")
        
        grades = [
            {"student_id": student_ids[0], "course_id": course_ids[0], "grade": "A"},
            {"student_id": student_ids[0], "course_id": course_ids[2], "grade": "B+"},
            {"student_id": student_ids[1], "course_id": course_ids[2], "grade": "A-"},
            {"student_id": student_ids[1], "course_id": course_ids[0], "grade": "B"},
            {"student_id": student_ids[2], "course_id": course_ids[3], "grade": "A+"},
            {"student_id": student_ids[3], "course_id": course_ids[1], "grade": "A"},
        ]
        
        for grade_data in grades:
            response = self.session.put(
                f"{self.base_url}/enrollments/{grade_data['student_id']}/{grade_data['course_id']}", 
                data=json.dumps({"grade": grade_data["grade"]})
            )
            if response.status_code == 200:
                print(f"✅ Assigned grade {grade_data['grade']} to Student {grade_data['student_id']} in Course {grade_data['course_id']}")
            else:
                print(f"❌ Failed to assign grade: {response.text}")
    
    def test_read_operations(self, student_ids, course_ids, professor_ids):
        """Test various read operations"""
        print("\n🔍 Testing Read Operations...")
        
        # Test get all students
        response = self.session.get(f"{self.base_url}/students")
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Retrieved {len(students)} students")
            # Display GPAs
            for student in students:
                gpa = student.get('gpa', 'N/A')
                print(f"   - {student['name']}: GPA = {gpa}")
        
        # Test get student courses
        if student_ids:
            response = self.session.get(f"{self.base_url}/students/{student_ids[0]}/courses")
            if response.status_code == 200:
                courses = response.json()
                print(f"✅ Student {student_ids[0]} is enrolled in {len(courses)} courses")
        
        # Test get course with students
        if course_ids:
            response = self.session.get(f"{self.base_url}/courses/{course_ids[0]}")
            if response.status_code == 200:
                course = response.json()
                print(f"✅ Course {course_ids[0]} has {len(course.get('enrolled_students', []))} students")
        
        # Test get professor with courses
        if professor_ids:
            response = self.session.get(f"{self.base_url}/professors/{professor_ids[0]}")
            if response.status_code == 200:
                professor = response.json()
                print(f"✅ Professor {professor_ids[0]} teaches {len(professor.get('assigned_courses', []))} courses")
    
    def test_update_operations(self, student_ids):
        """Test update operations"""
        print("\n✏️ Testing Update Operations...")
        
        if student_ids:
            # Update student information
            update_data = {"major": "Computer Engineering", "year": 2}
            response = self.session.put(f"{self.base_url}/students/{student_ids[0]}", 
                                      data=json.dumps(update_data))
            if response.status_code == 200:
                updated_student = response.json()
                print(f"✅ Updated student: {updated_student['name']} - Major: {updated_student['major']}, Year: {updated_student['year']}")
    
    def test_capacity_limits(self, course_ids):
        """Test course capacity limits"""
        print("\n🚫 Testing Capacity Limits...")
        
        if course_ids:
            # Try to exceed course capacity by creating many students and enrolling them
            print("Creating additional students to test capacity...")
            
            for i in range(5):
                student_data = {
                    "name": f"Test Student {i+1}",
                    "email": f"test{i+1}@university.edu",
                    "major": "Test Major",
                    "year": 1
                }
                
                student_response = self.session.post(f"{self.base_url}/students", 
                                                   data=json.dumps(student_data))
                
                if student_response.status_code == 201:
                    student = student_response.json()
                    
                    # Try to enroll in first course
                    enrollment_data = {"student_id": student['id'], "course_id": course_ids[0]}
                    enrollment_response = self.session.post(f"{self.base_url}/enrollments", 
                                                          data=json.dumps(enrollment_data))
                    
                    if enrollment_response.status_code == 201:
                        print(f"✅ Enrolled Test Student {i+1}")
                    else:
                        print(f"⚠️ Enrollment failed for Test Student {i+1}: {enrollment_response.json().get('detail', 'Unknown error')}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎓 University Course Management System - Comprehensive API Test")
        print("=" * 60)
        
        # Test connection
        if not self.test_connection():
            return
        
        # Create sample data
        professor_ids = self.create_professors()
        course_ids = self.create_courses(professor_ids)
        student_ids = self.create_students()
        
        if student_ids and course_ids:
            self.create_enrollments(student_ids, course_ids)
            self.assign_grades(student_ids, course_ids)
        
        # Test read operations
        self.test_read_operations(student_ids, course_ids, professor_ids)
        
        # Test update operations
        self.test_update_operations(student_ids)
        
        # Test capacity limits
        self.test_capacity_limits(course_ids)
        
        print("\n🎉 Test completed! Check the API documentation at http://localhost:8000/docs")
        print("💡 Try exploring the API endpoints manually using the interactive documentation.")


if __name__ == "__main__":
    tester = UniversityAPITester()
    tester.run_comprehensive_test() 