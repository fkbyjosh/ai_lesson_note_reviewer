#!/usr/bin/env python3
"""
Complete Test script for AI Lesson Reviewer API endpoints
Run this script to test all endpoints after setting up the server

Usage:
1. Start Django server: python manage.py runserver
2. Run this script: python tests.py
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testteacher",
    "email": "test@example.com",
    "password": "testpassword123",
    "password2": "testpassword123",
    "name": "Test Teacher"
}

TEST_LESSON_NOTE = {
    "subject": "Mathematics",
    "grade_level": "Grade 5",
    "term": "Term 1",
    "content": """
    Lesson Title: Introduction to Fractions
    
    Learning Objectives:
    - Students will understand what fractions represent
    - Students will be able to identify numerator and denominator
    - Students will solve basic fraction problems
    
    Materials Needed:
    - Fraction circles
    - Whiteboard
    - Worksheets
    
    Lesson Structure:
    1. Introduction (10 minutes)
       - Review previous lesson on whole numbers
       - Introduce the concept of parts of a whole
    
    2. Main Activity (25 minutes)
       - Demonstrate fractions using fraction circles
       - Show how to write fractions (numerator/denominator)
       - Interactive examples with students
    
    3. Practice (10 minutes)
       - Students work on worksheet problems
       - Teacher provides individual support
    
    4. Conclusion (5 minutes)
       - Review key concepts
       - Preview next lesson
    
    Assessment:
    - Observation during activities
    - Worksheet completion
    - Exit ticket with 3 fraction problems
    """
}

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.lesson_note_id = None
        self.feedback_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def log_success(self, message):
        self.log(f"✓ {message}")
        
    def log_error(self, message):
        self.log(f"✗ {message}")
        
    def log_info(self, message):
        self.log(f"ℹ {message}")
    
    def check_server_connection(self):
        """Check if Django server is running"""
        self.log("Checking server connection...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 404:  # Expected for API root
                self.log_success("Server is running and accessible")
                return True
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to server. Make sure Django server is running on localhost:8000")
            return False
        except Exception as e:
            self.log_error(f"Server connection error: {str(e)}")
            return False
        
    def register_user(self):
        """Test user registration"""
        self.log("Testing user registration...")
        try:
            response = requests.post(
                f"{self.base_url}/register/",
                json=TEST_USER,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 201:
                self.log_success("User registered successfully")
                data = response.json()
                self.log_info(f"User ID: {data.get('user_id')}, Username: {data.get('username')}")
                return True
            elif response.status_code == 400:
                error_data = response.json()
                if "already exists" in str(error_data):
                    self.log_info("User already exists, continuing...")
                    return True
                else:
                    self.log_error(f"Registration failed: {error_data}")
                    return False
            else:
                self.log_error(f"Registration failed with status {response.status_code}")
                self.log_error(response.text)
                return False
                
        except Exception as e:
            self.log_error(f"Registration request failed: {str(e)}")
            return False
    
    def login(self):
        """Test user login and get token"""
        self.log("Testing user login...")
        try:
            response = requests.post(
                f"{self.base_url}/token/",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                },
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                self.log_success("Login successful")
                self.log_info(f"Access token obtained (length: {len(self.token)})")
                return True
            else:
                self.log_error(f"Login failed with status {response.status_code}")
                self.log_error(response.text)
                return False
                
        except Exception as e:
            self.log_error(f"Login request failed: {str(e)}")
            return False
    
    def test_profile(self):
        """Test profile endpoint"""
        self.log("Testing profile endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/profile/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_success("Profile retrieved successfully")
                data = response.json()
                self.log_info(f"Username: {data.get('username')}, Teacher: {data.get('teacher_name')}")
                return True
            else:
                self.log_error(f"Profile request failed with status {response.status_code}")
                self.log_error(response.text)
                return False
                
        except Exception as e:
            self.log_error(f"Profile request failed: {str(e)}")
            return False
    
    def test_lesson_note_creation(self):
        """Test lesson note creation"""
        self.log("Testing lesson note creation...")
        try:
            response = requests.post(
                f"{self.base_url}/lesson-notes/",
                json=TEST_LESSON_NOTE,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 201:
                self.log_success("Lesson note created successfully")
                data = response.json()
                self.lesson_note_id = data.get('id')
                self.log_info(f"Lesson Note ID: {self.lesson_note_id}")
                self.log_info(f"Subject: {data.get('subject')}, Grade: {data.get('grade_level')}")
                return True
            else:
                self.log_error(f"Lesson note creation failed with status {response.status_code}")
                self.log_error(response.text)
                return False
                
        except Exception as e:
            self.log_error(f"Lesson note creation failed: {str(e)}")
            return False
    
    def test_lesson_notes_list(self):
        """Test lesson notes listing"""
        self.log("Testing lesson notes listing...")
        try:
            response = requests.get(
                f"{self.base_url}/lesson-notes/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else data.get('count', 0)
                self.log_success(f"Retrieved {count} lesson notes")
                return True
            else:
                self.log_error(f"Lesson notes listing failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Lesson notes listing failed: {str(e)}")
            return False
    
    def test_ai_feedback_generation(self):
        """Test AI feedback generation"""
        if not self.lesson_note_id:
            self.log_error("No lesson note ID available for AI feedback test")
            return False
            
        self.log("Testing AI feedback generation...")
        try:
            # First check if AI feedback already exists
            response = requests.get(
                f"{self.base_url}/lesson-notes/{self.lesson_note_id}/ai-feedback/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('has_ai_feedback'):
                    self.log_success("AI feedback already exists")
                    self.feedback_id = data.get('feedback', {}).get('id')
                    score = data.get('feedback', {}).get('score')
                    self.log_info(f"AI Feedback Score: {score}")
                    return True
            
            # Generate new AI feedback
            self.log("Generating new AI feedback...")
            response = requests.post(
                f"{self.base_url}/lesson-notes/{self.lesson_note_id}/generate-ai-feedback/",
                headers=self.headers,
                timeout=30  # AI generation might take longer
            )
            
            if response.status_code == 201:
                self.log_success("AI feedback generated successfully")
                data = response.json()
                self.feedback_id = data.get('feedback_id')
                feedback_data = data.get('feedback', {})
                score = feedback_data.get('score')
                self.log_info(f"AI Feedback Score: {score}")
                return True
            else:
                self.log_error(f"AI feedback generation failed with status {response.status_code}")
                self.log_error(response.text)
                return False
                
        except Exception as e:
            self.log_error(f"AI feedback generation failed: {str(e)}")
            return False
    
    def test_feedback_retrieval(self):
        """Test feedback retrieval"""
        if not self.lesson_note_id:
            self.log_error("No lesson note ID available for feedback test")
            return False
            
        self.log("Testing feedback retrieval...")
        try:
            response = requests.get(
                f"{self.base_url}/lesson-notes/{self.lesson_note_id}/feedback/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('feedback_count', 0)
                self.log_success(f"Retrieved {count} feedback records")
                
                # Display feedback details
                for feedback in data.get('feedback', []):
                    reviewer_type = feedback.get('reviewer_type')
                    score = feedback.get('score')
                    self.log_info(f"  - {reviewer_type} Feedback: Score {score}")
                
                return True
            else:
                self.log_error(f"Feedback retrieval failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Feedback retrieval failed: {str(e)}")
            return False
    
    def test_all_ai_feedback(self):
        """Test getting all AI feedback for teacher"""
        self.log("Testing all AI feedback retrieval...")
        try:
            response = requests.get(
                f"{self.base_url}/feedback/ai-feedback/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log_success(f"Retrieved {count} AI feedback records")
                return True
            else:
                self.log_error(f"All AI feedback retrieval failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"All AI feedback retrieval failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("="*60)
        self.log("Starting AI Lesson Reviewer API Tests")
        self.log("="*60)
        
        tests = [
            ("Server Connection", self.check_server_connection),
            ("User Registration", self.register_user),
            ("User Login", self.login),
            ("Profile Retrieval", self.test_profile),
            ("Lesson Note Creation", self.test_lesson_note_creation),
            ("Lesson Notes Listing", self.test_lesson_notes_list),
            ("AI Feedback Generation", self.test_ai_feedback_generation),
            ("Feedback Retrieval", self.test_feedback_retrieval),
            ("All AI Feedback", self.test_all_ai_feedback),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_error(f"Test {test_name} crashed: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Summary
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        self.log(f"✓ Passed: {passed}")
        self.log(f"✗ Failed: {failed}")
        self.log(f"Total Tests: {passed + failed}")
        
        if failed == 0:
            self.log_success("🎉 ALL TESTS PASSED! Your API is working correctly.")
        else:
            self.log_error(f"❌ {failed} tests failed. Check the errors above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Your AI Lesson Reviewer API is ready to use!")
        print("You can now:")
        print("- Register users via /api/register/")
        print("- Login via /api/token/")
        print("- Create lesson notes via /api/lesson-notes/")
        print("- Generate AI feedback automatically")
        print("- Retrieve feedback via various endpoints")
    else:
        print("\n🔧 Please fix the issues above before using the API.")