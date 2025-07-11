import pytest
from src.api_tester import perform_api_test

# Lấy cấu hình môi trường từ pytest fixture
@pytest.fixture
def env_config(pytestconfig):
    return pytestconfig.env_config

def test_get_users(env_config):
    result = perform_api_test(env_config, "/users", expected_status=200)
    assert result["success"], f"Test failed: {result['error_message']}"

def test_create_user(env_config):
    payload = {"name": "Test User", "email": "test@example.com"}
    result = perform_api_test(env_config, "/users", method="POST", payload=payload, expected_status=201)
    assert result["success"], f"Test failed: {result['error_message']}"