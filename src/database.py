"""
Turkcell Decision Engine - Database Module
PostgreSQL connection and query management
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging

from .config import db_config

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection manager"""
    
    _instance: Optional['Database'] = None
    _connection = None
    
    def __new__(cls):
        """Singleton pattern for database connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self._connection = psycopg2.connect(**db_config.connection_dict)
            self._connection.autocommit = False
            logger.info(f"Connected to database: {db_config.name}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connection is not None and not self._connection.closed
    
    @contextmanager
    def cursor(self, dict_cursor: bool = True):
        """Context manager for database cursor"""
        if not self.is_connected:
            self.connect()
        
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = self._connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute a query and return results"""
        with self.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # SELECT query
                return cur.fetchall()
            return None
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute a query and return single result"""
        with self.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchone()
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries with different parameters"""
        with self.cursor() as cur:
            cur.executemany(query, params_list)
            return cur.rowcount


# ============================================================
# Repository Classes
# ============================================================

class UserRepository:
    """User data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        """Get all users"""
        return self.db.execute("SELECT * FROM users ORDER BY user_id")
    
    def get_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.db.execute_one(
            "SELECT * FROM users WHERE user_id = %s", 
            (user_id,)
        )
    
    def get_with_state(self) -> List[Dict]:
        """Get all users with their current state"""
        return self.db.execute("""
            SELECT u.*, us.internet_today_gb, us.spend_today_try, 
                   us.content_minutes_today, us.risk_level
            FROM users u
            LEFT JOIN user_state us ON u.user_id = us.user_id
            ORDER BY u.user_id
        """)


class EventRepository:
    """Event data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self, limit: int = 100) -> List[Dict]:
        """Get all events"""
        return self.db.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT %s",
            (limit,)
        )
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get events for a specific user"""
        return self.db.execute(
            "SELECT * FROM events WHERE user_id = %s ORDER BY timestamp DESC",
            (user_id,)
        )
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get most recent events"""
        return self.db.execute("""
            SELECT e.*, u.name as user_name 
            FROM events e
            JOIN users u ON e.user_id = u.user_id
            ORDER BY e.timestamp DESC 
            LIMIT %s
        """, (limit,))
    
    def create(self, event: Dict) -> bool:
        """Create a new event"""
        query = """
            INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.execute(query, (
                event['event_id'], event['user_id'], event['service'],
                event['event_type'], event['value'], event['unit'], event['timestamp']
            ))
            return True
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return False


class UserStateRepository:
    """User state data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        """Get all user states"""
        return self.db.execute("""
            SELECT us.*, u.name, u.city
            FROM user_state us
            JOIN users u ON us.user_id = u.user_id
            ORDER BY 
                CASE us.risk_level 
                    WHEN 'CRITICAL' THEN 1 
                    WHEN 'HIGH' THEN 2 
                    WHEN 'MEDIUM' THEN 3 
                    WHEN 'LOW' THEN 4 
                END
        """)
    
    def get_by_user(self, user_id: str) -> Optional[Dict]:
        """Get state for a specific user"""
        return self.db.execute_one(
            "SELECT * FROM user_state WHERE user_id = %s",
            (user_id,)
        )
    
    def get_by_risk_level(self, risk_level: str) -> List[Dict]:
        """Get users with specific risk level"""
        return self.db.execute(
            "SELECT * FROM user_state WHERE risk_level = %s",
            (risk_level,)
        )


