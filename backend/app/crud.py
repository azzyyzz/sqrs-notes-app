from sqlalchemy.orm import Session

from . import models, schemas

def get_note(db: Session, note_id: int, user_id: int):
    return db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.owner_id == user_id
    ).first()

def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Note).filter(
        models.Note.owner_id == user_id
    ).offset(skip).limit(limit).all()

def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    db_note = models.Note(**note.dict(), owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note: schemas.NoteCreate, user_id: int):
    db_note = get_note(db, note_id, user_id)
    if db_note:
        db_note.title = note.title
        db_note.content = note.content
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int, user_id: int):
    db_note = get_note(db, note_id, user_id)
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note