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

# Test get user info
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_get_me(api_client, reporter):
    response, request_info = api_client.get("api/v1/me")
    test_name = "test_get_me"
    
    try:
        # Kiểm tra assertion
        assert response.status_code == 200
        assert "acct" in response.json()  # Kiểm tra key 'acct'
        final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
        reporter.add_result(test_name, final_status, response.status_code, request_info, response.json())
        logging.debug(f"test_get_me: Added result for {final_status}")
    except AssertionError as e:
        final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"  # Dựa vào response_code
        reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": str(e), **response.json()})
        logging.debug(f"test_get_me: Added result for {final_status} due to assertion failure: {str(e)}")
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
    file_path = "media/image_1.jpg"  # Đảm bảo file này tồn tại trong thư mục dự án
    try:
        assert os.path.exists(file_path), f"File {file_path} not found in project directory"
        with open(file_path, "rb") as file:
            files = {
                "file": ("image_1.jpg", file, "image/jpeg")
            }
            data = {
                "position": "1"
            }
            response, request_info = api_client.post_media("api/v1/media", files=files, data=data)
        
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found in response"
                assert "type" in response_json, "Key 'type' not found in response"
                assert response_json["type"] == "image", "Expected type to be 'image'"
                # Lấy và lưu media_id
                media_id = response_json["id"]
                MEDIA_ID = media_id
                logging.debug(f"{test_name}: Extracted media_id: {media_id}")
                response_json["extracted_media_id"] = media_id
                final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, response_json)
                logging.debug(f"{test_name}: Added result for {final_status}")
            except ValueError:
                final_status = "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": "Response is not JSON"})
                logging.debug(f"{test_name}: Added result for {final_status} - Response is not JSON")
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": str(e)})
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "POST", "headers": "N/A"}, {"error": str(e)})
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "POST", "headers": "N/A"}, {"error": f"Unexpected error: {str(e)}"})
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise

# Test post statuses
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
@pytest.mark.dependency(name="post_statuses")
def test_post_statuses(api_client, reporter):
    global MEDIA_ID, STATUS_ID
    test_name = "test_post_statuses"
    try:
        assert MEDIA_ID is not None, "MEDIA_ID not set from test_post_media"
        data = {
            "id": None,
            "media_ids": [MEDIA_ID],
            "sensitive": False,
            "visibility": "public",
            "extra_body": {},
            "life_event": None,
            "poll": None,
            "place_id": "108277159419224039",
            "status_background_id": None,
            "mention_ids": None,
            "reblog_of_id": None,
            "post_type": None,
            "page_id": None,
            "page_owner_id": None,
            "event_id": None,
            "project_id": None,
            "recruit_id": None,
            "course_id": None,
            "status_question": None,
            "status_target": None,
            "tags": [],
            "status": "Hello cả nhà iu",
            "scheduled_at": None,
            "status_activity_id": 212
        }
        response, request_info = api_client.post_statuses("api/v1/statuses", data=data)
        
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found in response"
                assert "content" in response_json, "Key 'content' not found in response"
                assert response_json["content"] == "Hello cả nhà iu", "Expected content to be 'Hello cả nhà iu'"
                assert "media_attachments" in response_json, "Key 'media_attachments' not found in response"
                assert any(m["id"] == MEDIA_ID for m in response_json["media_attachments"]), f"MEDIA_ID {MEDIA_ID} not found in media_attachments"
                STATUS_ID = response_json["id"]  # Lưu status_id
                logging.debug(f"{test_name}: Extracted status_id: {STATUS_ID}")
                response_json["extracted_status_id"] = STATUS_ID
                final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, response_json)
                logging.debug(f"{test_name}: Added result for {final_status}")
            except ValueError:
                final_status = "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": "Response is not JSON"})
                logging.debug(f"{test_name}: Added result for {final_status} - Response is not JSON")
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": str(e)})
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "POST", "headers": "N/A"}, {"error": str(e)})
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "POST", "headers": "N/A"}, {"error": f"Unexpected error: {str(e)}"})
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
    try:
        assert STATUS_ID is not None, "STATUS_ID not set from test_post_statuses"
        endpoint = f"api/v1/statuses/{STATUS_ID}"
        response, request_info = api_client.get_status_by_id(endpoint)
        
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            try:
                response_json = response.json()
                assert "id" in response_json, "Key 'id' not found in response"
                assert response_json["id"] == STATUS_ID, f"Expected id to be {STATUS_ID}"
                assert "content" in response_json, "Key 'content' not found in response"
                assert response_json["content"] == "Hello cả nhà iu", "Expected content to be 'Hello cả nhà iu'"
                final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, response_json)
                logging.debug(f"{test_name}: Added result for {final_status}")
            except ValueError:
                final_status = "FAIL"
                reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": "Response is not JSON"})
                logging.debug(f"{test_name}: Added result for {final_status} - Response is not JSON")
                raise AssertionError("Response is not JSON")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": str(e)})
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "GET", "headers": "N/A"}, {"error": str(e)})
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "GET", "headers": "N/A"}, {"error": f"Unexpected error: {str(e)}"})
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
    try:
        assert STATUS_ID is not None, "STATUS_ID not set from test_post_statuses"
        endpoint = f"api/v1/statuses/{STATUS_ID}"
        response, request_info = api_client.delete_status_by_id(endpoint)
        
        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            # Không kiểm tra response body, coi 200 là thành công
            response_json = response.json() if response.content else {}
            final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, response_json)
            logging.debug(f"{test_name}: Added result for {final_status}")
        except AssertionError as e:
            final_status = "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, {"error": str(e)})
            logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
            raise
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "DELETE", "headers": "N/A"}, {"error": str(e)})
        logging.debug(f"{test_name}: Added result for {final_status} - {str(e)}")
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "DELETE", "headers": "N/A"}, {"error": f"Unexpected error: {str(e)}"})
        logging.error(f"{test_name}: Unexpected error - {str(e)}")
        raise
    
