import re
import json
import os
import argparse
import logging
from datetime import datetime

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_curl_file(curl_file):
    """Đọc và phân tích file curl.txt để trích xuất phương thức, endpoint, headers, body."""
    try:
        with open(curl_file, 'r', encoding='utf-8') as f:
            curl_command = f.read().strip()
        
        # Trích xuất phương thức HTTP
        method_match = re.search(r'curl\s+-X\s+(\w+)', curl_command)
        method = method_match.group(1) if method_match else 'GET'

        # Trích xuất URL và endpoint
        url_match = re.search(r'curl\s+[\'"]?([^\s\'"]+)[\'"]?', curl_command)
        if not url_match:
            raise ValueError("Không tìm thấy URL trong lệnh curl")
        full_url = url_match.group(1)
        endpoint = full_url.split('/api/')[-1] if '/api/' in full_url else full_url.split('/')[-1]

        # Trích xuất headers
        headers = {}
        header_matches = re.findall(r'-H\s+[\'"]?([^\'"]+)[\'"]?', curl_command)
        for header in header_matches:
            key, value = header.split(': ', 1)
            headers[key.strip()] = value.strip()

        # Trích xuất body (nếu có)
        body_match = re.search(r'-d\s+[\'"]?(\{.*?\})[\'"]?', curl_command, re.DOTALL)
        body = json.loads(body_match.group(1)) if body_match else None

        logging.debug(f"Parsed curl: method={method}, endpoint={endpoint}, headers={headers}, body={body}")
        return {
            'method': method.upper(),
            'endpoint': endpoint,
            'headers': headers,
            'body': body,
            'full_url': full_url
        }
    except Exception as e:
        logging.error(f"Lỗi khi phân tích file curl: {e}")
        raise

def update_api_client(api_info):
    """Cập nhật tests/utils/api_client.py để thêm phương thức mới nếu cần."""
    api_client_file = 'tests/utils/api_client.py'
    method_name = api_info['method'].lower()
    endpoint_name = api_info['endpoint'].replace('/', '_').replace('-', '_')
    
    # Đọc file api_client.py
    with open(api_client_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Kiểm tra xem phương thức đã tồn tại chưa
    if f'def {method_name}_{endpoint_name}' in content:
        logging.info(f"Phương thức {method_name}_{endpoint_name} đã tồn tại trong api_client.py")
        return

    # Tạo code cho phương thức mới
    new_method = f"""
    def {method_name}_{endpoint_name}(self, endpoint, data=None, custom_headers=None):
        url = f"{{self.base_url}}/{{endpoint}}"
        headers = self.get_headers(custom_headers)
        response = requests.{method_name}(url, headers=headers, json=data)
        return response, {{"url": url, "method": "{method_name.upper()}", "headers": headers}}
"""
    
    # Thêm phương thức vào trước dòng cuối cùng của class APIClient
    lines = content.splitlines()
    class_end_index = next(i for i, line in enumerate(lines) if line.startswith('class APIClient:'))
    for i in range(class_end_index + 1, len(lines)):
        if lines[i].startswith('class ') or i == len(lines) - 1:
            lines.insert(i, new_method)
            break

    # Ghi lại file
    with open(api_client_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logging.info(f"Đã thêm phương thức {method_name}_{endpoint_name} vào {api_client_file}")

def update_test_single_api(api_info):
    """Thêm test case mới vào tests/test_single_api.py."""
    test_file = 'tests/test_single_api.py'
    test_name = f"test_{api_info['method'].lower()}_{api_info['endpoint'].replace('/', '_').replace('-', '_')}"
    
    # Đọc file test_single_api.py
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Kiểm tra xem test case đã tồn tại chưa
    if f'def {test_name}' in content:
        logging.info(f"Test case {test_name} đã tồn tại trong test_single_api.py")
        return test_name

    # Tạo code cho test case mới
    body_str = json.dumps(api_info['body'], indent=4, ensure_ascii=False) if api_info['body'] else 'None'
    test_case = f"""
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_{api_info['method'].lower()}_{api_info['endpoint'].replace('/', '_').replace('-', '_')}(api_client, reporter):
    test_name = "{test_name}"
    data = {body_str}
    response, request_info = api_client.{api_info['method'].lower()}_{api_info['endpoint'].replace('/', '_').replace('-', '_')}("{api_info['endpoint']}", data=data)
    
    try:
        assert response.status_code == 200
        # Thêm các assertion tùy chỉnh dựa trên response thực tế
        reporter.add_result(test_name, "PASS", response.status_code, request_info, response.json())
        logging.debug(f"{test_name}: Added result for PASS")
    except AssertionError:
        reporter.add_result(test_name, "FAIL", response.status_code, request_info, response.json())
        logging.debug(f"{test_name}: Added result for FAIL")
        raise
"""
    
    # Thêm test case vào cuối file
    with open(test_file, 'a', encoding='utf-8') as f:
        f.write(test_case)
    logging.info(f"Đã thêm test case {test_name} vào {test_file}")
    return test_name

def main():
    parser = argparse.ArgumentParser(description="Thêm API mới từ file curl.txt vào dự án api_test_project")
    parser.add_argument('--curl-file', default='curl.txt', help="Đường dẫn đến file curl.txt")
    args = parser.parse_args()

    # Đọc và phân tích file curl
    api_info = parse_curl_file(args.curl_file)

    # Cập nhật api_client.py
    update_api_client(api_info)

    # Cập nhật test_single_api.py và lấy test_name
    test_name = update_test_single_api(api_info)

    # Hướng dẫn chạy test
    logging.info("Để chạy test mới, sử dụng lệnh:")
    logging.info(f"cd C:\\Users\\Thinh\\OneDrive\\Máy tính\\api_test_project\\api_test_project")
    logging.info(f"python run_tests.py --env=develop")
    logging.info("Hoặc chạy riêng test case mới:")
    logging.info(f"set ENV=develop")
    logging.info(f"pytest -m env_develop -v -s tests/test_single_api.py::{test_name}")

if __name__ == "__main__":
    main()