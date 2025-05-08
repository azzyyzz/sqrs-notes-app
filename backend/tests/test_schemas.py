from app.schemas import (
    Token,
    TokenData,
    UserCreate,
    User,
    NoteCreate,
    Note,
    TranslationRequest,
)


def test_token_schema():
    token = Token(access_token="abc123", token_type="bearer")
    assert token.access_token == "abc123"
    assert token.token_type == "bearer"


def test_token_data_schema():
    data = TokenData(username="testuser")
    assert data.username == "testuser"


def test_user_create_schema():
    user = UserCreate(username="testuser", password="123")
    assert user.username == "testuser"
    assert user.password == "123"


def test_user_schema_with_config():
    user = User(username="user1", id=1)
    assert user.id == 1
    assert user.username == "user1"


def test_note_create_schema():
    note = NoteCreate(title="My Note", content="Some text")
    assert note.title == "My Note"
    assert note.content == "Some text"


def test_note_schema_with_config():
    note = Note(id=1, title="Title", content="Content", owner_id=42)
    assert note.id == 1
    assert note.owner_id == 42


def test_translation_request_schema():
    req = TranslationRequest(text="Translate me")
    assert req.text == "Translate me"
