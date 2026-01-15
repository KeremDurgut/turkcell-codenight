"""
Turkcell Decision Engine - Authentication Manager
Rol tabanlı erişim kontrolü (RBAC) yönetimi
"""

import hashlib
import logging
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime

from .database import db

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Logged in user data"""
    admin_id: int
    username: str
    role: str
    full_name: str
    
    def is_admin(self) -> bool:
        return self.role == 'ADMIN'
    
    def is_analyst(self) -> bool:
        return self.role == 'ANALYST'
    
    def can_modify_rules(self) -> bool:
        return self.role == 'ADMIN'
    
    def can_add_events(self) -> bool:
        return self.role == 'ADMIN'


class AuthManager:
    """
    Authentication and authorization manager.
    Handles login, logout, and role-based access control.
    """
    
    _instance: Optional['AuthManager'] = None
    _current_user: Optional[User] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @property
    def current_user(self) -> Optional[User]:
        """Get current logged in user"""
        return self._current_user
    
    @property
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self._current_user is not None
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate user with username and password.
        Returns: (success, message)
        """
        try:
            # Hash the password
            password_hash = self.hash_password(password)
            
            # Query database
            result = db.execute_one("""
                SELECT admin_id, username, role, full_name, is_active
                FROM system_admins
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            
            if not result:
                logger.warning(f"Failed login attempt for username: {username}")
                return False, "Kullanıcı adı veya şifre hatalı"
            
            if not result['is_active']:
                logger.warning(f"Inactive user login attempt: {username}")
                return False, "Bu hesap devre dışı bırakılmış"
            
            # Create user object
            self._current_user = User(
                admin_id=result['admin_id'],
                username=result['username'],
                role=result['role'],
                full_name=result['full_name'] or result['username']
            )
            
            # Update last login
            db.execute("""
                UPDATE system_admins 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE admin_id = %s
            """, (result['admin_id'],))
            
            logger.info(f"User logged in: {username} (role: {result['role']})")
            return True, f"Hoş geldiniz, {self._current_user.full_name}!"
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "Giriş sırasında bir hata oluştu"
    
    def logout(self):
        """Log out current user"""
        if self._current_user:
            logger.info(f"User logged out: {self._current_user.username}")
            self._current_user = None
    
    def has_permission(self, required_role: str) -> bool:
        """
        Check if current user has required role.
        ADMIN has all permissions.
        """
        if not self._current_user:
            return False
        
        if self._current_user.role == 'ADMIN':
            return True
        
        return self._current_user.role == required_role
    
    def require_login(self) -> bool:
        """Check if login is required (user not logged in)"""
        return not self.is_logged_in


# Global auth manager instance
auth_manager = AuthManager()
