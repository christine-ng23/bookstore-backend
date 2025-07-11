# tests/auth_service/api/pages/reset_api.py
import requests


class ResetAPI:
    ENDPOINT = "/test/reset_and_load"

    def __init__(self, base_url, secret_key):
        self.base_url = base_url.rstrip("/")
        self.secret_key = secret_key

    def reset_with_json(self, json_data):
        url = f"{self.base_url}{self.ENDPOINT}"
        headers = {"X-Test-Secret": self.secret_key}
        return requests.post(url, headers=headers, json=json_data)

    def reset_with_file(self, file_path):
        url = f"{self.base_url}{self.ENDPOINT}"
        headers = {"X-Test-Secret": self.secret_key}
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "application/json")}
            return requests.post(url, headers=headers, files=files)

    def reset_without_file_and_json(self):
        url = f"{self.base_url}{self.ENDPOINT}"
        headers = {"X-Test-Secret": self.secret_key}
        return requests.post(url, headers=headers)

    def reset_without_auth(self, json_data):
        url = f"{self.base_url}{self.ENDPOINT}"
        return requests.post(url, json=json_data)

    def reset_with_invalid_auth(self, json_data):
        url = f"{self.base_url}{self.ENDPOINT}"
        headers = {"X-Test-Secret": "invalid key"}
        return requests.post(url, headers=headers)

    def reset_with_invalid_ext(self, file_path):
        url = f"{self.base_url}{self.ENDPOINT}"
        headers = {"X-Test-Secret": self.secret_key}
        with open(file_path, "rb") as f:
            files = {"file": ("file.txt", f, "text/plain")}
            return requests.post(url, headers=headers, files=files)
