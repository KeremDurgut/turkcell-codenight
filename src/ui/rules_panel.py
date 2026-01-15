"""
Turkcell Decision Engine - Rules Panel
View and manage decision rules (Bonus Feature)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QFormLayout,
    QDialog, QDialogButtonBox, QMessageBox, QSpinBox,
    QCheckBox, QTextEdit, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .widgets import DataTable, SectionHeader
from .styles import TURKCELL_BLUE, RISK_COLORS, ACTION_COLORS
from ..database import db, RuleRepository


class RuleDialog(QDialog):
    """Dialog for adding/editing a rule"""
    
    def __init__(self, rule_data: dict = None, parent=None):
        super().__init__(parent)
        self.rule_data = rule_data
        self.is_edit = rule_data is not None
        
        self.setWindowTitle("Kural Düzenle" if self.is_edit else "Yeni Kural Ekle")
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if self.is_edit:
            self.populate_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Rule ID
        self.rule_id_input = QLineEdit()
        if self.is_edit:
            self.rule_id_input.setReadOnly(True)
        else:
            self.rule_id_input.setPlaceholderText("Örn: R-07")
        form.addRow("Kural ID:", self.rule_id_input)
        
        # Condition
        self.condition_input = QTextEdit()
        self.condition_input.setMaximumHeight(80)
        self.condition_input.setPlaceholderText("Örn: internet_today_gb > 15 AND spend_today_try > 300")
        form.addRow("Koşul:", self.condition_input)
        
        # Help text for conditions
        help_label = QLabel("""
        <small>Kullanılabilir alanlar: <b>internet_today_gb</b>, <b>spend_today_try</b>, <b>content_minutes_today</b><br>
        Operatörler: >, <, >=, <=, ==, AND, OR, BETWEEN X AND Y</small>
        """)
        help_label.setWordWrap(True)
        form.addRow("", help_label)
        
        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            'DATA_USAGE_WARNING',
            'SPEND_ALERT',
            'CONTENT_COOLDOWN_SUGGESTION',
            'CRITICAL_ALERT',
            'DATA_USAGE_NUDGE',
            'SPEND_NUDGE'
        ])
        form.addRow("Aksiyon:", self.action_combo)
        
        # Priority
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(5)
        form.addRow("Öncelik (1=En Yüksek):", self.priority_spin)
        
        # Active status
        self.active_check = QCheckBox("Aktif")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Kural açıklaması (opsiyonel)")
        form.addRow("Açıklama:", self.description_input)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def populate_data(self):
        """Populate form with existing rule data"""
        self.rule_id_input.setText(self.rule_data.get('rule_id', ''))
        self.condition_input.setText(self.rule_data.get('condition', ''))
        
        action = self.rule_data.get('action', '')
        index = self.action_combo.findText(action)
        if index >= 0:
            self.action_combo.setCurrentIndex(index)
        
        self.priority_spin.setValue(self.rule_data.get('priority', 5))
        self.active_check.setChecked(self.rule_data.get('is_active', True))
        self.description_input.setText(self.rule_data.get('description', '') or '')
    
    def validate_and_accept(self):
        """Validate input before accepting"""
        if not self.rule_id_input.text().strip():
            QMessageBox.warning(self, "Hata", "Kural ID boş olamaz!")
            return
        
        if not self.condition_input.toPlainText().strip():
            QMessageBox.warning(self, "Hata", "Koşul boş olamaz!")
            return
        
        self.accept()
    
    def get_rule_data(self) -> dict:
        """Get the entered rule data"""
        return {
            'rule_id': self.rule_id_input.text().strip(),
            'condition': self.condition_input.toPlainText().strip(),
            'action': self.action_combo.currentText(),
            'priority': self.priority_spin.value(),
            'is_active': self.active_check.isChecked(),
            'description': self.description_input.text().strip()
        }


class RulesPanel(QWidget):
    """Panel for viewing and managing rules (Bonus Feature)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rule_repo = RuleRepository(db)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Kural Yönetimi")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_BLUE};")
        
        # Bonus badge
        bonus_badge = QLabel("BONUS")
        bonus_badge.setStyleSheet("""
            background-color: #2ED573;
            color: #1A1A2E;
            padding: 4px 12px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 10px;
        """)
        
        # Action buttons
        add_btn = QPushButton("Yeni Kural")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_rule)
        
        header_layout.addWidget(title)
        header_layout.addWidget(bonus_badge)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Info text
        info = QLabel("Kurallar, kullanıcı durumuna göre çalışır. Düşük öncelik numarası = yüksek öncelik.")
        info.setStyleSheet("color: #8B8B8B; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Rules table
        self.rules_table = DataTable([
            "Kural ID", "Koşul", "Aksiyon", "Öncelik", "Durum", "Açıklama"
        ])
        self.rules_table.doubleClicked.connect(self.edit_rule)
        layout.addWidget(self.rules_table)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Düzenle")
        edit_btn.clicked.connect(self.edit_selected_rule)
        
        toggle_btn = QPushButton("Aktif/Pasif")
        toggle_btn.clicked.connect(self.toggle_selected_rule)
        
        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(toggle_btn)
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Load rules from database"""
        try:
            rules = self.rule_repo.get_all()
            
            self.rules_table.setRowCount(len(rules))
            
            for row_idx, rule in enumerate(rules):
                # Rule ID
                self.rules_table.setItem(row_idx, 0, QTableWidgetItem(rule.get('rule_id', '')))
                
                # Condition (truncated)
                condition = rule.get('condition', '')
                if len(condition) > 40:
                    condition = condition[:40] + '...'
                self.rules_table.setItem(row_idx, 1, QTableWidgetItem(condition))
                
                # Action (colored)
                action = rule.get('action', '')
                action_item = QTableWidgetItem(action)
                color = ACTION_COLORS.get(action, '#FFFFFF')
                action_item.setForeground(QColor(color))
                self.rules_table.setItem(row_idx, 2, action_item)
                
                # Priority
                self.rules_table.setItem(row_idx, 3, QTableWidgetItem(str(rule.get('priority', ''))))
                
                # Status
                is_active = rule.get('is_active', False)
                status_item = QTableWidgetItem("Aktif" if is_active else "Pasif")
                status_item.setForeground(QColor('#2ED573' if is_active else '#FF4757'))
                self.rules_table.setItem(row_idx, 4, status_item)
                
                # Description
                self.rules_table.setItem(row_idx, 5, QTableWidgetItem(rule.get('description', '') or ''))
                
        except Exception as e:
            print(f"Error loading rules: {e}")
    
    def add_rule(self):
        """Show wizard to add new rule"""
        from .rule_wizard import RuleWizardDialog
        
        dialog = RuleWizardDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule_data = dialog.get_rule_data()
            if self.rule_repo.create(rule_data):
                QMessageBox.information(self, "Başarılı", "Kural başarıyla eklendi!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Hata", "Kural eklenirken bir hata oluştu.")
    
    def edit_rule(self, index):
        """Edit rule at index"""
        row = index.row()
        self.edit_rule_at_row(row)
    
    def edit_selected_rule(self):
        """Edit currently selected rule"""
        selected = self.rules_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kural seçin.")
            return
        
        row = selected[0].row()
        self.edit_rule_at_row(row)
    
    def edit_rule_at_row(self, row: int):
        """Edit rule at specific row"""
        rule_id = self.rules_table.item(row, 0).text()
        rule_data = self.rule_repo.get_by_id(rule_id)
        
        if rule_data:
            dialog = RuleDialog(dict(rule_data), parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_rule_data()
                if self.rule_repo.update(rule_id, updated_data):
                    QMessageBox.information(self, "Başarılı", "Kural güncellendi!")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Hata", "Kural güncellenirken bir hata oluştu.")
    
    def toggle_selected_rule(self):
        """Toggle active status of selected rule"""
        selected = self.rules_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kural seçin.")
            return
        
        row = selected[0].row()
        rule_id = self.rules_table.item(row, 0).text()
        
        if self.rule_repo.toggle_active(rule_id):
            self.load_data()
        else:
            QMessageBox.warning(self, "Hata", "Durum değiştirilemedi.")
