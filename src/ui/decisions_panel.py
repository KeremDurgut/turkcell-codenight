"""
Turkcell Decision Engine - Decisions Panel
View decision history and audit logs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTableWidgetItem, QTextEdit,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import json

from .widgets import DataTable, SectionHeader
from .styles import TURKCELL_BLUE, ACTION_COLORS
from ..database import db, DecisionRepository, UserRepository
from ..rule_engine import rule_engine


class DecisionDetailDialog(QDialog):
    """Dialog showing decision details"""
    
    def __init__(self, decision_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Karar Detayı - {decision_data.get('decision_id', '')}")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Decision info
        info_text = f"""
        <h2>Karar: {decision_data.get('decision_id', '')}</h2>
        <p><b>Kullanıcı:</b> {decision_data.get('user_name', decision_data.get('user_id', ''))}</p>
        <p><b>Zaman:</b> {decision_data.get('timestamp', '')}</p>
        <hr>
        <p><b>Tetiklenen Kurallar:</b></p>
        <ul>
        """
        
        triggered = decision_data.get('triggered_rules', [])
        if isinstance(triggered, str):
            triggered = triggered.strip('{}').split(',')
        for rule in triggered:
            info_text += f"<li>{rule}</li>"
        info_text += "</ul>"
        
        info_text += f"""
        <p><b>Seçilen Aksiyon:</b> <span style="color: {ACTION_COLORS.get(decision_data.get('selected_action', ''), '#FFFFFF')}">{decision_data.get('selected_action', '')}</span></p>
        """
        
        suppressed = decision_data.get('suppressed_actions', [])
        if suppressed:
            if isinstance(suppressed, str):
                suppressed = suppressed.strip('{}').split(',')
            info_text += "<p><b>Bastırılan Aksiyonlar:</b></p><ul>"
            for action in suppressed:
                if action:
                    info_text += f"<li style='color: #8B8B8B;'>{action}</li>"
            info_text += "</ul>"
        
        # User state snapshot
        snapshot = decision_data.get('user_state_snapshot')
        if snapshot:
            try:
                state = json.loads(snapshot) if isinstance(snapshot, str) else snapshot
                info_text += """
                <hr>
                <p><b>Karar Anındaki Kullanıcı Durumu:</b></p>
                <ul>
                """
                info_text += f"<li>İnternet: {state.get('internet_today_gb', 0):.1f} GB</li>"
                info_text += f"<li>Harcama: {state.get('spend_today_try', 0):.0f} ₺</li>"
                info_text += f"<li>İçerik: {state.get('content_minutes_today', 0):.0f} dk</li>"
                info_text += f"<li>Risk: {state.get('risk_level', 'N/A')}</li>"
                info_text += "</ul>"
            except:
                pass
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class DecisionsPanel(QWidget):
    """Panel for viewing decisions and audit logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.decision_repo = DecisionRepository(db)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Karar Geçmişi (Audit Log)")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TURKCELL_BLUE};")
        
        header_layout.addWidget(title)
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
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Decisions table
        self.decisions_table = DataTable([
            "Karar ID", "Kullanıcı", "Tetiklenen Kurallar", "Seçilen Aksiyon", "Bastırılan", "Zaman"
        ])
        self.decisions_table.doubleClicked.connect(self.show_decision_detail)
        layout.addWidget(self.decisions_table)
        
        # Info text
        info = QLabel("💡 Detayları görmek için bir satıra çift tıklayın. 'Tüm Kullanıcıları İşle' butonuyla kural motorunu çalıştırabilirsiniz.")
        info.setStyleSheet("color: #8B8B8B; font-size: 12px;")
        layout.addWidget(info)
    
    def load_data(self):
        """Load decisions from database"""
        try:
            user_id = self.user_filter.currentData()
            
            if user_id:
                decisions = self.decision_repo.get_by_user(user_id)
            else:
                decisions = self.decision_repo.get_all(100)
            
            self.current_decisions = decisions  # Store for detail view
            
            self.decisions_table.setRowCount(len(decisions))
            
            for row_idx, decision in enumerate(decisions):
                # Decision ID
                self.decisions_table.setItem(row_idx, 0, 
                    QTableWidgetItem(decision.get('decision_id', '')))
                
                # User
                self.decisions_table.setItem(row_idx, 1, 
                    QTableWidgetItem(decision.get('user_name', decision.get('user_id', ''))))
                
                # Triggered rules
                triggered = decision.get('triggered_rules', [])
                if isinstance(triggered, list):
                    triggered = ', '.join(triggered)
                elif isinstance(triggered, str):
                    triggered = triggered.strip('{}').replace(',', ', ')
                self.decisions_table.setItem(row_idx, 2, QTableWidgetItem(triggered))
                
                # Selected action (colored)
                action = decision.get('selected_action', '')
                action_item = QTableWidgetItem(action)
                color = ACTION_COLORS.get(action, '#FFFFFF')
                action_item.setForeground(QColor(color))
                self.decisions_table.setItem(row_idx, 3, action_item)
                
                # Suppressed actions
                suppressed = decision.get('suppressed_actions', [])
                if isinstance(suppressed, list):
                    suppressed = ', '.join(filter(None, suppressed))
                elif isinstance(suppressed, str):
                    suppressed = suppressed.strip('{}').replace(',', ', ')
                else:
                    suppressed = ''
                self.decisions_table.setItem(row_idx, 4, QTableWidgetItem(suppressed or '-'))
                
                # Timestamp
                self.decisions_table.setItem(row_idx, 5, 
                    QTableWidgetItem(str(decision.get('timestamp', ''))[:19]))
                
        except Exception as e:
            print(f"Error loading decisions: {e}")
    
    def show_decision_detail(self, index):
        """Show decision detail dialog"""
        row = index.row()
        if row < len(self.current_decisions):
            dialog = DecisionDetailDialog(dict(self.current_decisions[row]), self)
            dialog.exec()
    
    def process_all_users(self):
        """Run rule engine for all users"""
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            results = rule_engine.process_all_users()
            
            if results:
                msg = f"{len(results)} kullanıcı için karar oluşturuldu:\n\n"
                for r in results[:5]:  # Show first 5
                    msg += f"• {r['decision']['user_id']}: {r['decision']['selected_action']}\n"
                if len(results) > 5:
                    msg += f"... ve {len(results) - 5} daha"
            else:
                msg = "Hiçbir kullanıcı için kural tetiklenmedi."
            
            QMessageBox.information(self, "Kural Motoru Sonucu", msg)
            self.load_data()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kural motoru çalıştırılırken hata: {e}")
