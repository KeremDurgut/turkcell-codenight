"""
Turkcell Decision Engine - Rule Wizard Dialog
Adım adım kural oluşturma wizard'ı
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QStackedWidget, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QCheckBox, QWidget,
    QButtonGroup, QRadioButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .styles import (
    TURKCELL_YELLOW, TURKCELL_BLUE, TURKCELL_DARK,
    BG_WHITE, BG_GRAY, BORDER_GRAY, TEXT_PRIMARY, TEXT_SECONDARY,
    COLOR_SUCCESS, ACTION_COLORS
)


class RuleWizardDialog(QDialog):
    """
    Wizard-style dialog for creating rules step by step.
    Prevents syntax errors by guiding the user through each step.
    """
    
    # Available fields for conditions
    FIELDS = {
        'internet_today_gb': {
            'label': '🌐 Günlük İnternet Kullanımı (GB)',
            'unit': 'GB',
            'min': 0,
            'max': 1000
        },
        'spend_today_try': {
            'label': '💳 Günlük Harcama (₺)',
            'unit': '₺',
            'min': 0,
            'max': 10000
        },
        'content_minutes_today': {
            'label': '📺 Günlük İçerik Süresi (dakika)',
            'unit': 'dk',
            'min': 0,
            'max': 1440
        }
    }
    
    # Available operators
    OPERATORS = {
        '>': 'Büyüktür (>)',
        '>=': 'Büyük Eşittir (>=)',
        '<': 'Küçüktür (<)',
        '<=': 'Küçük Eşittir (<=)',
        '==': 'Eşittir (==)',
        'BETWEEN': 'Arasında (BETWEEN)'
    }
    
    # Available actions
    ACTIONS = {
        'DATA_USAGE_WARNING': '📊 Veri Kullanım Uyarısı',
        'SPEND_ALERT': '💳 Harcama Uyarısı',
        'CONTENT_COOLDOWN_SUGGESTION': '☕ İçerik Mola Önerisi',
        'CRITICAL_ALERT': '🚨 Kritik Uyarı',
        'DATA_USAGE_NUDGE': '📶 Veri Kullanım Hatırlatması',
        'SPEND_NUDGE': '💰 Harcama Hatırlatması'
    }
    
    def __init__(self, rule_data: dict = None, parent=None):
        super().__init__(parent)
        self.rule_data = rule_data
        self.is_edit = rule_data is not None
        self.conditions = []  # List of condition dicts
        
        self.setWindowTitle("Kural Oluşturma Sihirbazı" if not self.is_edit else "Kural Düzenleme")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"background-color: {BG_WHITE};")
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_existing_rule()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {TURKCELL_DARK}, stop:1 {TURKCELL_BLUE});
                padding: 20px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        
        self.title_label = QLabel("📋 Yeni Kural Oluştur")
        self.title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {TURKCELL_YELLOW};
        """)
        header_layout.addWidget(self.title_label)
        
        self.step_label = QLabel("Adım 1/4: Koşul Tanımlama")
        self.step_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        header_layout.addWidget(self.step_label)
        
        layout.addWidget(header)
        
        # Stacked widget for steps
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG_WHITE};")
        
        # Step 1: Condition Builder
        self.step1 = self.create_step1_condition()
        self.stack.addWidget(self.step1)
        
        # Step 2: Additional Conditions
        self.step2 = self.create_step2_additional()
        self.stack.addWidget(self.step2)
        
        # Step 3: Action Selection
        self.step3 = self.create_step3_action()
        self.stack.addWidget(self.step3)
        
        # Step 4: Priority & Summary
        self.step4 = self.create_step4_summary()
        self.stack.addWidget(self.step4)
        
        layout.addWidget(self.stack)
        
        # Navigation buttons
        nav_frame = QFrame()
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_GRAY};
                border-top: 1px solid {BORDER_GRAY};
                padding: 15px;
            }}
        """)
        nav_layout = QHBoxLayout(nav_frame)
        
        self.back_btn = QPushButton("◀ Geri")
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TURKCELL_BLUE};
                border: 2px solid {TURKCELL_BLUE};
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {TURKCELL_BLUE};
                color: white;
            }}
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        self.next_btn = QPushButton("İleri ▶")
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {TURKCELL_YELLOW};
                color: {TURKCELL_DARK};
                border: none;
                padding: 12px 32px;
                border-radius: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #E6B800;
            }}
        """)
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        layout.addWidget(nav_frame)
    
    def create_step1_condition(self) -> QWidget:
        """Step 1: Define first condition"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Field selection
        field_label = QLabel("Hangi değeri kontrol etmek istiyorsunuz?")
        field_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        layout.addWidget(field_label)
        
        self.field_combo = QComboBox()
        self.field_combo.setMinimumHeight(45)
        for field_id, field_info in self.FIELDS.items():
            self.field_combo.addItem(field_info['label'], field_id)
        self.field_combo.currentIndexChanged.connect(self.on_field_changed)
        layout.addWidget(self.field_combo)
        
        # Operator selection
        op_label = QLabel("Hangi koşulu kullanmak istiyorsunuz?")
        op_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px; margin-top: 10px;")
        layout.addWidget(op_label)
        
        self.operator_combo = QComboBox()
        self.operator_combo.setMinimumHeight(45)
        for op_id, op_label in self.OPERATORS.items():
            self.operator_combo.addItem(op_label, op_id)
        self.operator_combo.currentIndexChanged.connect(self.on_operator_changed)
        layout.addWidget(self.operator_combo)
        
        # Value input
        value_label = QLabel("Değer:")
        value_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px; margin-top: 10px;")
        layout.addWidget(value_label)
        
        value_frame = QHBoxLayout()
        
        self.value1_spin = QDoubleSpinBox()
        self.value1_spin.setMinimumHeight(45)
        self.value1_spin.setRange(0, 10000)
        self.value1_spin.setDecimals(1)
        value_frame.addWidget(self.value1_spin)
        
        self.between_label = QLabel("ile")
        self.between_label.setStyleSheet(f"color: {TEXT_SECONDARY}; margin: 0 10px;")
        self.between_label.hide()
        value_frame.addWidget(self.between_label)
        
        self.value2_spin = QDoubleSpinBox()
        self.value2_spin.setMinimumHeight(45)
        self.value2_spin.setRange(0, 10000)
        self.value2_spin.setDecimals(1)
        self.value2_spin.hide()
        value_frame.addWidget(self.value2_spin)
        
        self.unit_label = QLabel("GB")
        self.unit_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600; margin-left: 10px;")
        value_frame.addWidget(self.unit_label)
        
        value_frame.addStretch()
        layout.addLayout(value_frame)
        
        # Preview
        preview_label = QLabel("Koşul Önizleme:")
        preview_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; margin-top: 20px;")
        layout.addWidget(preview_label)
        
        self.condition_preview = QLabel("")
        self.condition_preview.setStyleSheet(f"""
            background-color: {BG_GRAY};
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            color: {TURKCELL_BLUE};
        """)
        layout.addWidget(self.condition_preview)
        
        layout.addStretch()
        
        # Connect signals for preview update
        self.value1_spin.valueChanged.connect(self.update_preview)
        self.value2_spin.valueChanged.connect(self.update_preview)
        
        return widget
    
    def create_step2_additional(self) -> QWidget:
        """Step 2: Additional conditions (AND/OR)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        question_label = QLabel("Ek koşul eklemek ister misiniz?")
        question_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        layout.addWidget(question_label)
        
        # Radio buttons for choice
        self.no_additional = QRadioButton("Hayır, tek koşul yeterli")
        self.no_additional.setChecked(True)
        self.no_additional.setStyleSheet("font-size: 13px; padding: 10px;")
        layout.addWidget(self.no_additional)
        
        self.yes_and = QRadioButton("Evet, AND (VE) ile ek koşul ekle")
        self.yes_and.setStyleSheet("font-size: 13px; padding: 10px;")
        self.yes_and.toggled.connect(self.on_additional_toggled)
        layout.addWidget(self.yes_and)
        
        self.yes_or = QRadioButton("Evet, OR (VEYA) ile ek koşul ekle")
        self.yes_or.setStyleSheet("font-size: 13px; padding: 10px;")
        self.yes_or.toggled.connect(self.on_additional_toggled)
        layout.addWidget(self.yes_or)
        
        # Additional condition frame (hidden by default)
        self.additional_frame = QFrame()
        self.additional_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_GRAY};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        self.additional_frame.hide()
        
        add_layout = QVBoxLayout(self.additional_frame)
        
        add_field_label = QLabel("Ek koşul alanı:")
        add_field_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK};")
        add_layout.addWidget(add_field_label)
        
        self.add_field_combo = QComboBox()
        self.add_field_combo.setMinimumHeight(40)
        for field_id, field_info in self.FIELDS.items():
            self.add_field_combo.addItem(field_info['label'], field_id)
        add_layout.addWidget(self.add_field_combo)
        
        add_op_label = QLabel("Operatör:")
        add_op_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; margin-top: 10px;")
        add_layout.addWidget(add_op_label)
        
        self.add_operator_combo = QComboBox()
        self.add_operator_combo.setMinimumHeight(40)
        for op_id, op_label in self.OPERATORS.items():
            if op_id != 'BETWEEN':  # Simplify for additional
                self.add_operator_combo.addItem(op_label, op_id)
        add_layout.addWidget(self.add_operator_combo)
        
        add_value_label = QLabel("Değer:")
        add_value_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; margin-top: 10px;")
        add_layout.addWidget(add_value_label)
        
        self.add_value_spin = QDoubleSpinBox()
        self.add_value_spin.setMinimumHeight(40)
        self.add_value_spin.setRange(0, 10000)
        self.add_value_spin.setDecimals(1)
        add_layout.addWidget(self.add_value_spin)
        
        layout.addWidget(self.additional_frame)
        
        layout.addStretch()
        
        return widget
    
    def create_step3_action(self) -> QWidget:
        """Step 3: Select action"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        action_label = QLabel("Bu kural tetiklendiğinde hangi aksiyon alınsın?")
        action_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        layout.addWidget(action_label)
        
        # Action radio buttons
        self.action_group = QButtonGroup(self)
        
        for action_id, action_label in self.ACTIONS.items():
            action_color = ACTION_COLORS.get(action_id, TURKCELL_BLUE)
            radio = QRadioButton(action_label)
            radio.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 13px;
                    padding: 12px;
                    background-color: {BG_GRAY};
                    border-radius: 8px;
                    margin: 2px 0;
                }}
                QRadioButton:checked {{
                    background-color: {action_color}20;
                    border: 2px solid {action_color};
                }}
            """)
            radio.setProperty("action_id", action_id)
            self.action_group.addButton(radio)
            layout.addWidget(radio)
        
        # Select first by default
        first_btn = self.action_group.buttons()[0]
        first_btn.setChecked(True)
        
        layout.addStretch()
        
        return widget
    
    def create_step4_summary(self) -> QWidget:
        """Step 4: Priority and Summary"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Rule ID
        id_label = QLabel("Kural ID:")
        id_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px;")
        layout.addWidget(id_label)
        
        self.rule_id_input = QLineEdit()
        self.rule_id_input.setMinimumHeight(45)
        self.rule_id_input.setPlaceholderText("Örn: R-07")
        layout.addWidget(self.rule_id_input)
        
        # Priority
        priority_label = QLabel("Öncelik (1 = En Yüksek):")
        priority_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px; margin-top: 10px;")
        layout.addWidget(priority_label)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setMinimumHeight(45)
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(5)
        layout.addWidget(self.priority_spin)
        
        # Description
        desc_label = QLabel("Açıklama (isteğe bağlı):")
        desc_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px; margin-top: 10px;")
        layout.addWidget(desc_label)
        
        self.description_input = QLineEdit()
        self.description_input.setMinimumHeight(45)
        self.description_input.setPlaceholderText("Bu kuralın amacını açıklayın")
        layout.addWidget(self.description_input)
        
        # Summary
        summary_label = QLabel("Kural Özeti:")
        summary_label.setStyleSheet(f"font-weight: 600; color: {TURKCELL_DARK}; font-size: 14px; margin-top: 20px;")
        layout.addWidget(summary_label)
        
        self.summary_text = QLabel("")
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet(f"""
            background-color: {BG_GRAY};
            padding: 20px;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.6;
        """)
        layout.addWidget(self.summary_text)
        
        layout.addStretch()
        
        return widget
    
    def on_field_changed(self, index):
        """Update unit label when field changes"""
        field_id = self.field_combo.currentData()
        if field_id in self.FIELDS:
            self.unit_label.setText(self.FIELDS[field_id]['unit'])
        self.update_preview()
    
    def on_operator_changed(self, index):
        """Show/hide second value for BETWEEN"""
        op = self.operator_combo.currentData()
        is_between = (op == 'BETWEEN')
        self.between_label.setVisible(is_between)
        self.value2_spin.setVisible(is_between)
        self.update_preview()
    
    def on_additional_toggled(self, checked):
        """Show/hide additional condition frame"""
        show = self.yes_and.isChecked() or self.yes_or.isChecked()
        self.additional_frame.setVisible(show)
    
    def update_preview(self):
        """Update condition preview"""
        field = self.field_combo.currentData()
        op = self.operator_combo.currentData()
        value1 = self.value1_spin.value()
        value2 = self.value2_spin.value()
        
        if op == 'BETWEEN':
            preview = f"{field} BETWEEN {value1} AND {value2}"
        else:
            preview = f"{field} {op} {value1}"
        
        self.condition_preview.setText(preview)
    
    def update_summary(self):
        """Update summary on step 4"""
        # Build condition
        condition = self.build_condition()
        
        # Get selected action
        selected_btn = self.action_group.checkedButton()
        action = selected_btn.property("action_id") if selected_btn else ""
        action_label = self.ACTIONS.get(action, action)
        
        summary = f"""
        <b>Koşul:</b><br>
        <code style="background:#f0f0f0; padding:5px;">{condition}</code><br><br>
        <b>Aksiyon:</b> {action_label}<br>
        <b>Öncelik:</b> {self.priority_spin.value()}
        """
        
        self.summary_text.setText(summary)
    
    def build_condition(self) -> str:
        """Build condition string from wizard inputs"""
        field = self.field_combo.currentData()
        op = self.operator_combo.currentData()
        value1 = self.value1_spin.value()
        value2 = self.value2_spin.value()
        
        if op == 'BETWEEN':
            condition = f"{field} BETWEEN {value1} AND {value2}"
        else:
            condition = f"{field} {op} {value1}"
        
        # Add additional condition if selected
        if self.yes_and.isChecked() or self.yes_or.isChecked():
            connector = "AND" if self.yes_and.isChecked() else "OR"
            add_field = self.add_field_combo.currentData()
            add_op = self.add_operator_combo.currentData()
            add_value = self.add_value_spin.value()
            condition += f" {connector} {add_field} {add_op} {add_value}"
        
        return condition
    
    def go_back(self):
        """Go to previous step"""
        current = self.stack.currentIndex()
        if current > 0:
            self.stack.setCurrentIndex(current - 1)
            self.update_step_info()
    
    def go_next(self):
        """Go to next step or finish"""
        current = self.stack.currentIndex()
        
        if current < 3:
            self.stack.setCurrentIndex(current + 1)
            self.update_step_info()
            
            # Update summary when reaching step 4
            if current + 1 == 3:
                self.update_summary()
        else:
            # Finish - validate and accept
            self.finish_wizard()
    
    def update_step_info(self):
        """Update step indicator and buttons"""
        current = self.stack.currentIndex()
        steps = [
            "Adım 1/4: Koşul Tanımlama",
            "Adım 2/4: Ek Koşullar",
            "Adım 3/4: Aksiyon Seçimi",
            "Adım 4/4: Öncelik ve Özet"
        ]
        self.step_label.setText(steps[current])
        
        self.back_btn.setEnabled(current > 0)
        
        if current == 3:
            self.next_btn.setText("✓ Kaydet")
            self.next_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_SUCCESS};
                    color: white;
                    border: none;
                    padding: 12px 32px;
                    border-radius: 8px;
                    font-weight: 600;
                }}
            """)
        else:
            self.next_btn.setText("İleri ▶")
            self.next_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TURKCELL_YELLOW};
                    color: {TURKCELL_DARK};
                    border: none;
                    padding: 12px 32px;
                    border-radius: 8px;
                    font-weight: 600;
                }}
            """)
    
    def finish_wizard(self):
        """Validate and accept the wizard"""
        rule_id = self.rule_id_input.text().strip()
        
        if not rule_id:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir Kural ID girin.")
            return
        
        self.accept()
    
    def get_rule_data(self) -> dict:
        """Get the rule data from wizard"""
        selected_btn = self.action_group.checkedButton()
        action = selected_btn.property("action_id") if selected_btn else ""
        
        return {
            'rule_id': self.rule_id_input.text().strip(),
            'condition': self.build_condition(),
            'action': action,
            'priority': self.priority_spin.value(),
            'is_active': True,
            'description': self.description_input.text().strip()
        }
    
    def load_existing_rule(self):
        """Load existing rule data for editing"""
        # For edit mode - simplified, would need parsing logic
        self.title_label.setText("📋 Kural Düzenle")
        self.rule_id_input.setText(self.rule_data.get('rule_id', ''))
        self.rule_id_input.setReadOnly(True)
        self.priority_spin.setValue(self.rule_data.get('priority', 5))
        self.description_input.setText(self.rule_data.get('description', '') or '')
