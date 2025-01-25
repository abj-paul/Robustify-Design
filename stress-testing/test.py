import requests
import pytest
import json
from typing import Dict, Any

BASE_URL = "http://localhost:3000"  # Adjust to your actual server URL
import random
import string

def generate_random_username(length=8):
    characters = string.ascii_letters + string.digits + "_"
    username = ''.join(random.choice(characters) for i in range(length))
    return username

class TestAPIEndpoints:
    def setup_method(self):
        # Registration and authentication setup
        self.username = "testabj" #generate_random_username()
        self.password = "spl3exampassword"
        self.organization = "iit"
        self.access_token = None
        self.project_id = None
        self.user_id = 14
        self.project_name = "VotingTest"

    def register_user(self) -> Dict[str, Any]:
        """Register a new user"""
        register_payload = {
            "username": self.username,
            "password": self.password,
            "organization": self.organization,
            "email": f"{self.username}@example.com"
        }
        response = requests.post(f"{BASE_URL}/register", json=register_payload)
        assert response.status_code == 200, f"Registration failed: {response.text}"
        return response.json()

    def login_user(self) -> str:
        """Login and retrieve access token"""
        login_payload = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(f"{BASE_URL}/login", json=login_payload)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.access_token = data['access_token']
        return self.access_token

    def create_project(self) -> Dict[str, Any]:
        """Create a test project"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        project_payload = {
            "name": self.project_name,
            "description": "A comprehensive test project",
        }
        response = requests.post(f"{BASE_URL}/projects?user_id={self.user_id}", 
                                 json=project_payload, 
                                 headers=headers)
        assert response.status_code == 200, f"Project creation failed: {response.text}"
        project = response.json()
        self.project_id = project['id']
        print(f"Created Project id = {self.project_id}")
        return project
    
    # def test_register_user(self):
    #     """Test user registration"""
    #     self.register_user()

    def test_login_user(self):
        """Test user login"""
        self.login_user()

    def test_create_project(self):
        """Test project creation"""
        self.create_project()

    def test_full_workflow(self):
        """End-to-end test covering registration, login, project CRUD, and spec uploads"""
        # 1. User Registration
        # user = self.register_user()
        # self.user_id = user['id']
        # assert self.user_id is not None, "User registration failed"

        # 2. User Login
        token = self.login_user()
        assert token is not None, "Login token not received"

        # 3. Create Project
        project = self.create_project()
        assert project['name'] == self.project_name, "Project creation failed"

        # 4. Get User Projects
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/projects", 
                                params={"user_id": self.user_id}, 
                                headers=headers)
        assert response.status_code == 200
        assert len(response.json()) > 0, "No projects retrieved"

        # 5. Get Specific Project
        # response = requests.get(f"{BASE_URL}/projects/{self.project_id}", 
        #                         params={"user_id": self.user_id}, 
        #                         headers=headers)
        # assert response.status_code == 200
        # assert response.json()['id'] == self.project_id

        # 6. Update Project
        update_payload = {
            "name": self.project_name+"_uwu",
            "description": "Updated project description"
        }
        response = requests.put(f"{BASE_URL}/projects/{self.project_id}", 
                                json=update_payload, 
                                params={"user_id": self.user_id},
                                headers=headers)
        assert response.status_code == 200
        assert response.json()['name'] == self.project_name+"_uwu"

        # 7. Environment Specification Upload (LTS)
        with open('test_env.lts', 'w') as f:
            f.write("Test LTS Environment Specification")
        
        with open('test_env.lts', 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{BASE_URL}/projects/{self.project_id}/environment_spec", 
                                     files=files, 
                                     headers=headers)
        assert response.status_code == 200

        # 8. Get Environment Specification
        response = requests.get(f"{BASE_URL}/projects/{self.project_id}/environment_spec", 
                                headers=headers)
        assert response.status_code == 200
        assert 'spec' in response.json()

        # 9. System Specification Upload (XML)
        with open('test_sys.xml', 'w') as f:
            f.write("<uml>Test System Specification</uml>")
        
        with open('test_sys.xml', 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{BASE_URL}/projects/{self.project_id}/system_spec", 
                                     files=files, 
                                     headers=headers)
        assert response.status_code == 200

        # 10. Get System Specification
        response = requests.get(f"{BASE_URL}/projects/{self.project_id}/system_spec", 
                                headers=headers)
        assert response.status_code == 200
        assert 'spec' in response.json()

        # 11. Delete Project (Optional)
        response = requests.delete(f"{BASE_URL}/projects/{self.project_id}", 
                                   params={"user_id": self.user_id},
                                   headers=headers)
        assert response.status_code == 200
    # def test_upload_safety_property(self):
    #     """Test uploading a safety specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     # Prepare test file for upload
    #     with open("test_p.lts", "w") as f:
    #         f.write("Safety property content")

    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     files = {"file": open("test_p.lts", "rb")}
    #     print(f"Does variables get reset? {self.project_id}")
    #     # Upload safety specification
    #     response = requests.post(
    #         f"{BASE_URL}/projects/{self.project_id}/safety_spec",
    #         headers=headers, 
    #         files=files
    #     )
    #     assert response.status_code == 200, f"Upload failed: {response.text}"
    #     assert 'message' in response.json(), "System spec updated successfully in database and file"
    # def test_get_safety_property(self):
    #     """Test retrieving a safety specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     headers = {"Authorization": f"Bearer {self.access_token}"}

    #     # Retrieve safety specification
    #     response = requests.get(
    #         f"{BASE_URL}/projects/{self.project_id}/safety_spec",
    #         headers=headers
    #     )
    #     assert response.status_code == 200, f"Failed to retrieve safety property: {response.text}"
    #     assert 'spec' in response.json(), "Safety property not found in response"
    # def test_update_safety_property(self):
    #     """Test updating a safety specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     # Prepare updated content
    #     with open("test_p.lts", "w") as f:
    #         f.write("Updated safety property content")

    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     files = {"file": open("test_p.lts", "rb")}

    #     # Update safety specification
    #     response = requests.put(
    #         f"{BASE_URL}/projects/{self.project_id}/safety_spec",
    #         headers=headers,
    #         files=files
    #     )
    #     assert response.status_code == 200, f"Update failed: {response.text}"
    #     assert 'message' in response.json(), "System spec updated successfully in database and file"

    # def test_upload_config(self):
    #     """Test uploading a configuration specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     # Prepare test file for upload
    #     with open("test_config.json", "w") as f:
    #         f.write('{"key": "value"}')

    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     files = {"file": open("test_config.json", "rb")}

    #     # Upload configuration specification
    #     response = requests.post(
    #         f"{BASE_URL}/projects/{self.project_id}/configuration_spec",
    #         headers=headers, 
    #         files=files
    #     )
    #     assert response.status_code == 200, f"Upload failed: {response.text}"
    #     assert 'message' in response.json(), "System spec updated successfully in database and file"

    # def test_get_config(self):
    #     """Test retrieving a configuration specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     headers = {"Authorization": f"Bearer {self.access_token}"}

    #     # Retrieve configuration specification
    #     response = requests.get(
    #         f"{BASE_URL}/projects/{self.project_id}/configuration_spec",
    #         headers=headers
    #     )
    #     assert response.status_code == 200, f"Failed to retrieve configuration spec: {response.text}"
    #     assert 'spec' in response.json(), "Configuration spec not found in response"

    # def test_update_config(self):
    #     """Test updating a configuration specification for a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     # Prepare updated content
    #     with open("test_config.json", "w") as f:
    #         f.write('{"key": "new_value"}')

    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     files = {"file": open("test_config.json", "rb")}

    #     # Update configuration specification
    #     response = requests.put(
    #         f"{BASE_URL}/projects/{self.project_id}/configuration_spec",
    #         headers=headers,
    #         files=files
    #     )
    #     assert response.status_code == 200, f"Update failed: {response.text}"
    #     assert 'message' in response.json(), "config-pareto.json spec saved successfully in projects/Test Project-13."
    # def test_run_fortis(self):
    #     """Test running the Fortis execution on a project"""
    #     token = self.login_user()
    #     assert token is not None, "Login token not received"

    #     headers = {"Authorization": f"Bearer {self.access_token}"}

    #     class_list = ["Class1", "Class2"]  # Example list, modify based on actual classes

    #     # Run Fortis execution
    #     response = requests.post(
    #         f"{BASE_URL}/projects/{self.project_id}/execute",
    #         headers=headers,
    #         data={"class_list": class_list}
    #     )
    #     assert response.status_code == 200, f"Execution failed: {response.text}"
    #     #assert 'result' in response.json(), "Fortis execution result not found"

    # # def test_get_reports(self):
    # #     """Test retrieving reports for a project"""
    # #     token = self.login_user()
    # #     assert token is not None, "Login token not received"

    # #     headers = {"Authorization": f"Bearer {self.access_token}"}

    # #     # Retrieve reports
    # #     response = requests.get(
    # #         f"{BASE_URL}/reports/{self.project_id}/",
    # #         headers=headers
    # #     )
    # #     assert response.status_code == 200, f"Failed to retrieve reports: {response.text}"
    # #     assert 'reports' in response.json(), "Reports not found in response"

    # # def test_get_solutions(self):
    # #     """Test retrieving solutions for a project"""
    # #     token = self.login_user()
    # #     assert token is not None, "Login token not received"

    # #     headers = {"Authorization": f"Bearer {self.access_token}"}

    # #     # Retrieve solutions
    # #     response = requests.get(
    # #         f"{BASE_URL}/solutions/{self.project_id}/",
    # #         headers=headers
    # #     )
    # #     assert response.status_code == 200, f"Failed to retrieve solutions: {response.text}"
    # #     assert 'solutions' in response.json(), "Solutions not found in response"


def pytest_main():
    pytest.main([__file__])

if __name__ == "__main__":
    pytest_main()



    # def test_error_scenarios(self):
    #     """Test error handling and edge cases"""
    #     # # 1. Duplicate User Registration
    #     # self.register_user()
    #     # duplicate_payload = {
    #     #     "username": self.username,
    #     #     "password": "newpassword",
    #     #     "email": f"{self.username}@example.com"
    #     # }
    #     # response = requests.post(f"{BASE_URL}/register", json=duplicate_payload)
    #     # assert response.status_code == 400

    #     # 2. Invalid Login
    #     invalid_login = {
    #         "username": self.username,
    #         "password": "wrongpassword"
    #     }
    #     response = requests.post(f"{BASE_URL}/login", json=invalid_login)
    #     assert response.status_code == 400

    #     # 3. Access Project Without Authentication
    #     response = requests.get(f"{BASE_URL}/projects")
    #     assert response.status_code in [401, 403]