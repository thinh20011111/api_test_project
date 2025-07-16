# tests/utils/api_client.py
import requests
import logging
import time

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
    
    def get_time_duration(self, start_time, end_time):
        """Tính thời gian thực thi của request (giây)."""
        return end_time - start_time  # Trả về giây thay vì mili giây

    def get(self, endpoint, params=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        start_time = time.time()
        logging.debug(f"Sending GET request to {url}")
        response = requests.get(url, headers=headers, params=params, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "GET", "headers": headers, "time_duration": time_duration}

    def post_media(self, endpoint, files=None, data=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        start_time = time.time()
        logging.debug(f"Sending POST request to {url}")
        response = requests.post(url, headers=headers, files=files, data=data, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "POST", "headers": headers, "time_duration": time_duration}

    def post_statuses(self, endpoint, data=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        headers["content-type"] = "application/json"
        start_time = time.time()
        logging.debug(f"Sending POST request to {url}")
        response = requests.post(url, headers=headers, json=data, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "POST", "headers": headers, "time_duration": time_duration}

    def get_status_by_id(self, endpoint, params=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        start_time = time.time()
        logging.debug(f"Sending GET request to {url}")
        response = requests.get(url, headers=headers, params=params, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "GET", "headers": headers, "time_duration": time_duration}

    def delete_status_by_id(self, endpoint, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        start_time = time.time()
        logging.debug(f"Sending DELETE request to {url}")
        response = requests.delete(url, headers=headers, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "DELETE", "headers": headers, "time_duration": time_duration}

    def patch(self, endpoint, files=None, data=None, custom_headers=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(custom_headers)
        start_time = time.time()
        logging.debug(f"Sending PATCH request to {url}")
        response = requests.patch(url, headers=headers, files=files, data=data, allow_redirects=True)
        end_time = time.time()
        time_duration = self.get_time_duration(start_time, end_time)
        logging.debug(f"Received response from {url} with status {response.status_code}, duration {time_duration:.2f} ms")
        return response, {"url": url, "method": "PATCH", "headers": headers, "time_duration": time_duration}