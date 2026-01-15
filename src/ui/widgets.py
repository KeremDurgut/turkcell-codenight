"""
Turkcell Decision Engine - Custom Widgets
Yeniden kullanılabilir UI bileşenleri
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from .styles import (
    TURKCELL_YELLOW, TURKCELL_BLUE, TURKCELL_DARK,
    BG_WHITE, BORDER_GRAY, TEXT_PRIMARY, TEXT_SECONDARY,
    RISK_COLORS, ACTION_COLORS, CARD_STYLE, STAT_CARD_STYLE,
    COLOR_SUCCESS
)


class StatCard(QFrame):
    """İstatistik kartı widget'ı"""
    
    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WHITE};
                border: 1px solid {BORDER_GRAY};
                border-radius: 16px;
            }}
        """)
        self.setMinimumSize(180, 120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 11px;
            color: {TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        # Value - LARGE AND VISIBLE
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {TURKCELL_BLUE};
            background: transparent;
        """)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
    
    def set_value(self, value: str):
        """Update the value"""
        self.value_label.setText(value)
        self.value_label.repaint()  # Force repaint


class DataTable(QTableWidget):
    """Özelleştirilmiş data tablosu"""
    
    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setDefaultSectionSize(120)
        
        # Configure table
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(45)
    
    def populate(self, data: list):
        """Populate table with data"""
        self.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)


class RiskBadge(QLabel):
    """Risk seviyesi badge'i"""
    
    def __init__(self, risk_level: str = "LOW", parent=None):
        super().__init__(parent)
        self.set_level(risk_level)
    
    def set_level(self, level: str):
        """Set risk level"""
        color = RISK_COLORS.get(level, COLOR_SUCCESS)
        self.setText(level)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 0.5px;
        """)


class ActionBadge(QLabel):
    """Aksiyon türü badge'i"""
    
    def __init__(self, action_type: str, parent=None):
        super().__init__(parent)
        self.set_type(action_type)
    
    def set_type(self, action_type: str):
        """Set action type"""
        color = ACTION_COLORS.get(action_type, TURKCELL_BLUE)
        # Shorten label
        short_labels = {
            'CRITICAL_ALERT': 'CRITICAL',
            'DATA_USAGE_WARNING': 'DATA WARN',
            'SPEND_ALERT': 'SPEND',
            'CONTENT_COOLDOWN_SUGGESTION': 'CONTENT',
            'DATA_USAGE_NUDGE': 'NUDGE',
            'SPEND_NUDGE': 'NUDGE'
        }
        label = short_labels.get(action_type, action_type[:10])
        self.setText(label)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 5px 10px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 10px;
        """)


class UserStateCard(QFrame):
    """Kullanıcı durum kartı"""
    
    def __init__(self, user_data: dict = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self.setMinimumWidth(280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        if user_data:
            self.populate(user_data)
    
    def populate(self, data: dict):
        """Populate card with user data"""
        # Clear existing
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        layout = self.layout()
        
        # Header with user name and risk badge
        header_layout = QHBoxLayout()
        
        user_label = QLabel(f"👤 {data.get('user_id', 'N/A')}")
        user_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {TURKCELL_DARK};
        """)
        header_layout.addWidget(user_label)
        
        header_layout.addStretch()
        
        risk_badge = RiskBadge(data.get('risk_level', 'LOW'))
        header_layout.addWidget(risk_badge)
        
        layout.addLayout(header_layout)
        
        # Stats
        stats = [
            ("İnternet", f"{data.get('internet_today_gb', 0):.1f} GB"),
            ("Harcama", f"₺{data.get('spend_today_try', 0):.0f}"),
            ("İçerik", f"{data.get('content_minutes_today', 0):.0f} dk")
        ]
        
        for label, value in stats:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel(value)
            val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600;")
            row.addWidget(val)
            layout.addLayout(row)


class SectionHeader(QWidget):
    """Bölüm başlığı"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        
        label = QLabel(title)
        label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {TURKCELL_DARK};
        """)
        layout.addWidget(label)
        layout.addStretch()
