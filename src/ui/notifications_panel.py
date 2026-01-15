"""
Turkcell Decision Engine - Notifications Panel
View sent BiP notifications/messages
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTableWidgetItem, QTextEdit,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .widgets import DataTable, SectionHeader
from .styles import TURKCELL_BLUE, ACTION_COLORS, TEXT_SECONDARY
from ..database import db, ActionRepository, UserRepository


class NotificationDetailDialog(QDialog):
    """Dialog showing notification details"""
    
    def __init__(self, action_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Bildirim Detayı - {action_data.get('action_id', '')}")
        self.setMinimumSize(450, 300)
        
        layout = QVBoxLayout(self)
        
        action_type = action_data.get('action_type', '')
        color = ACTION_COLORS.get(action_type, '#FFFFFF')
        
        info_text = f"""
        <h2 style="color: {color};">{action_type}</h2>
        <hr>
        <p><b>Bildirim ID:</b> {action_data.get('action_id', '')}</p>
        <p><b>Kullanıcı:</b> {action_data.get('user_name', action_data.get('user_id', ''))}</p>
        <p><b>Gönderim Zamanı:</b> {action_data.get('created_at', '')}</p>
        <p><b>Gönderim Kanalı:</b> {action_data.get('sent_via', 'BiP')}</p>
        <hr>
        <p><b>Mesaj İçeriği:</b></p>
        <div style="background-color: #1E2746; padding: 15px; border-radius: 8px; margin-top: 10px;">
            {action_data.get('message', 'Mesaj bulunamadı')}
        </div>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class NotificationsPanel(QWidget):
    """Panel for viewing sent notifications/messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_repo = ActionRepository(db)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("BiP Bildirimleri")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_BLUE};")
        
        # Info badge
        info_badge = QLabel("Gönderilen tüm bildirimler")
        info_badge.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(info_badge)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Filter row
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Kullanıcı:"))
        self.user_filter = QComboBox()
        self.user_filter.addItem("Tümü", None)
        user_repo = UserRepository(db)
        for user in user_repo.get_all():
            self.user_filter.addItem(f"{user['name']}", user['user_id'])
        self.user_filter.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.user_filter)
        
        filter_layout.addWidget(QLabel("Bildirim Türü:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            'Tümü', 
            'CRITICAL_ALERT',
            'SPEND_ALERT', 
            'DATA_USAGE_WARNING',
            'CONTENT_COOLDOWN_SUGGESTION',
            'DATA_USAGE_NUDGE',
            'SPEND_NUDGE'
        ])
        self.type_filter.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Notifications table
        self.notifications_table = DataTable([
            "ID", "Kullanıcı", "Bildirim Türü", "Mesaj", "Zaman"
        ])
        self.notifications_table.doubleClicked.connect(self.show_detail)
        layout.addWidget(self.notifications_table)
        
        # Stats row
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Toplam: 0 bildirim")
        self.stats_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
    
    def load_data(self):
        """Load notifications from database"""
        try:
            user_id = self.user_filter.currentData()
            
            if user_id:
                actions = self.action_repo.get_by_user(user_id)
            else:
                actions = self.action_repo.get_all(100)
            
            # Filter by type if selected
            action_type = self.type_filter.currentText()
            if action_type != 'Tümü':
                actions = [a for a in actions if a.get('action_type') == action_type]
            
            self.current_actions = actions  # Store for detail view
            
            self.notifications_table.setRowCount(len(actions))
            
            for row_idx, action in enumerate(actions):
                # ID
                self.notifications_table.setItem(row_idx, 0, 
                    QTableWidgetItem(action.get('action_id', '')))
                
                # User
                self.notifications_table.setItem(row_idx, 1, 
                    QTableWidgetItem(action.get('user_name', action.get('user_id', ''))))
                
                # Action type (colored)
                action_type = action.get('action_type', '')
                type_item = QTableWidgetItem(action_type)
                color = ACTION_COLORS.get(action_type, '#FFFFFF')
                type_item.setForeground(QColor(color))
                self.notifications_table.setItem(row_idx, 2, type_item)
                
                # Message (truncated)
                message = action.get('message', '') or ''
                if len(message) > 50:
                    message = message[:50] + '...'
                self.notifications_table.setItem(row_idx, 3, QTableWidgetItem(message))
                
                # Timestamp
                self.notifications_table.setItem(row_idx, 4, 
                    QTableWidgetItem(str(action.get('created_at', ''))[:19]))
            
            self.stats_label.setText(f"Toplam: {len(actions)} bildirim")
                
        except Exception as e:
            print(f"Error loading notifications: {e}")
    
    def show_detail(self, index):
        """Show notification detail dialog"""
        row = index.row()
        if row < len(self.current_actions):
            dialog = NotificationDetailDialog(dict(self.current_actions[row]), self)
            dialog.exec()
