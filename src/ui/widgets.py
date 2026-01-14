"""
Turkcell Decision Engine - Dashboard Widgets
Reusable UI components for the dashboard
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from .styles import (
    TURKCELL_YELLOW, TURKCELL_DARK, TURKCELL_DARKER,
    TURKCELL_ACCENT, TURKCELL_TEXT, TURKCELL_TEXT_DIM,
    RISK_COLORS, ACTION_COLORS, CARD_STYLE, STAT_CARD_STYLE
)


class StatCard(QFrame):
    """A card widget displaying a single statistic"""
    
    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setStyleSheet(STAT_CARD_STYLE)
        self.setMinimumSize(180, 120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Value label
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(f"color: {TURKCELL_YELLOW};")
        
        # Title label
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("statLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"color: {TURKCELL_TEXT_DIM}; font-size: 11px; letter-spacing: 1px;")
        
        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)
    
    def set_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(str(value))
    
    def set_color(self, color: str):
        """Change the value color"""
        self.value_label.setStyleSheet(f"color: {color};")


class DataTable(QTableWidget):
    """Enhanced table widget with styling and features"""
    
    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.setup_table()
    
    def setup_table(self):
        """Initialize table structure and styling"""
        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(self.columns)
        
        # Header styling
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Table settings
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(45)
    
    def populate(self, data: list, key_mapping: dict = None):
        """
        Populate table with data.
        key_mapping: dict mapping column names to data keys
        """
        self.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(self.columns):
                # Get the data key (might be different from column name)
                key = key_mapping.get(col_name, col_name.lower().replace(' ', '_')) if key_mapping else col_name.lower().replace(' ', '_')
                value = row_data.get(key, '')
                
                # Create item
                item = QTableWidgetItem(str(value) if value is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Apply color coding for specific columns
                if col_name.lower() in ['risk_level', 'risk']:
                    self._apply_risk_color(item, str(value))
                elif col_name.lower() in ['action', 'action_type', 'selected_action']:
                    self._apply_action_color(item, str(value))
                
                self.setItem(row_idx, col_idx, item)
    
    def _apply_risk_color(self, item: QTableWidgetItem, risk_level: str):
        """Apply color based on risk level"""
        color = RISK_COLORS.get(risk_level.upper(), TURKCELL_TEXT)
        item.setForeground(QColor(color))
        font = item.font()
        font.setBold(True)
        item.setFont(font)
    
    def _apply_action_color(self, item: QTableWidgetItem, action_type: str):
        """Apply color based on action type"""
        color = ACTION_COLORS.get(action_type, TURKCELL_TEXT)
        item.setForeground(QColor(color))


class SectionHeader(QWidget):
    """A styled section header with optional action button"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {TURKCELL_YELLOW};
            padding: 5px 0;
        """)
        
        layout.addWidget(self.title_label)
        layout.addStretch()


class RiskBadge(QLabel):
    """A colored badge showing risk level"""
    
    def __init__(self, risk_level: str = "LOW", parent=None):
        super().__init__(parent)
        self.set_risk(risk_level)
    
    def set_risk(self, risk_level: str):
        """Update the risk level display"""
        color = RISK_COLORS.get(risk_level.upper(), RISK_COLORS['LOW'])
        self.setText(risk_level.upper())
        self.setStyleSheet(f"""
            background-color: {color};
            color: {TURKCELL_DARK if risk_level.upper() in ['LOW', 'MEDIUM'] else 'white'};
            padding: 6px 16px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 11px;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class UserStateCard(QFrame):
    """Card displaying a user's current state"""
    
    def __init__(self, user_data: dict = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self.setup_ui()
        if user_data:
            self.update_data(user_data)
    
    def setup_ui(self):
        """Setup the card layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Header row (name + risk badge)
        header = QHBoxLayout()
        self.name_label = QLabel("User")
        self.name_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {TURKCELL_TEXT};")
        self.risk_badge = RiskBadge()
        header.addWidget(self.name_label)
        header.addStretch()
        header.addWidget(self.risk_badge)
        layout.addLayout(header)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(8)
        
        # Internet usage
        self.internet_label = QLabel("0.0 GB")
        self.internet_label.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {TURKCELL_YELLOW};")
        stats_grid.addWidget(QLabel("İnternet"), 0, 0)
        stats_grid.addWidget(self.internet_label, 1, 0)
        
        # Spending
        self.spend_label = QLabel("0.0 ₺")
        self.spend_label.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {TURKCELL_YELLOW};")
        stats_grid.addWidget(QLabel("Harcama"), 0, 1)
        stats_grid.addWidget(self.spend_label, 1, 1)
        
        # Content minutes
        self.content_label = QLabel("0 dk")
        self.content_label.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {TURKCELL_YELLOW};")
        stats_grid.addWidget(QLabel("İçerik"), 0, 2)
        stats_grid.addWidget(self.content_label, 1, 2)
        
        layout.addLayout(stats_grid)
        
        # City label
        self.city_label = QLabel("")
        self.city_label.setStyleSheet(f"color: {TURKCELL_TEXT_DIM}; font-size: 12px;")
        layout.addWidget(self.city_label)
    
    def update_data(self, data: dict):
        """Update card with new data"""
        self.name_label.setText(data.get('name', 'Unknown'))
        self.risk_badge.set_risk(data.get('risk_level', 'LOW'))
        
        internet = data.get('internet_today_gb', 0) or 0
        spend = data.get('spend_today_try', 0) or 0
        content = data.get('content_minutes_today', 0) or 0
        
        self.internet_label.setText(f"{float(internet):.1f} GB")
        self.spend_label.setText(f"{float(spend):.0f} ₺")
        self.content_label.setText(f"{int(float(content))} dk")
        
        self.city_label.setText(f"📍 {data.get('city', '')}")
