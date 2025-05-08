import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import streamlit as st
import app as notes_app

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUtils(unittest.TestCase):

    def setUp(self):
        st.session_state.clear()

    @patch("app.stx.CookieManager")
    def test_init_cookie_manager(self, mock_cookie_manager):
        mock_instance = MagicMock()
        mock_cookie_manager.return_value = mock_instance

        notes_app.init_cookie_manager()
        self.assertIn("cookie_manager", st.session_state)
        self.assertEqual(st.session_state.cookie_manager, mock_instance)

        original_manager = st.session_state.cookie_manager
        notes_app.init_cookie_manager()

        self.assertEqual(st.session_state.cookie_manager, original_manager)


if __name__ == "__main__":
    unittest.main()
