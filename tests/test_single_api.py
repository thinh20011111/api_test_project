import pytest
import yaml
import os
from .utils.api_client import APIClient
from .utils.report_generator import ReportGenerator
import logging
import requests

# Biến toàn cục để lưu MEDIA_ID và STATUS_ID
MEDIA_ID = None
STATUS_ID = None

@pytest.fixture(scope="session")
def api_client():
    env = os.getenv("ENV", "develop")
    with open("config/env_config.yaml") as f:
        config = yaml.safe_load(f)[env]
    logging.debug(f"APIClient initialized with env: {env}, base_url: {config['base_url']}")
    return APIClient(config["base_url"], config["auth_token"])

@pytest.fixture(scope="session")
def reporter():
    return ReportGenerator()

# Test get user info
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_get_me(api_client, reporter):
    test_name = "test_get_me"
    response, request_info = api_client.get("api/v1/me")
    try:
        assert response.status_code == 200
        assert "acct" in response.json()  # Kiểm tra key 'acct'
        final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, "FAIL", response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for FAIL due to assertion failure: {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, "FAIL", 0, None,
            {"url": f"{api_client.base_url}/api/v1/me", "method": "GET", "headers": {}, "time_duration": 0}
        )
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise

# Test post media
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(name="post_media")
def test_post_media(api_client, reporter):
    global MEDIA_ID
    test_name = "test_post_media"
    logging.debug(f"Starting {test_name}")
    file_path = "media/image_1.jpg"  # Đảm bảo file này tồn tại
    try:
        assert os.path.exists(file_path), f"File {file_path} not found"
        with open(file_path, "rb") as file:
            files = {"file": ("image_1.jpg", file, "image/jpeg")}
            response, request_info = api_client.post_media("api/v1/media", files=files)
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found"
                assert "type" in response_json, "Key 'type' not found"
                assert response_json["type"] == "image", "Expected type to be 'image'"
                MEDIA_ID = response_json["id"]
                logging.debug(f"{test_name}: Extracted media_id: {MEDIA_ID}")
                final_status = "PASS"
            except ValueError:
                final_status = "FAIL"
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, response, request_info)
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/media", "method": "POST", "headers": {}, "time_duration": 0}
        )
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/media", "method": "POST", "headers": {}, "time_duration": 0}
        )
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise

# Test update avatar
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(depends=["post_media"])
def test_update_avatar(api_client, reporter):
    global MEDIA_ID
    test_name = "test_update_avatar"
    logging.debug(f"Starting {test_name}")
    try:
        assert MEDIA_ID is not None, "MEDIA_ID not set from test_post_media"
        data = {"avatar[status]": "", "avatar[id]": str(MEDIA_ID)}
        response, request_info = api_client.patch("api/v1/accounts/update_credentials", data=data)
        final_status = "FAIL"  # Giả định thất bại ban đầu
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                # Cập nhật kiểm tra dựa trên phản hồi thực tế
                assert "success" in response_json and response_json["success"] is True, "API did not return success"
                final_status = "PASS"
            except ValueError:
                raise AssertionError("Response is not JSON")
            except AssertionError as e:
                logging.debug(f"{test_name}: Assertion failed - {str(e)}")
                raise
        except AssertionError as e:
            logging.debug(f"{test_name}: HTTP status check failed - {str(e)}")
            raise
    except AssertionError as e:
        reporter.add_result(test_name, final_status, response.status_code if 'response' in locals() else 0, response if 'response' in locals() else None, request_info if 'request_info' in locals() else {"url": f"{api_client.base_url}/api/v1/accounts/update_credentials", "method": "PATCH", "headers": {}, "time_duration": 0})
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        reporter.add_result(test_name, "FAIL", 0, None, {"url": f"{api_client.base_url}/api/v1/accounts/update_credentials", "method": "PATCH", "headers": {}, "time_duration": 0})
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise
    else:
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")

# Test post statuses
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(name="post_statuses", depends=["post_media"])
def test_post_statuses(api_client, reporter):
    global STATUS_ID, MEDIA_ID
    test_name = "test_post_statuses"
    logging.debug(f"Starting {test_name}")
    try:
        assert MEDIA_ID is not None, "MEDIA_ID not set"
        data = {
            "media_ids": [MEDIA_ID],
            "sensitive": False,
            "visibility": "public",
            "status": "Hello cả nhà iu",
            "place_id": "108277159419224039",
            "status_activity_id": 212
        }
        response, request_info = api_client.post_statuses("api/v1/statuses", data=data)
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found"
                assert "content" in response_json, "Key 'content' not found"
                assert response_json["content"] == "Hello cả nhà iu", "Expected content to be 'Hello cả nhà iu'"
                STATUS_ID = response_json["id"]
                logging.debug(f"{test_name}: Extracted status_id: {STATUS_ID}")
                final_status = "PASS"
            except ValueError:
                final_status = "FAIL"
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, response, request_info)
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses", "method": "POST", "headers": {}, "time_duration": 0}
        )
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses", "method": "POST", "headers": {}, "time_duration": 0}
        )
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise

# Test get status by ID
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(depends=["post_statuses"])
def test_get_status_by_id(api_client, reporter):
    global STATUS_ID
    test_name = "test_get_status_by_id"
    logging.debug(f"Starting {test_name}")
    try:
        assert STATUS_ID is not None, "STATUS_ID not set from test_post_statuses"
        endpoint = f"api/v1/statuses/{STATUS_ID}"
        response, request_info = api_client.get_status_by_id(endpoint)
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found"
                assert response_json["id"] == STATUS_ID, f"Expected id to be {STATUS_ID}"
                assert "content" in response_json, "Key 'content' not found"
                assert response_json["content"] == "Hello cả nhà iu", "Expected content to be 'Hello cả nhà iu'"
                final_status = "PASS"
            except ValueError:
                final_status = "FAIL"
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, response, request_info)
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses/{STATUS_ID}", "method": "GET", "headers": {}, "time_duration": 0}
        )
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses/{STATUS_ID}", "method": "GET", "headers": {}, "time_duration": 0}
        )
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise

# Test delete status by ID
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(depends=["post_statuses"])
def test_delete_status_by_id(api_client, reporter):
    global STATUS_ID
    test_name = "test_delete_status_by_id"
    logging.debug(f"Starting {test_name}")
    try:
        assert STATUS_ID is not None, "STATUS_ID not set from test_post_statuses"
        endpoint = f"api/v1/statuses/{STATUS_ID}"
        response, request_info = api_client.delete_status_by_id(endpoint)
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            final_status = "PASS"
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, response, request_info)
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
        reporter.add_result(test_name, final_status, response.status_code, response, request_info)
        logging.debug(f"{test_name}: Added result for {final_status}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses/{STATUS_ID}", "method": "DELETE", "headers": {}, "time_duration": 0}
        )
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(
            test_name, final_status, 0, None,
            {"url": f"{api_client.base_url}/api/v1/statuses/{STATUS_ID}", "method": "DELETE", "headers": {}, "time_duration": 0}
        )
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise