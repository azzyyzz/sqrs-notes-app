import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# Now import from app
from ..app import models, schemas
from ..app.crud import (
    get_note,
    get_notes,
    create_note,
    update_note,
    delete_note,
)

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixtures
@pytest.fixture(scope="function")
def db():
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        models.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    # Use a unique username for each test
    user = models.User(username=f"testuser_{os.urandom(4).hex()}", hashed_password="fakehashedpass")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_note(db, test_user):
    note_data = schemas.NoteCreate(title="Test Note", content="Test Content")
    note = create_note(db, note_data, test_user.id)
    return note

def test_get_note(db, test_user, test_note):
    # Test getting an existing note
    retrieved_note = get_note(db, test_note.id, test_user.id)
    assert retrieved_note is not None
    assert retrieved_note.id == test_note.id
    assert retrieved_note.title == "Test Note"
    assert retrieved_note.content == "Test Content"
    assert retrieved_note.owner_id == test_user.id
    
    # Test getting a non-existent note
    non_existent_note = get_note(db, 999, test_user.id)
    assert non_existent_note is None
    
    # Test getting a note with wrong user
    another_user = models.User(username=f"anotheruser_{os.urandom(4).hex()}", hashed_password="fakehashedpass")
    db.add(another_user)
    db.commit()
    wrong_user_note = get_note(db, test_note.id, another_user.id)
    assert wrong_user_note is None

def test_get_notes(db, test_user, test_note):
    # Test getting all notes for a user
    notes = get_notes(db, test_user.id)
    assert len(notes) == 1
    assert notes[0].id == test_note.id
    
    # Test skip and limit parameters
    for i in range(1, 11):
        note_data = schemas.NoteCreate(title=f"Note {i}", content=f"Content {i}")
        create_note(db, note_data, test_user.id)
    
    notes = get_notes(db, test_user.id, skip=5, limit=3)
    assert len(notes) == 3
    assert notes[0].title.startswith("Note 5")
    assert notes[2].title.startswith("Note 7")
    
    # Test getting notes for user with no notes
    another_user = models.User(username=f"nouser_{os.urandom(4).hex()}", hashed_password="fakehashedpass")
    db.add(another_user)
    db.commit()
    empty_notes = get_notes(db, another_user.id)
    assert len(empty_notes) == 0

def test_create_note(db, test_user):
    # Test creating a new note
    note_data = schemas.NoteCreate(title="New Note", content="New Content")
    new_note = create_note(db, note_data, test_user.id)
    
    assert new_note.id is not None
    assert new_note.title == "New Note"
    assert new_note.content == "New Content"
    assert new_note.owner_id == test_user.id
    
    # Verify the note exists in the database
    db_note = db.query(models.Note).filter(models.Note.id == new_note.id).first()
    assert db_note is not None
    assert db_note.title == "New Note"

def test_update_note(db, test_user, test_note):
    # Test updating an existing note
    update_data = schemas.NoteCreate(title="Updated Title", content="Updated Content")
    updated_note = update_note(db, test_note.id, update_data, test_user.id)
    
    assert updated_note is not None
    assert updated_note.id == test_note.id
    assert updated_note.title == "Updated Title"
    assert updated_note.content == "Updated Content"
    assert updated_note.owner_id == test_user.id
    
    # Verify the update in the database
    db_note = db.query(models.Note).filter(models.Note.id == test_note.id).first()
    assert db_note.title == "Updated Title"
    
    # Test updating a non-existent note
    non_existent_update = update_note(db, 999, update_data, test_user.id)
    assert non_existent_update is None
    
    # Test updating with wrong user
    another_user = models.User(username=f"updateuser_{os.urandom(4).hex()}", hashed_password="fakehashedpass")
    db.add(another_user)
    db.commit()
    wrong_user_update = update_note(db, test_note.id, update_data, another_user.id)
    assert wrong_user_update is None

def test_delete_note(db, test_user, test_note):
    # Test deleting an existing note
    deleted_note = delete_note(db, test_note.id, test_user.id)
    
    assert deleted_note is not None
    assert deleted_note.id == test_note.id
    
    # Verify the note is deleted from the database
    db_note = db.query(models.Note).filter(models.Note.id == test_note.id).first()
    assert db_note is None
    
    # Test deleting a non-existent note
    non_existent_delete = delete_note(db, 999, test_user.id)
    assert non_existent_delete is None
    
    # Test deleting with wrong user (should not delete)
    another_note_data = schemas.NoteCreate(title="Another Note", content="Another Content")
    another_note = create_note(db, another_note_data, test_user.id)
    
    another_user = models.User(username=f"deleteuser_{os.urandom(4).hex()}", hashed_password="fakehashedpass")
    db.add(another_user)
    db.commit()
    
    wrong_user_delete = delete_note(db, another_note.id, another_user.id)
    assert wrong_user_delete is None
    
    # Verify the note still exists
    db_note = db.query(models.Note).filter(models.Note.id == another_note.id).first()
    assert db_note is not None