from datetime import datetime , timezone
from database.db_setup import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    read_books = db.relationship("UserReadBook", back_populates="user")

class UserReadBook(db.Model):
    __tablename__ = "user_read_books" 

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(300),nullable=False)
    authors = db.Column(db.String(200))
    isbn = db.Column(db.String(100))
    description = db.Column(db.Text)

    read_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="read_books")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'isbn', name='unique_user_book'),
    )



