import pytest
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import argparse
from config.config import REPORTS_DIR, load_environment_config

# Danh sách lưu kết quả kiểm thử
test_results = []

def generate_html_report(environment):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report_template.html")
    
    status_counts = {}
    for result in test_results:
        status_code = str(result.get("status_code", "N/A"))
        status_counts[status_code] = status_counts.get(status_code, 0) + 1
    
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
    parser = argparse.ArgumentParser(description="API Test Suite")
    parser.add_argument(
        "--env",
        default="dev",
        choices=[
            "lab", "dev", "staging", "production"
        ],
        help="Environment to test"
    )
    parser.add_argument("--tests", help="Run specific tests matching this keyword expression (e.g., 'test_get_users')")
    args = parser.parse_args()

    try:
        env_config = load_environment_config(args.env)
        env_config["name"] = args.env
    except KeyError as e:
        print(f"Lỗi: Môi trường '{args.env}' không được định nghĩa trong config/environments.yaml")
        exit(1)

    if not os.path.exists("tests/test_api.py"):
        print("Lỗi: Không tìm thấy file tests/test_api.py")
        exit(1)

    pytest_args = ["-v", "tests/test_api.py"]
    if args.tests:
        pytest_args.append(f"-k {args.tests}")

    pytest_args.append(f"--env={args.env}")

    result = pytest.main(pytest_args)
    
    if result == 0 and test_results:
        html_report = generate_html_report(args.env)
        xlsx_report = generate_xlsx_report(args.env)
        print(f"Báo cáo HTML được tạo: {html_report}")
        print(f"Báo cáo XLSX được tạo: {xlsx_report}")
    else:
        print("Không có kiểm thử nào được thực thi hoặc có lỗi xảy ra.")