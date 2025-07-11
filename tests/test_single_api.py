# tests/test_single_api.py
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
def test_get_me(api_client, reporter):
    response, request_info = api_client.get("api/v1/me")
    test_name = "test_get_me"
    
    try:
        assert response.status_code == 200
        assert "acct" in response.json()  # Kiểm tra key 'acct'
        assert response.json()["acct"] == "hungnguyen12e"  # Kiểm tra giá trị cụ thể
        reporter.add_result(test_name, "PASS", response.status_code, request_info, response.json())
        logging.debug(f"test_get_me: Added result for PASS")
    except AssertionError:
        reporter.add_result(test_name, "FAIL", response.status_code, request_info, response.json())
        logging.debug(f"test_get_me: Added result for FAIL")
        raise