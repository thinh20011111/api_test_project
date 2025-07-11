import requests
from time import time
from datetime import datetime

def perform_api_test(env_config, endpoint, method="GET", payload=None, expected_status=200, custom_headers=None):
    """
    Thực hiện kiểm thử API và trả về kết quả.
    
    Args:
        env_config (dict): Cấu hình môi trường từ environments.yaml
        endpoint (str): Đường dẫn endpoint (ví dụ: /users)
        method (str): Phương thức HTTP (GET, POST, etc.)
        payload (dict): Dữ liệu gửi đi (cho POST, PUT, etc.)
        expected_status (int): Mã trạng thái HTTP mong đợi
        custom_headers (dict): Header tùy chỉnh để ghi đè hoặc bổ sung
    
    Returns:
        dict: Kết quả kiểm thử
    """
    result = {
        "test_id": f"test_{endpoint.replace('/', '_')}_{method.lower()}",
        "environment": env_config.get("name", "unknown"),
        "endpoint": endpoint,
        "method": method,
        "status_code": None,
        "response_time": None,
        "success": False,
        "error_message": None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Lấy header từ cấu hình môi trường
    headers = env_config.get("headers", {}).copy()  # Copy để tránh thay đổi cấu hình gốc
    if custom_headers:
        headers.update(custom_headers)  # Ghi đè hoặc bổ sung header tùy chỉnh

    url = f"{env_config['api_base_url']}{endpoint}"
    start_time = time()
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload,
            timeout=env_config.get("timeout", 10)
        )
        result["status_code"] = response.status_code
        result["response_time"] = (time() - start_time) * 1000  # Chuyển sang mili giây
        result["success"] = response.status_code == expected_status
        if not result["success"]:
            result["error_message"] = f"Mã trạng thái không như mong đợi: nhận {response.status_code}, mong đợi {expected_status}"
    except requests.RequestException as e:
        result["error_message"] = str(e)
        result["status_code"] = None
        result["response_time"] = None
        result["success"] = False

    return result