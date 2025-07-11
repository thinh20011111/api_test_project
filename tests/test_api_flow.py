# tests/test_api_flow.py
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

@pytest.mark.env("dev")
@pytest.mark.env("staging")
@pytest.mark.env("prod")
def test_user_flow(api_client, reporter):
    test_name = "test_user_flow"
    
    try:
        # Example flow: Get user info -> Update user info
        get_response = api_client.get("api/v1/me")
        assert get_response.status_code == 200
        user_id = get_response.json().get("user", {}).get("id")
        
        # Update user (example endpoint, adjust as needed)
        update_response = api_client.post(f"api/v1/users/{user_id}", 
                                        data={"name": "Updated User"},
                                        custom_headers={"x-custom-header": "test-value"})
        assert update_response.status_code == 200
        
        reporter.add_result(test_name, "PASS", 200)
    except AssertionError as e:
        reporter.add_result(test_name, "FAIL", locals().get("response", {}).get("status_code", "N/A"))
        raise