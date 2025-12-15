from database.models import UserReadBook 
from database.db_setup import db
from sqlalchemy.exc import IntegrityError

def add_read_book(user_id , title, authors=None , isbn=None, description=None) -> UserReadBook:
    """ create a new read book entry for a user and add to the database."""
    
    read_book = UserReadBook(
        user_id=user_id,
        title=title,
        authors=authors,
        isbn=isbn,
        description=description
    )

    db.session.add(read_book)

    try:
        db.session.commit()
        return read_book
    except IntegrityError:
        db.session.rollback()
        raise ValueError("This book has already been added to the user's read list.")