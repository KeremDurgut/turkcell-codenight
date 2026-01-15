"""
Turkcell Decision Engine - Rule Engine
Dynamic rule evaluation and decision making
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal

from .database import (
    db, RuleRepository, UserStateRepository, 
    DecisionRepository, ActionRepository
)

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal and datetime types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class RuleEngine:
    """
    Dynamic rule evaluation engine.
    Rules are stored in database as data, not hardcoded.
    """
    
    # Action messages for BiP notifications
    ACTION_MESSAGES = {
        'DATA_USAGE_WARNING': 'Günlük internet kullanımınız 15GB\'ı aştı. Kalan kotanızı kontrol etmenizi öneririz.',
        'SPEND_ALERT': 'Bugün yüksek harcama yaptınız. Harcama limitinizi gözden geçirin.',
        'CONTENT_COOLDOWN_SUGGESTION': '4 saatten fazla içerik tükettiniz. Biraz ara vermeye ne dersiniz?',
        'CRITICAL_ALERT': 'Bugün internet ve harcama kullanımınız yüksek seviyededir. Limitlerinizi kontrol etmenizi öneririz.',
        'DATA_USAGE_NUDGE': 'İnternet kullanımınız orta seviyeye ulaştı. Dikkatli olmanızı öneririz.',
        'SPEND_NUDGE': 'Harcamalarınız orta seviyeye ulaştı. Bütçenizi kontrol edin.'
    }
    
    def __init__(self):
        self.rule_repo = RuleRepository(db)
        self.user_state_repo = UserStateRepository(db)
        self.decision_repo = DecisionRepository(db)
        self.action_repo = ActionRepository(db)
        
        # Initialize counters from database to avoid duplicates
        self._decision_counter = self._get_max_decision_id()
        self._action_counter = self._get_max_action_id()
    
    def _get_max_decision_id(self) -> int:
        """Get the maximum decision ID number from database"""
        try:
            result = db.execute_one("SELECT MAX(CAST(SUBSTRING(decision_id FROM 3) AS INTEGER)) as max_id FROM decisions WHERE decision_id LIKE 'D-%'")
            if result and result.get('max_id'):
                return result['max_id']
        except:
            pass
        return 900
    
    def _get_max_action_id(self) -> int:
        """Get the maximum action ID number from database"""
        try:
            result = db.execute_one("SELECT MAX(CAST(SUBSTRING(action_id FROM 3) AS INTEGER)) as max_id FROM actions WHERE action_id LIKE 'A-%'")
            if result and result.get('max_id'):
                return result['max_id']
        except:
            pass
        return 1000
    
    def evaluate_condition(self, condition: str, user_state: Dict) -> bool:
        """
        Evaluate a rule condition against user state.
        Supports: >, <, >=, <=, ==, AND, OR, BETWEEN
        """
        try:
            # Replace field names with actual values
            expr = condition
            
            # Handle BETWEEN operator (e.g., "field BETWEEN 10 AND 15")
            between_pattern = r'(\w+)\s+BETWEEN\s+([\d.]+)\s+AND\s+([\d.]+)'
            matches = re.findall(between_pattern, expr, re.IGNORECASE)
            for field, low, high in matches:
                value = float(user_state.get(field, 0) or 0)
                result = float(low) <= value <= float(high)
                expr = re.sub(
                    rf'{field}\s+BETWEEN\s+{low}\s+AND\s+{high}',
                    str(result),
                    expr,
                    flags=re.IGNORECASE
                )
            
            # Replace field names with values
            for field, value in user_state.items():
                if field in expr:
                    # Handle None values
                    if value is None:
                        value = 0
                    expr = expr.replace(field, str(float(value)))
            
            # Replace AND/OR with Python operators
            expr = re.sub(r'\bAND\b', 'and', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bOR\b', 'or', expr, flags=re.IGNORECASE)
            expr = expr.replace('&&', 'and')
            expr = expr.replace('||', 'or')
            
            # Evaluate the expression safely
            # Only allow specific operations
            allowed_chars = set('0123456789.+-*/<>= ()andorTrueFalse')
            clean_expr = expr.replace(' ', '')
            if not all(c in allowed_chars for c in clean_expr.replace('and', '').replace('or', '').replace('True', '').replace('False', '')):
                logger.warning(f"Unsafe expression detected: {condition}")
                return False
            
            result = eval(expr)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def is_rule_relevant_to_event(self, condition: str, event_type: str) -> bool:
        """
        Check if a rule is relevant to the given event type.
        USAGE events -> only internet_today_gb rules
        PAYMENT events -> only spend_today_try rules
        CONTENT_CONSUMPTION events -> only content_minutes_today rules
        """
        condition_lower = condition.lower()
        
        # Define which fields each event type affects
        event_field_map = {
            'USAGE': 'internet_today_gb',
            'PAYMENT': 'spend_today_try',
            'CONTENT_CONSUMPTION': 'content_minutes_today'
        }
        
        relevant_field = event_field_map.get(event_type, '')
        
        if not relevant_field:
            # Unknown event type, evaluate all rules
            return True
        
        # Check if the condition contains the relevant field
        # Also allow CRITICAL_ALERT which may check multiple fields
        if relevant_field in condition_lower:
            return True
        
        # For combined rules (like internet AND spend), check if our field is part of it
        return relevant_field in condition_lower
    
    def get_triggered_rules(self, user_state: Dict, event_type: str = None) -> List[Dict]:
        """
        Get all rules that are triggered by the current user state.
        If event_type is provided, only evaluate rules relevant to that event type.
        Returns rules sorted by priority (1 = highest priority).
        """
        active_rules = self.rule_repo.get_active()
        triggered = []
        
        for rule in active_rules:
            # Filter by event type if specified
            if event_type and not self.is_rule_relevant_to_event(rule['condition'], event_type):
                continue
            
            if self.evaluate_condition(rule['condition'], user_state):
                triggered.append(rule)
                logger.debug(f"Rule {rule['rule_id']} triggered for condition: {rule['condition']}")
        
        # Sort by priority (lower number = higher priority)
        triggered.sort(key=lambda r: r['priority'])
        return triggered

    
    def select_action(self, triggered_rules: List[Dict]) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Select the highest priority action and return suppressed actions.
        Returns: (selected_rule, suppressed_rules)
        """
        if not triggered_rules:
            return None, []
        
        # First rule has highest priority (already sorted)
        selected = triggered_rules[0]
        suppressed = triggered_rules[1:]
        
        return selected, suppressed
    
    def process_user(self, user_id: str, event_type: str = None) -> Optional[Dict]:
        """
        Process a single user: evaluate rules and create decision/action.
        If event_type is provided, only evaluate rules relevant to that event type.
        Returns the decision record if any action was taken.
        """
        # Get current user state
        user_state = self.user_state_repo.get_by_user(user_id)
        if not user_state:
            logger.warning(f"No state found for user {user_id}")
            return None
        
        # Get triggered rules (filtered by event_type if provided)
        triggered_rules = self.get_triggered_rules(dict(user_state), event_type)
        
        if not triggered_rules:
            logger.debug(f"No rules triggered for user {user_id}")
            return None
        
        # Select action
        selected_rule, suppressed_rules = self.select_action(triggered_rules)
        
        if not selected_rule:
            return None
        
        # Generate IDs
        self._decision_counter += 1
        self._action_counter += 1
        decision_id = f"D-{self._decision_counter}"
        action_id = f"A-{self._action_counter}"
        
        # Create decision record
        decision = {
            'decision_id': decision_id,
            'user_id': user_id,
            'triggered_rules': [r['rule_id'] for r in triggered_rules],
            'selected_action': selected_rule['action'],
            'suppressed_actions': [r['action'] for r in suppressed_rules] if suppressed_rules else None,
            'user_state_snapshot': json.dumps(dict(user_state), cls=DecimalEncoder)
        }
        
        # Create action (BiP notification)
        action = {
            'action_id': action_id,
            'user_id': user_id,
            'action_type': selected_rule['action'],
            'message': self.ACTION_MESSAGES.get(
                selected_rule['action'], 
                f"Bildirim: {selected_rule['action']}"
            )
        }
        
        # Save to database
        self.decision_repo.create(decision)
        self.action_repo.create(action)
        
        logger.info(f"Decision {decision_id} created for user {user_id}: {selected_rule['action']}")
        
        return {
            'decision': decision,
            'action': action,
            'triggered_rules': triggered_rules,
            'suppressed_rules': suppressed_rules
        }
    
    def process_all_users(self) -> List[Dict]:
        """
        Process all users and return list of decisions made.
        """
        results = []
        user_states = self.user_state_repo.get_all()
        
        for state in user_states:
            result = self.process_user(state['user_id'])
            if result:
                results.append(result)
        
        return results
    
    def simulate_evaluation(self, user_state: Dict) -> List[Dict]:
        """
        Simulate rule evaluation without saving to database.
        Useful for testing and preview.
        """
        triggered_rules = self.get_triggered_rules(user_state)
        selected_rule, suppressed_rules = self.select_action(triggered_rules)
        
        return {
            'triggered_rules': triggered_rules,
            'selected_rule': selected_rule,
            'suppressed_rules': suppressed_rules,
            'would_send_action': selected_rule['action'] if selected_rule else None
        }


# Global rule engine instance
rule_engine = RuleEngine()
