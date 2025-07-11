# run_tests.py
import pytest
import argparse
from tests.utils.report_generator import ReportGenerator
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Run API tests with environment selection")
    parser.add_argument("--env", default="dev", 
                      choices=['dev', 'develop', 'staging', 'prod', 'qa', 'rc', 'production', 
                              'performance', 'replica', 'fedramp', 'offline', 'online', 'master', 
                              'remote', 'legacy', 'local', 'alpha', 'beta', 'demo', 'gdpr', 'main', 
                              'test', 'gov', 'new', 'old', 'uat'],
                      help="Environment to run tests against")
    args = parser.parse_args()

    pytest_args = [
        "-m", f"env_{args.env}",
        "--env", args.env,
        "-v"
    ]
    
    reporter = ReportGenerator()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pytest.main(pytest_args)
    reporter.generate_xlsx(args.env, timestamp)
    reporter.generate_html(args.env, timestamp)

if __name__ == "__main__":
    main()