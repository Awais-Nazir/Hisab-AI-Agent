import os

import httpx
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")


class HisabClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=BASE_URL,
            timeout=10.0,
        )

    def login(self):
        email = os.getenv("EMAIL")
        password = os.getenv("PASS")

        if not email or not password:
            raise ValueError("EMAIL and PASS must be set in .env")

        response = self.client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        response.raise_for_status()

        return response.json()

    def list_expenses(self):
        response = self.client.get("/expenses")

        response.raise_for_status()

        return response.json()

    def list_contacts(self):
        response = self.client.get("/people")

        response.raise_for_status()

        return response.json()

    def list_contact_balance(self, contact_id):
        response = self.client.get(f"/people/{contact_id}/ledger")

        response.raise_for_status()

        return response.json()

    def list_categories(self):
        response = self.client.get("/categories")

        response.raise_for_status()

        return response.json()

    def list_accounts(self):
        response = self.client.get("/accounts")

        response.raise_for_status()

        return response.json()

    def list_udhar(self):
        response = self.client.get("/udhar")

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()
