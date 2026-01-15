"""
Turkcell Decision Engine - Dashboard Panel
Kullanıcı bazlı karşılaştırmalı metrikler
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSplitter, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from .widgets import DataTable, SectionHeader
from .styles import (
    TURKCELL_YELLOW, TURKCELL_BLUE, TURKCELL_DARK,
    BG_WHITE, BG_GRAY, TEXT_PRIMARY, TEXT_SECONDARY,
    COLOR_CRITICAL, COLOR_WARNING, COLOR_SUCCESS
)
from ..database import (
    db, UserStateRepository, EventRepository, 
    ActionRepository, DashboardRepository, UserRepository
)


class DashboardPanel(QWidget):
    """Dashboard panel with user-based comparative metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_state_repo = UserStateRepository(db)
        self.event_repo = EventRepository(db)
        self.action_repo = ActionRepository(db)
        self.dashboard_repo = DashboardRepository(db)
        self.user_repo = UserRepository(db)
        
        # Configure pyqtgraph for light theme
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', TURKCELL_DARK)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 20)
        
        # User selector row
        selector_frame = QFrame()
        selector_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_GRAY};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        selector_layout = QHBoxLayout(selector_frame)
        selector_layout.setContentsMargins(15, 10, 15, 10)
        
        selector_label = QLabel("Kullanıcı Seçin:")
        selector_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK};")
        selector_layout.addWidget(selector_label)
        
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(200)
        self.user_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {TURKCELL_BLUE};
                border-radius: 6px;
                background-color: white;
            }}
        """)
        self.user_combo.currentIndexChanged.connect(self.on_user_changed)
        selector_layout.addWidget(self.user_combo)
        
        selector_layout.addStretch()
        
        # Summary stats
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        selector_layout.addWidget(self.summary_label)
        
        main_layout.addWidget(selector_frame)
        
        # Charts row - comparative metrics
        charts_frame = QFrame()
        charts_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WHITE};
                border-radius: 12px;
            }}
        """)
        charts_layout = QHBoxLayout(charts_frame)
        charts_layout.setSpacing(15)
        charts_layout.setContentsMargins(15, 15, 15, 15)
        
        # Chart 1: Internet Usage - User vs Average
        chart1_frame = self.create_chart_frame("İnternet Kullanımı")
        self.internet_chart = pg.PlotWidget()
        self.internet_chart.setBackground(BG_GRAY)
        self.internet_chart.showGrid(x=False, y=True, alpha=0.3)
        self.internet_chart.setLabel('left', 'GB')
        self.internet_chart.setMinimumHeight(140)
        self.internet_chart.setMaximumHeight(160)
        chart1_frame.layout().addWidget(self.internet_chart)
        charts_layout.addWidget(chart1_frame)
        
        # Chart 2: Spend - User vs Average
        chart2_frame = self.create_chart_frame("Harcama")
        self.spend_chart = pg.PlotWidget()
        self.spend_chart.setBackground(BG_GRAY)
        self.spend_chart.showGrid(x=False, y=True, alpha=0.3)
        self.spend_chart.setLabel('left', '₺')
        self.spend_chart.setMinimumHeight(140)
        self.spend_chart.setMaximumHeight(160)
        chart2_frame.layout().addWidget(self.spend_chart)
        charts_layout.addWidget(chart2_frame)
        
        # Chart 3: Content Time - User vs Average
        chart3_frame = self.create_chart_frame("İçerik Süresi")
        self.content_chart = pg.PlotWidget()
        self.content_chart.setBackground(BG_GRAY)
        self.content_chart.showGrid(x=False, y=True, alpha=0.3)
        self.content_chart.setLabel('left', 'dk')
        self.content_chart.setMinimumHeight(140)
        self.content_chart.setMaximumHeight(160)
        chart3_frame.layout().addWidget(self.content_chart)
        charts_layout.addWidget(chart3_frame)
        
        main_layout.addWidget(charts_frame)
        
        # Bottom section - Two tables side by side
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Left - Recent events
        events_widget = QFrame()
        events_widget.setStyleSheet(f"background-color: {BG_GRAY}; border-radius: 8px;")
        events_layout = QVBoxLayout(events_widget)
        events_layout.setContentsMargins(15, 12, 15, 12)
        
        events_title = QLabel("Son Eventler")
        events_title.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        events_layout.addWidget(events_title)
        
        self.events_table = DataTable([
            "Kullanıcı", "Servis", "Tür", "Değer", "Zaman"
        ])
        events_layout.addWidget(self.events_table)
        
        bottom_layout.addWidget(events_widget, 1)  # Stretch factor 1
        
        # Right - Recent actions
        actions_widget = QFrame()
        actions_widget.setStyleSheet(f"background-color: {BG_GRAY}; border-radius: 8px;")
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.setContentsMargins(15, 12, 15, 12)
        
        actions_title = QLabel("Son Aksiyonlar")
        actions_title.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        actions_layout.addWidget(actions_title)
        
        self.actions_table = DataTable([
            "Kullanıcı", "Aksiyon Türü", "Mesaj", "Zaman"
        ])
        actions_layout.addWidget(self.actions_table)
        
        bottom_layout.addWidget(actions_widget, 1)  # Stretch factor 1
        
        main_layout.addLayout(bottom_layout, 1)  # Give bottom section stretch to fill space
    
    def create_chart_frame(self, title: str) -> QFrame:
        """Create a styled frame for charts"""
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {BG_GRAY}; border-radius: 8px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 13px;")
        layout.addWidget(title_label)
        
        return frame
    
    def load_data(self):
        """Load all dashboard data"""
        try:
            # Load users into combo
            self.load_users()
            
            # Load charts for selected user
            self.load_user_charts()
            
            # Load tables
            self.load_recent_events()
            self.load_recent_actions()
            
            # Update summary
            self.update_summary()
            
        except Exception as e:
            import traceback
            print(f"Error loading dashboard: {e}")
            traceback.print_exc()
    
    def load_users(self):
        """Load users into combo box"""
        self.user_combo.blockSignals(True)
        self.user_combo.clear()
        
        users = self.user_repo.get_all()
        for user in users:
            self.user_combo.addItem(
                f"{user['user_id']} - {user['name']}", 
                user['user_id']
            )
        
        self.user_combo.blockSignals(False)
    
    def on_user_changed(self, index):
        """Handle user selection change"""
        self.load_user_charts()
    
    def load_user_charts(self):
        """Load comparative charts for selected user"""
        user_id = self.user_combo.currentData()
        if not user_id:
            return
        
        # Get selected user's state
        user_state = self.user_state_repo.get_by_user(user_id)
        if not user_state:
            return
        
        # Get all user states for average calculation
        all_states = self.user_state_repo.get_all()
        
        # Calculate averages
        if all_states:
            avg_internet = sum(float(s.get('internet_today_gb', 0) or 0) for s in all_states) / len(all_states)
            avg_spend = sum(float(s.get('spend_today_try', 0) or 0) for s in all_states) / len(all_states)
            avg_content = sum(float(s.get('content_minutes_today', 0) or 0) for s in all_states) / len(all_states)
        else:
            avg_internet = avg_spend = avg_content = 0
        
        user_internet = float(user_state.get('internet_today_gb', 0) or 0)
        user_spend = float(user_state.get('spend_today_try', 0) or 0)
        user_content = float(user_state.get('content_minutes_today', 0) or 0)
        
        # Update charts
        self.update_comparison_chart(
            self.internet_chart, 
            user_internet, avg_internet, 
            user_id, "Ortalama"
        )
        
        self.update_comparison_chart(
            self.spend_chart, 
            user_spend, avg_spend, 
            user_id, "Ortalama"
        )
        
        self.update_comparison_chart(
            self.content_chart, 
            user_content, avg_content, 
            user_id, "Ortalama"
        )
    
    def update_comparison_chart(self, chart, user_value, avg_value, user_label, avg_label):
        """Update a comparison bar chart"""
        chart.clear()
        
        x = [0, 1]
        heights = [user_value, avg_value]
        
        # Colors: User value in Turkcell blue, average in gray
        brushes = [
            pg.mkBrush(TURKCELL_BLUE),
            pg.mkBrush('#AAAAAA')
        ]
        
        bargraph = pg.BarGraphItem(x=x, height=heights, width=0.5, brushes=brushes)
        chart.addItem(bargraph)
        
        # Set Y axis to start from 0
        max_value = max(user_value, avg_value, 1)  # At least 1 to avoid empty chart
        chart.setYRange(0, max_value * 1.1)  # 10% padding on top
        
        # Set x-axis labels
        labels = [(0, user_label), (1, avg_label)]
        ax = chart.getAxis('bottom')
        ax.setTicks([labels])
    
    def load_risk_chart(self):
        """Load risk distribution bar chart"""
        self.risk_chart.clear()
        
        try:
            risk_data = self.dashboard_repo.get_risk_distribution()
            
            if not risk_data:
                return
            
            risk_colors = {
                'CRITICAL': COLOR_CRITICAL,
                'HIGH': '#FF6B35',
                'MEDIUM': COLOR_WARNING,
                'LOW': COLOR_SUCCESS
            }
            
            x = []
            heights = []
            colors = []
            
            for i, item in enumerate(risk_data):
                level = item['risk_level']
                count = item['count']
                x.append(i)
                heights.append(count)
                colors.append(pg.mkBrush(risk_colors.get(level, TURKCELL_BLUE)))
            
            bargraph = pg.BarGraphItem(x=x, height=heights, width=0.6, brushes=colors)
            self.risk_chart.addItem(bargraph)
            
            # Set Y axis to start from 0
            if heights:
                self.risk_chart.setYRange(0, max(heights) * 1.1)
            
            labels = [(i, item['risk_level']) for i, item in enumerate(risk_data)]
            ax = self.risk_chart.getAxis('bottom')
            ax.setTicks([labels])
            
        except Exception as e:
            print(f"Error loading risk chart: {e}")
    
    def update_summary(self):
        """Update summary statistics"""
        try:
            summary = self.dashboard_repo.get_summary()
            if summary:
                self.summary_label.setText(
                    f"Toplam: {summary.get('total_users', 0)} kullanıcı | "
                    f"{summary.get('today_events', 0)} event | "
                    f"{summary.get('today_decisions', 0)} karar | "
                    f"{summary.get('active_rules', 0)} kural"
                )
        except Exception as e:
            print(f"Error updating summary: {e}")
    
    def load_recent_events(self):
        """Load recent events table"""
        try:
            events = self.event_repo.get_recent(5)
            table_data = []
            
            for event in events:
                timestamp = event.get('timestamp', '')
                if hasattr(timestamp, 'strftime'):
                    timestamp = timestamp.strftime('%H:%M')
                
                table_data.append({
                    'Kullanıcı': event.get('user_id', ''),
                    'Servis': event.get('service', ''),
                    'Tür': event.get('event_type', ''),
                    'Değer': f"{event.get('value', 0)} {event.get('unit', '')}",
                    'Zaman': str(timestamp)[:5]
                })
            
            self.events_table.populate(table_data)
        except Exception as e:
            print(f"Error loading events: {e}")
    
    def load_recent_actions(self):
        """Load recent actions table"""
        try:
            actions = self.action_repo.get_all(5)
            table_data = []
            
            for action in actions:
                timestamp = action.get('created_at', '')
                if hasattr(timestamp, 'strftime'):
                    timestamp = timestamp.strftime('%H:%M')
                
                # Truncate message if too long
                message = action.get('message', '')
                if len(message) > 40:
                    message = message[:37] + '...'
                
                table_data.append({
                    'Kullanıcı': action.get('user_id', ''),
                    'Aksiyon Türü': action.get('action_type', ''),
                    'Mesaj': message,
                    'Zaman': str(timestamp)[:5]
                })
            
            self.actions_table.populate(table_data)
        except Exception as e:
            print(f"Error loading actions: {e}")
