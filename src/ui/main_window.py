"""
Turkcell Decision Engine - Main Window
Ana uygulama penceresi
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QLabel, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .styles import (
    MAIN_STYLESHEET, TURKCELL_YELLOW, TURKCELL_BLUE, 
    TURKCELL_DARK, BG_WHITE, HEADER_STYLE
)
from .dashboard import DashboardPanel
from .events_panel import EventsPanel
from .rules_panel import RulesPanel
from .decisions_panel import DecisionsPanel
from .notifications_panel import NotificationsPanel
from ..config import app_config
from ..database import db


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(app_config.window_title)
        self.setMinimumSize(app_config.window_width, app_config.window_height)
        
        # Apply stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # Connect to database
        self.connect_database()
        
        # Setup main UI
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.setup_main_ui()
        
        # Setup status bar
        self.setup_statusbar()
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        if not db.connect():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Veritabanı Hatası",
                "PostgreSQL veritabanına bağlanılamadı.\nLütfen veritabanı ayarlarını kontrol edin."
            )
    
    def setup_main_ui(self):
        """Setup the main UI layout"""
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet(HEADER_STYLE)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Left side - Logo and title
        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)
        
        title = QLabel("Turkcell Decision Engine")
        title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {TURKCELL_YELLOW};
            background: transparent;
        """)
        left_layout.addWidget(title)
        
        subtitle = QLabel("Çok Servisli Davranış ve Karar Platformu")
        subtitle.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.7);
            font-size: 11px;
            background: transparent;
        """)
        left_layout.addWidget(subtitle)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Create all panels
        self.dashboard_tab = DashboardPanel()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        self.events_tab = EventsPanel()
        self.tabs.addTab(self.events_tab, "Events")
        
        self.decisions_tab = DecisionsPanel()
        self.tabs.addTab(self.decisions_tab, "Kararlar")
        
        self.notifications_tab = NotificationsPanel()
        self.tabs.addTab(self.notifications_tab, "Bildirimler")
        
        self.rules_tab = RulesPanel()
        self.tabs.addTab(self.rules_tab, "Kurallar")
        
        # Connect tab change to auto-refresh
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tabs)
    
    def on_tab_changed(self, index: int):
        """Auto-refresh panel when tab changes"""
        current_tab = self.tabs.widget(index)
        if hasattr(current_tab, 'load_data'):
            current_tab.load_data()
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_WHITE};
                color: #666;
                border-top: 1px solid #E0E0E0;
                padding: 8px;
            }}
        """)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Turkcell Decision Engine | Veritabanına bağlı")
    
    def closeEvent(self, event):
        """Handle window close"""
        db.disconnect()
        event.accept()


def run_app():
    """Run the application"""
    import sys
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
