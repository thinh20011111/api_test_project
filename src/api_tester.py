import requests
import uuid
from datetime import datetime

def perform_api_test(env_config, endpoint, method="GET", payload=None, headers=None, expected_status=200):
    """Hàm kiểm thử API cơ bản"""
    result = {
        "test_id": str(uuid.uuid4()),
        "endpoint": endpoint,
        "method": method,
        "status_code": None,
        "response_time": None,
        "success": False,
        "error_message": None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": env_config.get("name", "unknown")
    }
    
    try:
        start_time = datetime.now()
        response = requests.request(
            method=method,
            url=f"{env_config['api_base_url']}{endpoint}",
            json=payload,
            headers=headers,
            timeout=env_config["timeout"]
        )
        end_time = datetime.now()
        
        result["status_code"] = response.status_code
        result["response_time"] = (end_time - start_time).total_seconds() * 1000  # ms
        result["success"] = response.status_code == expected_status
        result["response_content"] = response.text[:500]  # Giới hạn nội dung phản hồi
        
    except requests.exceptions.RequestException as e:
        result["error_message"] = str(e)
    
    return result