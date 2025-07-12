Cấu trúc dự án
api_test_project/
│
├── config/
│   └── env_config.yaml        # Cấu hình cho các môi trường khác nhau
├── reports/
│   ├── html/                  # Báo cáo HTML
│   ├── xlsx/                  # Báo cáo XLSX
│   └── json/                  # Kết quả kiểm thử dạng JSON
├── tests/
│   ├── __init__.py
│   ├── test_api_flow.py       # Test case cho luồng người dùng
│   ├── test_single_api.py     # Test case cho yêu cầu API đơn lẻ
│   └── utils/
│       ├── __init__.py
│       ├── api_client.py      # Client để gọi API HTTP
│       ├── report_generator.py # Logic tạo báo cáo
│       └── custom_marks.py    # Marker tùy chỉnh cho pytest (nếu có)
├── pytest.ini                 # Cấu hình pytest
├── requirements.txt           # Danh sách thư viện Python yêu cầu
└── run_tests.py              # Script để chạy test

1, Cài đặt
pip install -r requirements.txt

2, Cấu hình môi trường
develop:
  base_url: "https://lab-sn.emso.vn"
  auth_token: "3HoprhqqTHNNS7JvqWh2_CMKtJKK2FsQYslLSnTFzHs"

3, Chạy test
python run_tests.py --env=develop

4, Thêm API mới
- Thêm phương thức vào APIClient: tests/utils/api_client.py
ví dụ: 

def update_user(self, endpoint, user_id, data=None, custom_headers=None):
    url = f"{self.base_url}/{endpoint}/{user_id}"
    headers = self.get_headers(custom_headers)
    response = requests.post(url, headers=headers, json=data)
    return response, {"url": url, "method": "POST", "headers": headers}

- Thêm test case: tests/test_single_api.py
ví dụ: 

@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_update_user(api_client, reporter):
    test_name = "test_update_user"
    update_data = {
        "name": "Nguyen Van A",
        "email": "nguyenvana@example.com"
    }
    user_id = "108813322749055123"  # Thay bằng user_id thực tế
    response, request_info = api_client.update_user("api/v1/user/update", user_id, data=update_data)
    try:
        assert response.status_code == 200
        assert "success" in response.json()
        assert response.json()["success"] is True
        reporter.add_result(test_name, "PASS", response.status_code, request_info, response.json())
        logging.debug(f"test_update_user: Added result for PASS")
    except AssertionError:
        reporter.add_result(test_name, "FAIL", response_code, request_info, response.json())
        logging.debug(f"test_update_user: Added result for FAIL")
        raise


5, Chạy Flow với API lồng nhau
Để chạy một flow mà API này sử dụng dữ liệu từ API khác (ví dụ: lấy user_id từ GET /api/v1/me để gọi POST /api/v1/user/update), làm theo các bước sau:
- Cập nhật test_api_flow.py:

@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_user_flow(api_client, reporter):
    test_name = "test_user_flow"
    try:
        # Bước 1: Get user info để lấy user_id
        get_response, get_request_info = api_client.get("api/v1/me")
        assert get_response.status_code == 200
        assert "id" in get_response.json()
        user_id = get_response.json()["id"]
        reporter.add_result(f"{test_name}_get_me", "PASS", get_response.status_code, get_request_info, get_response.json())
        logging.debug(f"test_user_flow: Added result for GET /me PASS")
        # Bước 2: Update user info với user_id
        update_data = {
            "name": "Nguyen Van A",
            "email": "nguyenvana@example.com"
        }
        update_response, update_request_info = api_client.update_user("api/v1/user/update", user_id, data=update_data)
        assert update_response.status_code == 200
        assert "success" in update_response.json()
        assert update_response.json()["success"] is True
        reporter.add_result(f"{test_name}_update_user", "PASS", update_response.status_code, update_request_info, update_response.json())
        logging.debug(f"test_user_flow: Added result for POST /user/update PASS")
    except AssertionError as e:
        if "get_response" in locals():
            reporter.add_result(f"{test_name}_get_me", "FAIL", get_response.status_code, get_request_info, get_response.json())
            logging.debug(f"test_user_flow: Added result for GET /me FAIL")
        if "update_response" in locals():
            reporter.add_result(f"{test_name}_update_user", "FAIL", update_response.status_code, update_request_info, update_response.json())
            logging.debug(f"test_user_flow: Added result for POST /user/update FAIL")
        raise

Chạy riêng 1 api
pytest -m env_develop -v -s tests/test_single_api.py::test_post_example


AI GROK 
https://grok.com/share/c2hhcmQtMg%3D%3D_6c5f6975-28c6-48cb-8def-84f0ff3458dd
paste curl và promt "Hãy thêm giúp tôi api này (nếu có: id sẽ được lấy từ api abc)"
