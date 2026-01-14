"""
Turkcell Decision Engine - Configuration Module
Database and application settings management
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "turkcell_decision_engine")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")

    @property
    def connection_string(self) -> str:
        """Returns psycopg2 connection string"""
        return f"host={self.host} port={self.port} dbname={self.name} user={self.user} password={self.password}"

    @property
    def connection_dict(self) -> dict:
        """Returns connection parameters as dictionary"""
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.name,
            "user": self.user,
            "password": self.password
        }


@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("APP_LOG_LEVEL", "INFO")
    
    # UI Settings
    window_title: str = "Turkcell Decision Engine"
    window_width: int = 1400
    window_height: int = 900
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    database_dir: Path = base_dir / "database"


# Global config instances
db_config = DatabaseConfig()
app_config = AppConfig()
