import pytest
from src.api_tester import perform_api_test
from main import test_results

def test_get_status(env_config):
    # Test API với token cụ thể
    custom_headers = {"Authorization": "Bearer Pno6CeK44Y5KCiF8Qul0vd99ojmzNWxJtLiHM14KMJg"}
    result = perform_api_test(env_config, "/statuses/114809714727261565", method="GET", expected_status=200, custom_headers=custom_headers)
    test_results.append(result)
    assert result["success"], f"Kiểm thử thất bại: {result['error_message']}"