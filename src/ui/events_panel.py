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
from .styles import TURKCELL_BLUE
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
        
        # Service selection - also sets appropriate event type
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Superonline', 'Paycell', 'TV+', 'Fizy', 'Game+', 'BiP'])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        form.addRow("Servis:", self.service_combo)
        
        # Event type - auto-set based on service
        self.type_combo = QComboBox()
        self.type_combo.addItems(['USAGE', 'PAYMENT', 'CONTENT_CONSUMPTION'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form.addRow("Event Türü:", self.type_combo)
        
        # Value with appropriate label
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0, 999999)
        self.value_spin.setDecimals(2)
        self.value_label = QLabel("Değer:")
        form.addRow(self.value_label, self.value_spin)
        
        # Unit - READ ONLY, auto-set based on event type
        self.unit_label = QLabel("GB")
        self.unit_label.setStyleSheet("font-weight: bold; padding: 8px; background-color: #E0E0E0; border-radius: 4px;")
        form.addRow("Birim:", self.unit_label)
        
        # Store unit value internally
        self.current_unit = 'GB'
        
        # Timestamp
        self.timestamp_edit = QDateTimeEdit()
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        self.timestamp_edit.setCalendarPopup(True)
        form.addRow("Zaman:", self.timestamp_edit)
        
        layout.addLayout(form)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set initial values based on service
        self.on_service_changed(self.service_combo.currentText())
    
    def on_service_changed(self, service: str):
        """Update event type based on service"""
        # Service to default event type mapping
        service_type_map = {
            'Superonline': 'USAGE',
            'Paycell': 'PAYMENT',
            'TV+': 'CONTENT_CONSUMPTION',
            'Fizy': 'CONTENT_CONSUMPTION',
            'Game+': 'CONTENT_CONSUMPTION',
            'BiP': 'USAGE'
        }
        event_type = service_type_map.get(service, 'USAGE')
        index = self.type_combo.findText(event_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Update info
        self.update_info()
    
    def on_type_changed(self, event_type: str):
        """Update unit based on event type - LOCKED"""
        unit_map = {
            'USAGE': 'GB',
            'PAYMENT': 'TRY',
            'CONTENT_CONSUMPTION': 'MIN'
        }
        label_map = {
            'USAGE': 'İnternet Kullanımı (GB):',
            'PAYMENT': 'Harcama Tutarı (₺):',
            'CONTENT_CONSUMPTION': 'İçerik Süresi (dakika):'
        }
        
        self.current_unit = unit_map.get(event_type, 'GB')
        self.unit_label.setText(self.current_unit)
        self.value_label.setText(label_map.get(event_type, 'Değer:'))
        
        self.update_info()
    
    def update_info(self):
        """Update info label with explanation"""
        event_type = self.type_combo.currentText()
        info_map = {
            'USAGE': 'Bu event kullanıcının günlük internet kullanımına (internet_today_gb) eklenir.',
            'PAYMENT': 'Bu event kullanıcının günlük harcamasına (spend_today_try) eklenir.',
            'CONTENT_CONSUMPTION': 'Bu event kullanıcının günlük içerik süresine (content_minutes_today) eklenir.'
        }
        self.info_label.setText(info_map.get(event_type, ''))

    
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
            'unit': self.current_unit,  # Use locked unit based on event type
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
        title = QLabel("Event Yönetimi")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_BLUE};")
        
        # Action buttons
        add_btn = QPushButton("Yeni Event")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_event)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
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
                # Evaluate ALL rules based on cumulative user_state totals
                # This catches thresholds exceeded by many small events (e.g., 2GB x 40 = 80GB)
                user_id = event_data['user_id']
                result = rule_engine.process_user(user_id)  # No event_type filter - check all rules
                
                if result:
                    # Build detailed message
                    decision = result['decision']
                    action = result['action']
                    triggered = result.get('triggered_rules', [])
                    suppressed = result.get('suppressed_rules', [])
                    
                    # Rule details
                    rules_text = ""
                    for i, rule in enumerate(triggered):
                        marker = "SEÇİLDİ" if i == 0 else ""
                        rules_text += f"<br>#{rule.get('priority', i+1)} <b>{rule.get('rule_id', '')}</b> → {rule.get('action', '')} {marker}"
                    
                    # Suppressed actions
                    supp_text = ""
                    if suppressed:
                        supp_actions = [r.get('action', '') for r in suppressed]
                        supp_text = f"<br><br><b>Bastırılan:</b> {', '.join(supp_actions)}"
                    
                    msg = QMessageBox(self)
                    msg.setWindowTitle(f"Bildirim: {decision['selected_action']}")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setTextFormat(Qt.TextFormat.RichText)
                    msg.setText(f"""
                        <h2>{decision['selected_action'].replace('_', ' ')}</h2>
                        <p><b>Kullanıcı:</b> {user_id}</p>
                        <hr>
                        <p><b>BiP Bildirimi:</b></p>
                        <p style="background:#f0f0f0; padding:10px; border-radius:5px;">{action['message']}</p>
                        <hr>
                        <p><b>Tetiklenen Kurallar ({len(triggered)}):</b></p>
                        {rules_text}
                        {supp_text}
                    """)
                    msg.exec()
                else:
                    QMessageBox.information(
                        self, 
                        "Event Eklendi", 
                        f"Event başarıyla eklendi.\nKullanıcı {user_id} için herhangi bir kural tetiklenmedi."
                    )
            else:
                QMessageBox.warning(self, "Hata", "Event eklenirken bir hata oluştu.")


