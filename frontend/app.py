import streamlit as st
import requests
from requests.exceptions import RequestException
import extra_streamlit_components as stx
import time

# Backend API URL
API_URL = "http://localhost:8000"


def init_cookie_manager():
    if 'cookie_manager' not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager()


def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            response = requests.post(
                f"{API_URL}/token",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token
                st.session_state.username = username
                st.session_state.cookie_manager.set("auth_token", token)
                time.sleep(5)
                st.session_state.cookie_manager.get_all(key="login")
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        except RequestException:
            st.error("Could not connect to the server")


def check_login():
    cookies = st.session_state.cookie_manager.get_all("check_login")
    if 'auth_token' in cookies:
        token = cookies['auth_token']
        try:
            # Verify token with backend
            response = requests.get(
                f"{API_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if response.status_code == 200:
                st.session_state.token = token
                st.session_state.username = response.json().get("username")
                return True
        except RequestException:
            pass
    return False


def logout():
    st.session_state.cookie_manager.delete("auth_token")
    st.session_state.clear()
    time.sleep(5)
    st.rerun()


def signup():
    st.subheader("Sign Up")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    if st.button("Create Account"):
        try:
            response = requests.post(
                f"{API_URL}/users/",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                st.success("Account created successfully! Please login.")
            else:
                st.error(response.json().get("detail", "Registration failed"))
        except RequestException:
            st.error("Could not connect to the server")


def notes_app():
    st.title("Notes App")
    st.subheader(f"Welcome, {st.session_state.username}!")

    # Create note
    with st.form("new_note"):
        st.write("Add a new note")
        title = st.text_input("Title")
        content = st.text_area("Content")
        submitted = st.form_submit_button("Save")
        if submitted:
            try:
                response = requests.post(
                    f"{API_URL}/notes/",
                    json={"title": title, "content": content},
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}"
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    st.success("Note added!")
                else:
                    st.error("Failed to add note")
            except RequestException:
                st.error("Could not connect to the server")

    # List notes
    try:
        notes = requests.get(
            f"{API_URL}/notes/",
            headers={
                "Authorization": f"Bearer {st.session_state.token}"
            },
            timeout=10
        ).json()

        for note in notes:
            with st.expander(f"{note['title']}"):
                st.write(note['content'])

                # Translation
                if st.button("Translate to Russian",
                             key=f"translate_{note['id']}"):
                    try:
                        translated = requests.post(
                            f"{API_URL}/translate/",
                            json={"text": note['content']},
                            headers={
                                "Authorization":
                                    f"Bearer {st.session_state.token}"
                            },
                            timeout=10
                        ).json()
                        st.write("Translation:", translated['translated_text'])
                    except Exception:
                        st.error("Translation failed")

                # Edit and Delete
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_{note['id']}"):
                        st.session_state.edit_note_id = note['id']
                        st.session_state.edit_title = note['title']
                        st.session_state.edit_content = note['content']

                with col2:
                    if st.button("Delete", key=f"delete_{note['id']}"):
                        try:
                            response = requests.delete(
                                f"{API_URL}/notes/{note['id']}",
                                headers={
                                    "Authorization":
                                        f"Bearer {st.session_state.token}"
                                },
                                timeout=10
                            )
                            if response.status_code == 200:
                                st.success("Note deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete note")
                        except RequestException:
                            st.error("Could not connect to the server")

    except RequestException:
        st.error("Could not load notes")

    # Edit form (shown only when editing)
    if 'edit_note_id' in st.session_state:
        with st.form("edit_note"):
            st.write("Edit Note")
            edit_title = st.text_input(
                "Title",
                value=st.session_state.edit_title
            )
            edit_content = st.text_area(
                "Content",
                value=st.session_state.edit_content
            )
            submitted = st.form_submit_button("Update")
            if submitted:
                try:
                    response = requests.put(
                        f"{API_URL}/notes/{st.session_state.edit_note_id}",
                        json={"title": edit_title, "content": edit_content},
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}"
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        st.success("Note updated!")
                        del st.session_state.edit_note_id
                        del st.session_state.edit_title
                        del st.session_state.edit_content
                        st.rerun()
                    else:
                        st.error("Failed to update note")
                except RequestException:
                    st.error("Could not connect to the server")

    # Logout
    if st.button("Logout"):
        logout()


def main():
    st.title("Welcome to Notes App")

    init_cookie_manager()

    if 'token' not in st.session_state:
        if not check_login():
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            with tab1:
                login()
            with tab2:
                signup()
            return
    notes_app()


if __name__ == "__main__":
    main()
