"""
Turkcell Decision Engine - Main Window
Main application window with tab-based navigation
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QLabel, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

from .styles import MAIN_STYLESHEET, TURKCELL_YELLOW
from .dashboard import DashboardPanel
from .events_panel import EventsPanel
from .rules_panel import RulesPanel
from .decisions_panel import DecisionsPanel
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
        
        # Setup UI
        self.setup_ui()
        self.setup_statusbar()
        
        # Connect to database
        self.connect_database()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #0F3460, stop:1 #1A1A2E);
            padding: 15px;
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel("🚀 Turkcell Decision Engine")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {TURKCELL_YELLOW};
        """)
        
        subtitle = QLabel("Çok Servisli Davranış ve Karar Platformu • Code Night 2026")
        subtitle.setStyleSheet("color: #8B8B8B; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Add tabs
        self.dashboard_tab = DashboardPanel()
        self.events_tab = EventsPanel()
        self.decisions_tab = DecisionsPanel()
        self.rules_tab = RulesPanel()
        
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tabs.addTab(self.events_tab, "📨 Events")
        self.tabs.addTab(self.decisions_tab, "📋 Kararlar")
        self.tabs.addTab(self.rules_tab, "⚙️ Kurallar")
        
        layout.addWidget(self.tabs)
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Database status
        self.db_status = QLabel("🔴 Veritabanı: Bağlantı yok")
        self.statusbar.addPermanentWidget(self.db_status)
        
        # Connection refresh timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_db_status)
        self.status_timer.start(5000)
    
    def connect_database(self):
        """Connect to database"""
        if db.connect():
            self.db_status.setText("🟢 Veritabanı: Bağlı")
            self.statusbar.showMessage("Veritabanına başarıyla bağlanıldı", 3000)
        else:
            self.db_status.setText("🔴 Veritabanı: Bağlantı hatası")
            QMessageBox.warning(
                self, 
                "Veritabanı Hatası",
                "PostgreSQL veritabanına bağlanılamadı.\n\n"
                "Lütfen şunları kontrol edin:\n"
                "1. PostgreSQL servisi çalışıyor mu?\n"
                "2. .env dosyasındaki bağlantı bilgileri doğru mu?\n"
                "3. Veritabanı oluşturulmuş mu?"
            )
    
    def update_db_status(self):
        """Update database status indicator"""
        if db.is_connected:
            self.db_status.setText("🟢 Veritabanı: Bağlı")
        else:
            self.db_status.setText("🔴 Veritabanı: Bağlantı yok")
    
    def closeEvent(self, event):
        """Handle window close"""
        db.disconnect()
        event.accept()


def run_app():
    """Run the application"""
    import sys
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Turkcell Decision Engine")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Turkcell")
    
    # Set font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
