## tests/auth_service/api/pages/auth_api.py
import requests


class AuthAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def authorize(self, data):
        return requests.post(
            f"{self.base_url}/authorize",
            data=data
        )

    def exchange_token(self, json):
        return requests.post(
            f"{self.base_url}/token",
            json=json
            # {
            #     "client_id": client_id,
            #     "client_secret": client_secret,
            #     "code": code
            # }
        )
