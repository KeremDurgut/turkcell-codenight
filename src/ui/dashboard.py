"""
Turkcell Decision Engine - Dashboard Panel
Main dashboard view with statistics and data tables
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QFrame, QGridLayout, QPushButton, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from .widgets import StatCard, DataTable, SectionHeader, UserStateCard
from .styles import TURKCELL_YELLOW, TURKCELL_DARK, CARD_STYLE
from ..database import (
    db, DashboardRepository, UserRepository, EventRepository,
    UserStateRepository, DecisionRepository, ActionRepository
)


class DashboardPanel(QWidget):
    """Main dashboard panel showing overview statistics and data"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_repositories()
        self.setup_ui()
        self.load_data()
        
        # Auto-refresh timer (every 30 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)
    
    def setup_repositories(self):
        """Initialize data repositories"""
        self.dashboard_repo = DashboardRepository(db)
        self.user_repo = UserRepository(db)
        self.event_repo = EventRepository(db)
        self.user_state_repo = UserStateRepository(db)
        self.decision_repo = DecisionRepository(db)
        self.action_repo = ActionRepository(db)
    
    def setup_ui(self):
        """Setup the dashboard layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        title = QLabel("📊 Dashboard")
        title.setObjectName("headerLabel")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_YELLOW};")
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        main_layout.addLayout(header_layout)
        
        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.stat_users = StatCard("Toplam Kullanıcı")
        self.stat_events = StatCard("Bugünkü Event")
        self.stat_decisions = StatCard("Bugünkü Karar")
        self.stat_actions = StatCard("Bugünkü Aksiyon")
        self.stat_active_rules = StatCard("Aktif Kural")
        
        stats_layout.addWidget(self.stat_users)
        stats_layout.addWidget(self.stat_events)
        stats_layout.addWidget(self.stat_decisions)
        stats_layout.addWidget(self.stat_actions)
        stats_layout.addWidget(self.stat_active_rules)
        
        main_layout.addLayout(stats_layout)
        
        # Splitter for tables
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - User states
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        left_layout.addWidget(SectionHeader("👥 Kullanıcı Durumları"))
        
        # User state cards in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.users_container = QWidget()
        self.users_layout = QVBoxLayout(self.users_container)
        self.users_layout.setSpacing(12)
        self.users_layout.addStretch()
        
        scroll.setWidget(self.users_container)
        left_layout.addWidget(scroll)
        
        splitter.addWidget(left_panel)
        
        # Right side - Recent events and actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Recent events
        right_layout.addWidget(SectionHeader("📨 Son Eventler"))
        self.events_table = DataTable([
            "Event ID", "Kullanıcı", "Servis", "Tür", "Değer", "Zaman"
        ])
        self.events_table.setMaximumHeight(250)
        right_layout.addWidget(self.events_table)
        
        # Recent actions
        right_layout.addWidget(SectionHeader("🔔 Son Aksiyonlar"))
        self.actions_table = DataTable([
            "Action ID", "Kullanıcı", "Aksiyon Türü", "Zaman"
        ])
        right_layout.addWidget(self.actions_table)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def load_data(self):
        """Load all dashboard data from database"""
        try:
            # Load summary stats
            summary = self.dashboard_repo.get_summary()
            if summary:
                self.stat_users.set_value(str(summary.get('total_users', 0)))
                self.stat_events.set_value(str(summary.get('today_events', 0)))
                self.stat_decisions.set_value(str(summary.get('today_decisions', 0)))
                self.stat_actions.set_value(str(summary.get('today_actions', 0)))
                self.stat_active_rules.set_value(str(summary.get('active_rules', 0)))
            
            # Load user states
            self.load_user_states()
            
            # Load recent events
            self.load_recent_events()
            
            # Load recent actions
            self.load_recent_actions()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def load_user_states(self):
        """Load and display user state cards"""
        # Clear existing cards
        while self.users_layout.count() > 1:
            item = self.users_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load user states
        states = self.user_state_repo.get_all()
        for state in states:
            card = UserStateCard(dict(state))
            self.users_layout.insertWidget(self.users_layout.count() - 1, card)
    
    def load_recent_events(self):
        """Load recent events into table"""
        events = self.event_repo.get_recent(10)
        
        table_data = []
        for event in events:
            table_data.append({
                'event id': event.get('event_id', ''),
                'kullanıcı': event.get('user_name', event.get('user_id', '')),
                'servis': event.get('service', ''),
                'tür': event.get('event_type', ''),
                'değer': f"{event.get('value', 0)} {event.get('unit', '')}",
                'zaman': str(event.get('timestamp', ''))[:19]
            })
        
        self.events_table.populate(table_data)
    
    def load_recent_actions(self):
        """Load recent actions into table"""
        actions = self.action_repo.get_all(10)
        
        table_data = []
        for action in actions:
            table_data.append({
                'action id': action.get('action_id', ''),
                'kullanıcı': action.get('user_name', action.get('user_id', '')),
                'aksiyon türü': action.get('action_type', ''),
                'zaman': str(action.get('created_at', ''))[:19]
            })
        
        self.actions_table.populate(table_data)
