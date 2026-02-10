"""Authentication and user management services."""
from src.core import PasswordManager


class AuthService:
    """Handle user authentication and authorization."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with username and password."""
        password_hash = PasswordManager.hash_password(password)
        return self.db.authenticate_user(username, password_hash)
    
    def get_user_role(self, username: str) -> str:
        """Get the role of a user."""
        return self.db.get_user_role(username)
    
    def update_last_login(self, username: str):
        """Record user's login."""
        self.db.update_last_login(username)
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin."""
        return self.db.get_user_role(username) == 'admin'
