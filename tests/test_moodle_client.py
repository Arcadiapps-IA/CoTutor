import json
from unittest.mock import patch
import requests

from co_tutor.moodle.client import MoodleClient, MoodleAPIError
from co_tutor.moodle import services


def _fake_response(json_data, status_code=200):
    class FakeResp:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise requests.HTTPError(f"Status {self.status_code}")

        def json(self):
            return self._json

    return FakeResp(json_data, status_code)


@patch("requests.post")
def test_call_api_success(mock_post):
    mock_post.return_value = _fake_response({"courses": [{"id": 1, "fullname": "Test"}]})
    client = MoodleClient(base_url="https://moodle.test", token="tok")
    res = client.call_api("core_course_get_courses", {})
    assert isinstance(res, dict)
    assert "courses" in res


@patch("requests.post")
def test_call_api_moodle_error(mock_post):
    # Moodle error response contains 'exception'
    mock_post.return_value = _fake_response({"exception": "dberror", "errorcode": "dberror"})
    client = MoodleClient(base_url="https://moodle.test", token="tok")
    try:
        client.call_api("core_course_get_courses", {})
        assert False, "Expected MoodleAPIError"
    except MoodleAPIError:
        pass


@patch("requests.post")
def test_get_courses_service(mock_post):
    mock_post.return_value = _fake_response({"courses": [{"id": 2, "fullname": "C2"}]})
    client = MoodleClient(base_url="https://moodle.test", token="tok")
    res = services.get_courses(client)
    assert "courses" in res
