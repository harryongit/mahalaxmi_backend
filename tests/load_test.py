from locust import HttpUser, task, between
import random

class MahalaxmiDevotee(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # We don't authenticate in on_start because getting an OTP requires manual intervention usually.
        # But for load testing, if we have a backdoor or mock OTP, we can do it here.
        pass

    @task(3)
    def request_otp(self):
        # Simulate users requesting OTP during high load (festival season)
        phone = f"+9198{random.randint(10000000, 99999999)}"
        self.client.post("/api/v1/auth/request-otp", json={"phone_number": phone})

    @task(1)
    def view_services(self):
        # Simulate users browsing services
        self.client.get("/api/v1/services/active")
        
    @task(1)
    def view_categories(self):
        self.client.get("/api/v1/services/categories")
