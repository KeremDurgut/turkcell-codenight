"""
Turkcell Decision Engine - Login Screen
Giriş ekranı - RBAC sistemi için kimlik doğrulama
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from .styles import (
    LOGIN_STYLESHEET, TURKCELL_YELLOW, TURKCELL_BLUE, 
    TURKCELL_DARK, BG_WHITE, COLOR_CRITICAL
)
from ..auth import auth_manager


class LoginScreen(QWidget):
    """Login screen for authentication"""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loginWidget")
        self.setStyleSheet(LOGIN_STYLESHEET)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center container
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        
        # Login card
        login_card = QFrame()
        login_card.setFixedSize(420, 520)
        login_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_WHITE};
                border-radius: 16px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        login_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        # Logo / Title area
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("font-size: 48px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo_label)
        
        title_label = QLabel("Turkcell Decision Engine")
        title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {TURKCELL_DARK};
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Karar Destek Platformu")
        subtitle_label.setStyleSheet(f"""
            font-size: 13px;
            color: #888888;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle_label)
        
        card_layout.addSpacing(20)
        
        # Username field
        username_label = QLabel("Kullanıcı Adı")
        username_label.setObjectName("formLabel")
        username_label.setStyleSheet(f"color: {TURKCELL_DARK}; font-weight: 600;")
        card_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setObjectName("loginInput")
        self.username_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.username_input.setMinimumHeight(50)
        card_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Şifre")
        password_label.setObjectName("formLabel")
        password_label.setStyleSheet(f"color: {TURKCELL_DARK}; font-weight: 600;")
        card_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.password_input)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setStyleSheet(f"color: {COLOR_CRITICAL}; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)
        
        card_layout.addSpacing(10)
        
        # Login button
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setObjectName("loginButton")
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)
        
        card_layout.addStretch()
        
        # Footer
        footer_label = QLabel("Code Night 2026 • Turkcell")
        footer_label.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(footer_label)
        
        center_layout.addWidget(login_card)
        center_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            self.show_error("Kullanıcı adı boş olamaz")
            return
        
        if not password:
            self.show_error("Şifre boş olamaz")
            return
        
        # Attempt login
        success, message = auth_manager.login(username, password)
        
        if success:
            self.error_label.hide()
            self.login_successful.emit()
        else:
            self.show_error(message)
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.show()
    
    def clear_inputs(self):
        """Clear all input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
