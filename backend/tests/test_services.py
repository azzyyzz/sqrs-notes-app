import pytest
from unittest.mock import patch
from app.services import translate_text


@patch("app.services.requests.post")
def test_translate_text_success(mock_post):
    mock_post.return_value.json.return_value = {
        "data": {"translations": {"translatedText": ["Привет"]}}
    }

    result = translate_text("Hello")
    assert result == "Привет"


@patch("app.services.requests.post", side_effect=Exception("API unavailable"))
def test_translate_text_failure(mock_post):
    with pytest.raises(Exception, match="Translation failed: API unavailable"):
        translate_text("Hello")
