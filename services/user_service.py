from werkzeug.security import generate_password_hash , check_password_hash
from database.models import User
from database.db_setup import db 



def create_user(username: str, email: str, raw_password: str) -> 'User' :
    """Create a new user and add to the database."""
    user = User(username=username,
                email=email,
                password_hash= generate_password_hash(raw_password))
    
    db.session.add(user)
    try:
        db.session.commit()
        return user 
    except Exception as e:
        db.session.rollback()
        return None
    

def authenticate_user(email: str, raw_password: str) -> 'User' :
    """Authenticate a user by email and password."""
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, raw_password):
        return user
    return None
    


    