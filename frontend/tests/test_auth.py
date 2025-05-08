import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import streamlit as st
import requests
import app as notes_app

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAuth(unittest.TestCase):

    def setUp(self):
        st.session_state.clear()
        st.session_state.cookie_manager = MagicMock()

    @patch("app.requests.post")
    @patch("app.time.sleep")
    @patch("app.st.text_input")
    @patch("app.st.button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_login_success(
        self,
        mock_error,
        mock_success,
        mock_button,
        mock_text_input,
        mock_sleep,
        mock_post,
    ):
        mock_text_input.side_effect = ["testuser", "password"]
        mock_button.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "fake_token"}
        mock_post.return_value = mock_response

        notes_app.login()

        mock_post.assert_called_once()
        self.assertEqual(st.session_state.token, "fake_token")
        self.assertEqual(st.session_state.username, "testuser")
        mock_success.assert_called_once()
        mock_error.assert_not_called()

    @patch("app.requests.post")
    @patch("app.st.text_input")
    @patch("app.st.button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_login_failure(
        self, mock_error, mock_success, mock_button, mock_text_input, mock_post
    ):
        mock_text_input.side_effect = ["testuser", "wrong_password"]
        mock_button.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        notes_app.login()

        mock_post.assert_called_once()
        mock_error.assert_called_once()
        mock_success.assert_not_called()
        self.assertNotIn("token", st.session_state)

    @patch("app.requests.post")
    @patch("app.st.text_input")
    @patch("app.st.button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_login_exception(
        self, mock_error, mock_success, mock_button, mock_text_input, mock_post
    ):
        mock_text_input.side_effect = ["testuser", "password"]
        mock_button.return_value = True
        mock_post.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        notes_app.login()

        mock_post.assert_called_once()
        mock_error.assert_called_once_with("Could not connect to the server")
        mock_success.assert_not_called()
        self.assertNotIn("token", st.session_state)

    @patch("app.requests.get")
    def test_check_login_valid(self, mock_get):
        st.session_state.cookie_manager.get_all.return_value = {
            "auth_token": "test_token"
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"username": "testuser"}
        mock_get.return_value = mock_response

        result = notes_app.check_login()

        self.assertTrue(result)
        self.assertEqual(st.session_state.token, "test_token")
        self.assertEqual(st.session_state.username, "testuser")

    @patch("app.requests.get")
    def test_check_login_invalid(self, mock_get):
        st.session_state.cookie_manager.get_all.return_value = {
            "auth_token": "invalid_token"
        }
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = notes_app.check_login()
        self.assertFalse(result)

    @patch("app.requests.get")
    def test_check_login_exception(self, mock_get):
        st.session_state.cookie_manager.get_all.return_value = {
            "auth_token": "test_token"
        }
        mock_get.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        result = notes_app.check_login()
        self.assertFalse(result)

    @patch("app.time.sleep")
    @patch("app.st.rerun")
    def test_logout(self, mock_rerun, mock_sleep):
        st.session_state.token = "test_token"
        st.session_state.username = "testuser"
        cookie_manager_mock = MagicMock()
        st.session_state.cookie_manager = cookie_manager_mock

        notes_app.logout()

        cookie_manager_mock.delete.assert_called_once_with("auth_token")
        mock_sleep.assert_called_once()
        mock_rerun.assert_called_once()

    @patch("app.requests.post")
    @patch("app.st.text_input")
    @patch("app.st.button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_signup_success(
        self, mock_error, mock_success, mock_button, mock_text_input, mock_post
    ):
        mock_text_input.side_effect = ["new_user", "password"]
        mock_button.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notes_app.signup()

        mock_post.assert_called_once()
        mock_success.assert_called_once()
        mock_error.assert_not_called()

    @patch("app.requests.post")
    @patch("app.st.text_input")
    @patch("app.st.button")
    @patch("app.st.success")
    @patch("app.st.error")
    def test_signup_failure(
        self, mock_error, mock_success, mock_button, mock_text_input, mock_post
    ):
        mock_text_input.side_effect = ["existing_user", "password"]
        mock_button.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Username already exists"}
        mock_post.return_value = mock_response

        notes_app.signup()

        mock_post.assert_called_once()
        mock_error.assert_called_once()
        mock_success.assert_not_called()

    @patch("app.st.tabs")
    @patch("app.check_login")
    def test_main_not_logged_in(self, mock_check_login, mock_tabs):
        mock_check_login.return_value = False
        tab1, tab2 = MagicMock(), MagicMock()
        mock_tabs.return_value = [tab1, tab2]

        with patch("app.login") as mock_login:
            with patch("app.signup") as mock_signup:
                notes_app.main()
                mock_login.assert_called_once()
                mock_signup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
