#!/usr/bin/env python3
"""
Test script for AI Lesson Reviewer API endpoints
Run this script to test all endpoints after setting up the server
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testteacher",
    "email": "test@example.com",
    "password": "testpassword123",
    "password2": "testpassword123",
    "name": "Test Teacher"
}

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def register_user(self):
        """Test user registration"""
        self.log("Testing user registration...")
        response = requests.post(
            f"{self.base_url}/register/",
            json=TEST_USER,
            headers=self.headers
        )
        
        if response.status_code == 201:
            self.log("✓ User registered successfully")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            self.log("ℹ User already exists, continuing...")
            return True
        else:
            self.log(f"✗ Registration failed: {response.status_code}")
            self.log(response.text)
            return False
    
    def login(self):
        """Test user login and get token"""
        self.log("Testing user login...")
        response = requests.post(
            f"{self.base_url}/token/",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            },
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            self.log("✓ Login successful")
            return True
        else:
            self.log(f"✗ Login failed: {response.status_code}")
            self.log(response.text)
            return False
    
    def test_profile(self):
        """Test profile endpoint"""
        self.log("Testing profile endpoint...")
        response = requests.get(
            f"{self.base_url}/profile/",
            headers=self.headers
        )
        
        if response.status_code == 200:
            self.log("✓ Profile retrieved successfully")
            data = response.json()
