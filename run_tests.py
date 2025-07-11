# run_tests.py
import pytest
import argparse
from tests.utils.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Run API tests with environment selection")
    parser.add_argument("--env", default="develop", 
                      choices=['dev', 'staging', 'prod', 'qa', 'rc', 'develop', 'production', 
                              'performance', 'replica', 'fedramp', 'offline', 'online', 'master', 
                              'remote', 'legacy', 'local', 'alpha', 'beta', 'demo', 'gdpr', 'main', 
                              'test', 'gov', 'new', 'old', 'uat'],
                      help="Environment to run tests against")
    args = parser.parse_args()

    pytest_args = [
        "-m", f"env('{args.env}')",
        "--env", args.env,
        "-v"
    ]
    
    reporter = ReportGenerator()
    pytest.main(pytest_args)
    reporter.generate_xlsx(f"test_report_{args.env}.xlsx")
    reporter.generate_html(f"test_report_{args.env}.html")

if __name__ == "__main__":
    main()