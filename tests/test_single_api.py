# tests/test_single_api.py
import pytest
from .utils.api_client import APIClient
from .utils.report_generator import ReportGenerator

@pytest.fixture(scope="session")
def api_client(pytestconfig):
    env = pytestconfig.getoption("--env")
    import yaml
    with open("config/env_config.yaml") as f:
        config = yaml.safe_load(f)[env]
    return APIClient(config["base_url"], config["auth_token"])

@pytest.fixture(scope="session")
def reporter():
    return ReportGenerator()

@pytest.mark.env("lab")
@pytest.mark.env("staging")
@pytest.mark.env("prod")
def test_get_me(api_client, reporter):
    response = api_client.get("api/v1/me")
    test_name = "test_get_me"
    
    try:
        assert response.status_code == 200
        assert "user" in response.json()
        reporter.add_result(test_name, "PASS", response.status_code)
    except AssertionError:
        reporter.add_result(test_name, "FAIL", response.status_code)
        raise