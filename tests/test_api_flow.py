# tests/test_api_flow.py
import pytest
import os
from .utils.api_client import APIClient
from .utils.report_generator import ReportGenerator
import logging

@pytest.fixture(scope="session")
def api_client():
    env = os.getenv("ENV", "develop")
    import yaml
    with open("config/env_config.yaml") as f:
        config = yaml.safe_load(f)[env]
    logging.debug(f"APIClient initialized with env: {env}, base_url: {config['base_url']}")
    return APIClient(config["base_url"], config["auth_token"])

@pytest.fixture(scope="session")
def reporter():
    return ReportGenerator()

@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_user_flow(api_client, reporter):
    test_name = "test_user_flow"
    
    try:
        # Bước 1: Get user info
        get_response, get_request_info = api_client.get("api/v1/me")
        assert get_response.status_code == 200
        assert "acct" in get_response.json()
        reporter.add_result(test_name, "PASS", get_response.status_code, get_request_info, get_response.json())
        logging.debug(f"test_user_flow: Added result for PASS")
    except AssertionError as e:
        reporter.add_result(test_name, "FAIL", get_response.status_code, get_request_info, get_response.json())
        logging.debug(f"test_user_flow: Added result for FAIL")
        raise