# Test update avatar
@pytest.mark.env_dev
@pytest.mark.env_develop
@pytest.mark.env_staging
@pytest.mark.env_prod
def test_update_credentials(api_client, reporter):
    global MEDIA_ID
    test_name = "test_update_credentials"
    try:
        # Gọi post_media để tạo MEDIA_ID
        file_path = "media/image_1.jpg"
        assert os.path.exists(file_path), f"File {file_path} not found"
        with open(file_path, "rb") as file:
            files = {"file": ("image_1.jpg", file, "image/jpeg")}
            data = {"position": "1"}
            response, request_info = api_client.post_media("api/v1/media", files=files, data=data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            MEDIA_ID = response.json()["id"]
            final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
            reporter.add_result(f"{test_name}_post_media", final_status, response.status_code, request_info, response.json())

        # Gọi update_credentials với token từ config
        data = {"avatar[id]": str(MEDIA_ID)}  # Loại bỏ avatar[status] nếu không cần
        custom_headers = {"content-type": "multipart/form-data"}
        with open(file_path, "rb") as file:
            files = {
                "avatar[id]": (None, str(MEDIA_ID)),  # Gửi ID như text
                "avatar[file]": ("image_1.jpg", file, "image/jpeg")  # Gửi file riêng
            }
            response, request_info = api_client.patch("api/v1/accounts/update_credentials", files=files, data=data, custom_headers=custom_headers)
            logging.debug(f"Response content: {response.content.decode('utf-8')}")
            logging.debug(f"Response headers: {dict(response.headers)}")
            response_body = {"raw_response": response.text} if response.text else {"no_response_body": True}
            final_status = "PASS" if 200 <= response.status_code < 300 else "FAIL"
            reporter.add_result(test_name, final_status, response.status_code, request_info, response_body)
            if response.status_code != 200:
                logging.warning(f"Server returned {response.status_code}: {response.text}")
    except AssertionError as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, getattr(response, "status_code", 0), request_info, {"error": str(e)})
        raise
    except Exception as e:
        final_status = "FAIL"
        reporter.add_result(test_name, final_status, 0, {"url": "N/A", "method": "PATCH"}, {"error": str(e)})
        raise