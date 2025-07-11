import pytest
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import argparse
from config.config import REPORTS_DIR, load_environment_config
from src.api_tester import perform_api_test

# Danh sách lưu kết quả kiểm thử
test_results = []

def generate_html_report(environment):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report_template.html")
    
    # Tính toán dữ liệu cho biểu đồ
    status_counts = {
        "Success": sum(1 for result in test_results if result["success"]),
        "Failure": sum(1 for result in test_results if not result["success"])
    }
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(REPORTS_DIR, f"api_test_report_{environment}_{timestamp}.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template.render(results=test_results, environment=environment, status_counts=status_counts))
    return output_file

def generate_xlsx_report(environment):
    df = pd.DataFrame(test_results)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(REPORTS_DIR, f"api_test_report_{environment}_{timestamp}.xlsx")
    df.to_excel(output_file, index=False)
    return output_file

if __name__ == "__main__":
    # Xử lý tham số dòng lệnh
    parser = argparse.ArgumentParser(description="API Test Suite")
    parser.add_argument("--env", default="dev", choices=["dev", "staging", "production"], help="Environment to test")
    parser.add_argument("--tests", help="Run specific tests matching this keyword expression (e.g., 'test_get_users')")
    args = parser.parse_args()

    # Tải cấu hình môi trường
    env_config = load_environment_config(args.env)
    env_config["name"] = args.env  # Thêm tên môi trường vào config

    # Chuẩn bị tham số cho pytest
    pytest_args = ["-v", "tests/test_api.py", f"--env_config={env_config}"]
    if args.tests:
        pytest_args.append(f"-k {args.tests}")

    # Chạy các kiểm thử
    pytest.main(pytest_args)
    
    # Tạo báo cáo
    html_report = generate_html_report(args.env)
    xlsx_report = generate_xlsx_report(args.env)
    
    print(f"Báo cáo HTML được tạo: {html_report}")
    print(f"Báo cáo XLSX được tạo: {xlsx_report}")