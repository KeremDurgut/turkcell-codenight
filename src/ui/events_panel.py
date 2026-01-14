"""
Turkcell Decision Engine - Events Panel
View and manage events
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QFormLayout,
    QDialog, QDialogButtonBox, QMessageBox, QSpinBox,
    QDateTimeEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime

from .widgets import DataTable, SectionHeader
from .styles import TURKCELL_YELLOW
from ..database import db, EventRepository, UserRepository
from ..rule_engine import rule_engine


class AddEventDialog(QDialog):
    """Dialog for adding a new event"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Event Ekle")
        self.setMinimumWidth(400)
        
        self.user_repo = UserRepository(db)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # User selection
        self.user_combo = QComboBox()
        users = self.user_repo.get_all()
        for user in users:
            self.user_combo.addItem(f"{user['name']} ({user['user_id']})", user['user_id'])
        form.addRow("Kullanıcı:", self.user_combo)
        
        # Service selection
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Superonline', 'Paycell', 'TV+', 'Fizy', 'Game+', 'BiP'])
        form.addRow("Servis:", self.service_combo)
        
        # Event type
        self.type_combo = QComboBox()
        self.type_combo.addItems(['USAGE', 'PAYMENT', 'CONTENT_CONSUMPTION'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form.addRow("Event Türü:", self.type_combo)
        
        # Value
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0, 999999)
        self.value_spin.setDecimals(2)
        form.addRow("Değer:", self.value_spin)
        
        # Unit (auto-selected based on type)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['GB', 'TRY', 'MIN'])
        form.addRow("Birim:", self.unit_combo)
        
        # Timestamp
        self.timestamp_edit = QDateTimeEdit()
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        self.timestamp_edit.setCalendarPopup(True)
        form.addRow("Zaman:", self.timestamp_edit)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set initial unit based on type
        self.on_type_changed(self.type_combo.currentText())
    
    def on_type_changed(self, event_type: str):
        """Update unit based on event type"""
        unit_map = {
            'USAGE': 'GB',
            'PAYMENT': 'TRY',
            'CONTENT_CONSUMPTION': 'MIN'
        }
        unit = unit_map.get(event_type, 'GB')
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
    
    def get_event_data(self) -> dict:
        """Get the entered event data"""
        # Generate event ID
        event_id = f"EVT-{int(datetime.now().timestamp())}"
        
        return {
            'event_id': event_id,
            'user_id': self.user_combo.currentData(),
            'service': self.service_combo.currentText(),
            'event_type': self.type_combo.currentText(),
            'value': self.value_spin.value(),
            'unit': self.unit_combo.currentText(),
            'timestamp': self.timestamp_edit.dateTime().toPyDateTime()
        }


class EventsPanel(QWidget):
    """Panel for viewing and managing events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_repo = EventRepository(db)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("📨 Event Yönetimi")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_YELLOW};")
        
        # Action buttons
        add_btn = QPushButton("➕ Yeni Event")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_event)
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(refresh_btn)
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
        
        filter_layout.addWidget(QLabel("Servis:"))
        self.service_filter = QComboBox()
        self.service_filter.addItems(['Tümü', 'Superonline', 'Paycell', 'TV+', 'Fizy', 'Game+'])
        self.service_filter.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.service_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Events table
        self.events_table = DataTable([
            "Event ID", "Kullanıcı", "Servis", "Tür", "Değer", "Birim", "Zaman"
        ])
        layout.addWidget(self.events_table)
    
    def load_data(self):
        """Load events from database"""
        try:
            user_id = self.user_filter.currentData()
            
            if user_id:
                events = self.event_repo.get_by_user(user_id)
            else:
                events = self.event_repo.get_all(100)
            
            # Filter by service if selected
            service = self.service_filter.currentText()
            if service != 'Tümü':
                events = [e for e in events if e.get('service') == service]
            
            table_data = []
            for event in events:
                table_data.append({
                    'event id': event.get('event_id', ''),
                    'kullanıcı': event.get('user_id', ''),
                    'servis': event.get('service', ''),
                    'tür': event.get('event_type', ''),
                    'değer': str(event.get('value', 0)),
                    'birim': event.get('unit', ''),
                    'zaman': str(event.get('timestamp', ''))[:19]
                })
            
            self.events_table.populate(table_data)
        except Exception as e:
            print(f"Error loading events: {e}")
    
    def add_event(self):
        """Show dialog to add new event"""
        dialog = AddEventDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            event_data = dialog.get_event_data()
            if self.event_repo.create(event_data):
                self.load_data()
                
                # Automatically run rule engine for this user
                user_id = event_data['user_id']
                result = rule_engine.process_user(user_id)
                
                if result:
                    # Show notification with triggered action
                    action_type = result['decision']['selected_action']
                    message = result['action']['message']
                    triggered = ', '.join(result['decision']['triggered_rules'])
                    
                    QMessageBox.warning(
                        self, 
                        f"🔔 {action_type}",
                        f"<b>Kullanıcı:</b> {user_id}<br><br>"
                        f"<b>Tetiklenen Kurallar:</b> {triggered}<br><br>"
                        f"<b>BiP Bildirimi:</b><br>{message}"
                    )
                else:
                    QMessageBox.information(
                        self, 
                        "✅ Event Eklendi", 
                        f"Event başarıyla eklendi.\nHerhangi bir kural tetiklenmedi."
                    )
            else:
                QMessageBox.warning(self, "Hata", "Event eklenirken bir hata oluştu.")

