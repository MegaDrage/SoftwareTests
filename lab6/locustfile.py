from locust import HttpUser, task, between
import json

class OpenBMCTestUser(HttpUser):
    host = "https://localhost:2443"
    wait_time = between(1, 3)

    @task(3)
    def get_system_info(self):
        with self.client.get(
            "/redfish/v1/Systems/system",
            auth=("root", "0penBmc"),
            verify=False,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    power_state = response.json().get("PowerState")
                    if not power_state:
                        response.failure("PowerState not found")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")

class PublicAPITestUser(HttpUser):
    host = "https://jsonplaceholder.typicode.com"
    wait_time = between(2, 5)

    @task(2)
    def get_posts(self):
        self.client.get("/posts")

    @task(1)
    def get_weather(self):
        with self.client.get(
            "https://wttr.in/Novosibirsk?format=j1",
            name="/weather",
            catch_response=True
        ) as response:
            if "current_condition" not in response.text:
                response.failure("Invalid weather data")