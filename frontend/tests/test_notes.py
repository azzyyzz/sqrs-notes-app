import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import streamlit as st
import requests
import app as notes_app

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNotes(unittest.TestCase):

    def setUp(self):
        st.session_state.clear()
        st.session_state.token = "test_token"
        st.session_state.username = "testuser"
        st.session_state.cookie_manager = MagicMock()

    @patch("app.requests.post")
    @patch("app.st.form")
    @patch("app.st.text_input")
    @patch("app.st.text_area")
    @patch("app.st.form_submit_button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_create_note_success(
        self,
        mock_error,
        mock_success,
        mock_submit,
        mock_text_area,
        mock_text_input,
        mock_form,
        mock_post,
    ):
        mock_form.return_value.__enter__.return_value = None
        mock_text_input.return_value = "Test Title"
        mock_text_area.return_value = "Test Content"
        mock_submit.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch("app.requests.get") as mock_get:
            mock_get.return_value = MagicMock()
            mock_get.return_value.json.return_value = []

            with patch("app.st.button") as mock_button:
                mock_button.return_value = False
                notes_app.notes_app()

                mock_post.assert_called_once()
                mock_success.assert_called_once()
                mock_error.assert_not_called()

    @patch("app.requests.post")
    @patch("app.st.form")
    @patch("app.st.text_input")
    @patch("app.st.text_area")
    @patch("app.st.form_submit_button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_create_note_failure(
        self,
        mock_error,
        mock_success,
        mock_submit,
        mock_text_area,
        mock_text_input,
        mock_form,
        mock_post,
    ):
        mock_form.return_value.__enter__.return_value = None
        mock_text_input.return_value = "Test Title"
        mock_text_area.return_value = "Test Content"
        mock_submit.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with patch("app.requests.get") as mock_get:
            mock_get.return_value = MagicMock()
            mock_get.return_value.json.return_value = []

            with patch("app.st.button") as mock_button:
                mock_button.return_value = False
                notes_app.notes_app()

                mock_post.assert_called_once()
                mock_error.assert_called_once()
                mock_success.assert_not_called()


    @patch("app.requests.get")
    @patch("app.st.error")
    def test_list_notes_error(self, mock_error, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        with patch("app.st.form") as mock_form:
            mock_form.return_value.__enter__.return_value = None

            with patch("app.st.button") as mock_button:
                mock_button.return_value = False
                notes_app.notes_app()

                mock_get.assert_called_once()
                mock_error.assert_called_once_with("Could not load notes")

    @patch("app.requests.get")
    @patch("app.requests.delete")
    @patch("app.st.expander")
    @patch("app.st.success")
    @patch("app.st.error")
    @patch("app.st.rerun")
    def test_delete_note_success(
        self,
        mock_rerun,
        mock_error,
        mock_success,
        mock_expander,
        mock_delete,
        mock_get,
    ):
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = [
            {"id": 1, "title": "Note 1", "content": "Content 1"}
        ]
        mock_expander.return_value.__enter__.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        with patch("app.st.form") as mock_form:
            mock_form.return_value.__enter__.return_value = None

            with patch("app.st.columns") as mock_columns:
                col1, col2 = MagicMock(), MagicMock()
                mock_columns.return_value = [col1, col2]

                with patch("app.st.button") as mock_button:
                    mock_button.side_effect = [False, False, True, False]

                    with patch("app.st.write"):
                        notes_app.notes_app()
                        mock_delete.assert_called_once()
                        mock_success.assert_called_once()
                        mock_error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
