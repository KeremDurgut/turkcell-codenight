"""
Turkcell Decision Engine - Source Package
"""

from .config import db_config, app_config
from .database import Database, db
from .auth import AuthManager, auth_manager

__version__ = "2.0.0"
__all__ = ["db_config", "app_config", "Database", "db", "AuthManager", "auth_manager"]