class RuleRepository:
    """Rule data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self) -> List[Dict]:
        """Get all rules"""
        return self.db.execute("SELECT * FROM rules ORDER BY priority")
    
    def get_active(self) -> List[Dict]:
        """Get only active rules ordered by priority"""
        return self.db.execute(
            "SELECT * FROM rules WHERE is_active = TRUE ORDER BY priority"
        )
    
    def get_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get rule by ID"""
        return self.db.execute_one(
            "SELECT * FROM rules WHERE rule_id = %s",
            (rule_id,)
        )
    
    def create(self, rule: Dict) -> bool:
        """Create a new rule"""
        query = """
            INSERT INTO rules (rule_id, condition, action, priority, is_active, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.execute(query, (
                rule['rule_id'], rule['condition'], rule['action'],
                rule['priority'], rule.get('is_active', True), rule.get('description', '')
            ))
            return True
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            return False
    
    def update(self, rule_id: str, updates: Dict) -> bool:
        """Update an existing rule"""
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key != 'rule_id':
                set_clauses.append(f"{key} = %s")
                values.append(value)
        
        if not set_clauses:
            return False
        
        values.append(rule_id)
        query = f"UPDATE rules SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE rule_id = %s"
        
        try:
            self.db.execute(query, tuple(values))
            return True
        except Exception as e:
            logger.error(f"Failed to update rule: {e}")
            return False
    
    def toggle_active(self, rule_id: str) -> bool:
        """Toggle rule active status"""
        try:
            self.db.execute(
                "UPDATE rules SET is_active = NOT is_active, updated_at = CURRENT_TIMESTAMP WHERE rule_id = %s",
                (rule_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to toggle rule: {e}")
            return False


class DecisionRepository:
    """Decision data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self, limit: int = 100) -> List[Dict]:
        """Get all decisions"""
        return self.db.execute("""
            SELECT d.*, u.name as user_name
            FROM decisions d
            JOIN users u ON d.user_id = u.user_id
            ORDER BY d.timestamp DESC
            LIMIT %s
        """, (limit,))
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get decisions for a specific user"""
        return self.db.execute(
            "SELECT * FROM decisions WHERE user_id = %s ORDER BY timestamp DESC",
            (user_id,)
        )
    
    def create(self, decision: Dict) -> bool:
        """Create a new decision record"""
        query = """
            INSERT INTO decisions (decision_id, user_id, triggered_rules, selected_action, suppressed_actions, user_state_snapshot)
            VALUES (%s, %s, %s, %s, %s::action_type_enum[], %s)
        """
        try:
            # Convert Python lists to PostgreSQL array format
            triggered_rules = decision['triggered_rules']
            
            suppressed_actions = decision.get('suppressed_actions')
            if isinstance(suppressed_actions, list) and suppressed_actions:
                suppressed_actions = suppressed_actions
            else:
                suppressed_actions = None
            
            self.db.execute(query, (
                decision['decision_id'], decision['user_id'], 
                triggered_rules, decision['selected_action'],
                suppressed_actions, decision.get('user_state_snapshot')
            ))
            logger.info(f"Decision {decision['decision_id']} saved to database")
            return True
        except Exception as e:
            logger.error(f"Failed to create decision: {e}")
            return False


class ActionRepository:
    """Action data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all(self, limit: int = 100) -> List[Dict]:
        """Get all actions"""
        return self.db.execute("""
            SELECT a.*, u.name as user_name
            FROM actions a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
            LIMIT %s
        """, (limit,))
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get actions for a specific user"""
        return self.db.execute(
            "SELECT * FROM actions WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
    
    def create(self, action: Dict) -> bool:
        """Create a new action"""
        query = """
            INSERT INTO actions (action_id, user_id, action_type, message)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.execute(query, (
                action['action_id'], action['user_id'],
                action['action_type'], action.get('message', '')
            ))
            return True
        except Exception as e:
            logger.error(f"Failed to create action: {e}")
            return False
    
    def get_daily_counts(self) -> List[Dict]:
        """Get action counts grouped by type for today"""
        return self.db.execute("""
            SELECT action_type, COUNT(*) as count
            FROM actions
            WHERE DATE(created_at) = CURRENT_DATE
            GROUP BY action_type
            ORDER BY count DESC
        """)


class DashboardRepository:
    """Dashboard summary data access layer"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_summary(self) -> Dict:
        """Get dashboard summary statistics"""
        result = self.db.execute_one("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM events) as total_events,
                (SELECT COUNT(*) FROM events WHERE DATE(timestamp) = CURRENT_DATE) as today_events,
                (SELECT COUNT(*) FROM decisions) as total_decisions,
                (SELECT COUNT(*) FROM decisions WHERE DATE(timestamp) = CURRENT_DATE) as today_decisions,
                (SELECT COUNT(*) FROM actions) as total_actions,
                (SELECT COUNT(*) FROM actions WHERE DATE(created_at) = CURRENT_DATE) as today_actions,
                (SELECT COUNT(*) FROM rules WHERE is_active = TRUE) as active_rules
        """)
        return dict(result) if result else {}
    
    def get_risk_distribution(self) -> List[Dict]:
        """Get user distribution by risk level"""
        return self.db.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM user_state
            GROUP BY risk_level
            ORDER BY 
                CASE risk_level 
                    WHEN 'CRITICAL' THEN 1 
                    WHEN 'HIGH' THEN 2 
                    WHEN 'MEDIUM' THEN 3 
                    WHEN 'LOW' THEN 4 
                END
        """)


# Global database instance
db = Database()
