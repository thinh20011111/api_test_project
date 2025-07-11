# tests/utils/api_client.py
import requests

class APIClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token
        self.default_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "origin": "https://lab-fe.emso.vn",
            "priority": "u=1, i",
            "referer": "https://lab-fe.emso.vn/",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }

    def get_headers(self, custom_headers=None, include_auth=True):
        headers = self.default_headers.copy()
        if include_auth and self.auth_token:
            headers["authorization"] = f"Bearer {self.auth_token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def get(self, endpoint, params=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        response = requests.get(url, headers=headers, params=params)
        return response, {"url": url, "method": "GET", "headers": headers}

    def post(self, endpoint, data=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        response = requests.post(url, headers=headers, json=data)
        return response, {"url": url, "method": "POST", "headers": headers}