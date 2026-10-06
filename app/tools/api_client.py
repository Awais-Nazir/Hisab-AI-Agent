import os

import httpx
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")


class HisabClient:
    def __init__(
        self,
        authorization: str | None = None,
        cookie: str | None = None,
    ):
        self.client = httpx.Client(
            base_url=BASE_URL,
            timeout=10.0,
        )

        if authorization:
            self.client.headers.update({"Authorization": authorization})

        if cookie:
            self.client.headers.update({"Cookie": cookie})

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

    def get_category_name(self, category_id: str):
        data = self.list_categories()

        for category in data["categories"]:
            if (
                category["id"] == category_id
                or category["name"].lower() == category_id.lower()
            ):
                return category["name"]

        raise ValueError(f"Category not found: {category_id}")

    def get_account_name(self, account_id: str):
        data = self.list_accounts()

        for account in data["accounts"]:
            if account["id"] == account_id:
                return account["name"]

        return account_id

    def write_expense(
        self,
        amount: float,
        description: str,
        category: str,
        account_id: str,
        is_personal: bool,
        payments: list[dict] | None = None,
        splits: list[dict] | None = None,
    ):
        payload = {
            "amount": amount,
            "description": description,
            "category": category,
            "accountId": account_id,
            "isShared": not is_personal,
        }

        if not is_personal:
            payload["payments"] = payments or []
            payload["splits"] = splits or []

        print("PAYLOAD:", payload)  # temporary

        response = self.client.post(
            "/expenses",
            json=payload,
        )

        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()

    def write_udhar(
        self,
        type: str,
        person_id: str,
        amount: float,
        account_id: str,
        note: str | None = None,
    ):
        payload = {
            "type": type,
            "personId": person_id,
            "amount": amount,
            "accountId": account_id,
        }

        if note:
            payload["note"] = note

        print("PAYLOAD:", payload)  # temporary

        response = self.client.post("/udhar", json=payload)

        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()

    def settle_udhar(
        self,
        udhar_id: str,
        account_id: str,
    ):
        payload = {
            "accountId": account_id,
        }

        print("PAYLOAD", payload)

        response = self.client.post(
            f"/udhar/{udhar_id}/settle",
            json=payload,
        )

        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()

    def write_global_settlement(
        self,
        from_person_id: str,
        to_person_id: str,
        amount: float,
        account_id: str | None = None,
        note: str | None = None,
    ):
        payload = {
            "fromPersonId": from_person_id,
            "toPersonId": to_person_id,
            "amount": amount,
        }

        if account_id:
            payload["accountId"] = account_id

        if note:
            payload["note"] = note

        print("PAYLOAD", payload)

        response = self.client.post("/settlements/global", json=payload)

        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()
