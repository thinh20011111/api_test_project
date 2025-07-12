# run_tests.py
import pytest
import argparse
from tests.utils.report_generator import ReportGenerator
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Run API tests with environment selection")
    parser.add_argument("--env", default="develop", 
                       choices=['dev', 'develop', 'staging', 'prod', 'qa', 'rc', 'production', 
                                'performance', 'replica', 'fedramp', 'offline', 'online', 'master', 
                                'remote', 'legacy', 'local', 'alpha', 'beta', 'demo', 'gdpr', 'main', 
                                'test', 'gov', 'new', 'old', 'uat'],
                       help="Environment to run tests against")
    args = parser.parse_args()

    # Đặt biến môi trường ENV
    os.environ["ENV"] = args.env

    pytest_args = [
        "-m", f"env_{args.env}",
        "-v", "-s",
        "tests/test_single_api.py",
    ]
        # "tests/test_api_flow.py"
    
    reporter = ReportGenerator()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.debug(f"Starting pytest with args: {pytest_args}")
    exit_code = pytest.main(pytest_args)
    logging.debug(f"Pytest exit code: {exit_code}")
    logging.debug(f"Generating reports for env: {args.env}, timestamp: {timestamp}")
    xlsx_file = reporter.generate_xlsx(args.env, timestamp)
    html_file = reporter.generate_html(args.env, timestamp)
    logging.debug(f"Generated reports: XLSX={xlsx_file}, HTML={html_file}")

if __name__ == "__main__":
    main()