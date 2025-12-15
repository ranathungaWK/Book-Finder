from werkzeug.security import generate_password_hash
from database.models import User
from database.db_setup import db 



def create_user(username: str, email: str, raw_password: str) -> 'User' :
    """Create a new user and add to the database."""
    user = User(username=username,
                email=email,
                password_hash= generate_password_hash(raw_password))
    
    db.session.add(user)
    db.session.commit()
    return user 
    