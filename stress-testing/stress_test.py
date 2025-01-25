import asyncio
import pytest
import httpx

BASE_URL = "http://localhost:3000"
# @pytest.mark.asyncio
# async def test_stress_register_and_login():
#     """Stress test for user registration and login."""
#     async with httpx.AsyncClient(timeout=httpx.Timeout(30)) as client:
#         tasks = []
#         for i in range(100):  # Simulate 100 concurrent users
#             username = f"user{i}"
#             password = "testpassword"
#             organization = "iit"
#             tasks.append(client.post(f"{BASE_URL}/register", json={
#                 "username": username,
#                 "password": password,
#                 "organization": organization
#             }))

#         # Execute registration in smaller batches
#         for i in range(0, 100, 20):  # Batch size: 20
#             batch_tasks = tasks[i:i+20]
#             responses = await asyncio.gather(*batch_tasks)
#             for response in responses:
#                 if response.status_code not in {200, 400}:
#                     print(f"Unexpected status {response.status_code}: {response.text}")
#             assert all(response.status_code in {200, 400} for response in responses)

#         # Simulate login for all users
#         login_tasks = []
#         for i in range(100):
#             username = f"user{i}"
#             password = "testpassword"
#             login_tasks.append(client.post(f"{BASE_URL}/login", json={
#                 "username": username,
#                 "password": password
#             }))

#         login_responses = await asyncio.gather(*login_tasks)
#         for response in login_responses:
#             if response.status_code != 200:
#                 print(f"Login failed for user{i}: {response.text}")
#         assert all(response.status_code == 200 for response in login_responses)

# @pytest.mark.asyncio
# async def test_stress_project_creation():
#     """Stress test for creating projects."""
#     async with httpx.AsyncClient() as client:
#         # Login and get access token
#         login_response = await client.post(f"{BASE_URL}/login", json={
#             "username": "testabj",
#             "password": "spl3exampassword"
#         })
#         user_id = 14
#         assert login_response.status_code == 200
#         token = login_response.json()["access_token"]

#         headers = {"Authorization": f"Bearer {token}"}

#         # Create multiple projects concurrently
#         tasks = []
#         for i in range(50):
#             project_name = f"Project {i}"
#             tasks.append(client.post(f"{BASE_URL}/projects?user_id={user_id}", json={
#                 "name": project_name,
#                 "description": "test project",
#             }, headers=headers))

#         responses = await asyncio.gather(*tasks)

#         # Log failed responses
#         for idx, response in enumerate(responses):
#             if response.status_code != 200:
#                 print(f"Request {idx} failed with status {response.status_code}: {response.json()}")

#         assert all(response.status_code == 200 for response in responses)



@pytest.mark.asyncio
async def test_stress_spec_upload():
    """Stress test for specification uploads."""
    async with httpx.AsyncClient() as client:
        # Login and get access token
        login_response = await client.post(f"{BASE_URL}/login", json={
            "username": "testabj",
            "password": "spl3exampassword"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Upload specifications concurrentl
        tasks = []
        for i in range(10):
            project_id = i + 1  # Assume projects with these IDs exist
            tasks.append(client.post(
                f"{BASE_URL}/projects/{project_id}/environment_spec",
                files={"file": ("test_env.lts", "Some environment specification content")},
                headers=headers
            ))

        responses = await asyncio.gather(*tasks)
        assert all(response.status_code == 200 for response in responses)


# # @pytest.mark.asyncio
# # async def test_stress_execute_pipeline():
# #     """Stress test for robustification execution."""
# #     async with httpx.AsyncClient() as client:
# #         # Login and get access token
# #         login_response = await client.post(f"{BASE_URL}/login", json={
# #             "username": "admin",
# #             "password": "adminpassword"
# #         })
# #         assert login_response.status_code == 200
# #         token = login_response.json()["access_token"]

# #         headers = {"Authorization": f"Bearer {token}"}

# #         # Execute pipeline concurrently
# #         tasks = []
# #         for i in range(10):
# #             project_id = i + 1  # Assume projects with these IDs exist
# #             tasks.append(client.post(
# #                 f"{BASE_URL}/projects/{project_id}/execute",
# #                 json={"class_list": ["class1", "class2"]},
# #                 headers=headers
# #             ))

# #         responses = await asyncio.gather(*tasks)
# #         assert all(response.status_code in {200, 400} for response in responses)
