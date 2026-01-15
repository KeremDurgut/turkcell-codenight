"""
Turkcell Decision Engine - PyQt6 Styles
Turkcell resmi renk paleti ile modern arayüz tasarımı
"""

# ============================================================
# 1. ANA MARKA RENKLERİ (Primary Brand Colors)
# ============================================================

TURKCELL_YELLOW = "#FFC900"      # Butonlar, CTA, Vurgular
TURKCELL_BLUE = "#2855AC"        # Header, Başlıklar, Linkler
TURKCELL_DARK = "#0A1E43"        # Sidebar, Koyu Alanlar

# ============================================================
# 2. ARAYÜZ VE ZEMİN RENKLERİ (UI & Backgrounds)
# ============================================================

BG_WHITE = "#FFFFFF"             # Kartlar, Tablolar
BG_GRAY = "#F4F6F8"              # Ana arka plan
BORDER_GRAY = "#E0E0E0"          # Çizgiler, Border
TEXT_PRIMARY = "#333333"         # Ana metinler
TEXT_SECONDARY = "#666666"       # Alt başlıklar, Timestamp

# ============================================================
# 3. ALARM RENKLERİ (Semantic Colors)
# ============================================================

COLOR_CRITICAL = "#D32F2F"       # Kritik, Yüksek Risk (Kırmızı)
COLOR_WARNING = "#F57C00"        # Uyarı, Orta Seviye (Turuncu)
COLOR_SUCCESS = "#388E3C"        # Güvenli, Normal (Yeşil)
COLOR_INFO = "#1976D2"           # Bilgilendirme (Mavi)

# Risk Level Colors
RISK_COLORS = {
    'CRITICAL': COLOR_CRITICAL,
    'HIGH': COLOR_CRITICAL,
    'MEDIUM': COLOR_WARNING,
    'LOW': COLOR_SUCCESS
}

# Action Type Colors
ACTION_COLORS = {
    'CRITICAL_ALERT': COLOR_CRITICAL,
    'SPEND_ALERT': COLOR_WARNING,
    'DATA_USAGE_WARNING': COLOR_WARNING,
    'CONTENT_COOLDOWN_SUGGESTION': COLOR_INFO,
    'DATA_USAGE_NUDGE': COLOR_INFO,
    'SPEND_NUDGE': COLOR_SUCCESS
}

# ============================================================
# MAIN STYLESHEET - Light Theme
# ============================================================

MAIN_STYLESHEET = f"""
/* ===== Global Styles ===== */
QMainWindow, QWidget {{
    background-color: {BG_GRAY};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    font-size: 13px;
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    border: 1px solid {BORDER_GRAY};
    background-color: {BG_WHITE};
    border-radius: 8px;
    padding: 5px;
}}

QTabBar::tab {{
    background-color: {BG_WHITE};
    color: {TEXT_SECONDARY};
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid {BORDER_GRAY};
    border-bottom: none;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
    font-weight: 600;
    border-color: {TURKCELL_YELLOW};
}}

QTabBar::tab:hover:!selected {{
    background-color: #E8E8E8;
}}

/* ===== Tables ===== */
QTableWidget, QTableView {{
    background-color: {BG_WHITE};
    alternate-background-color: #FAFAFA;
    border: 1px solid {BORDER_GRAY};
    border-radius: 8px;
    gridline-color: {BORDER_GRAY};
    selection-background-color: {TURKCELL_YELLOW};
    selection-color: {TURKCELL_DARK};
}}

QTableWidget::item, QTableView::item {{
    padding: 10px;
    border-bottom: 1px solid {BORDER_GRAY};
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
}}

QHeaderView::section {{
    background-color: {TURKCELL_BLUE};
    color: white;
    padding: 12px 8px;
    border: none;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 8px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 8px;
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {TURKCELL_BLUE};
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-weight: 500;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: #1E4A9A;
}}

QPushButton:pressed {{
    background-color: {TURKCELL_DARK};
}}

QPushButton:disabled {{
    background-color: #CCCCCC;
    color: #888888;
}}

QPushButton#primaryButton {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background-color: #E6B800;
}}

QPushButton#dangerButton {{
    background-color: {COLOR_CRITICAL};
    color: white;
}}

QPushButton#dangerButton:hover {{
    background-color: #B71C1C;
}}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG_WHITE};
    color: {TEXT_PRIMARY};
    border: 2px solid {BORDER_GRAY};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {TURKCELL_BLUE};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid {TURKCELL_BLUE};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_WHITE};
    border: 1px solid {BORDER_GRAY};
    selection-background-color: {TURKCELL_YELLOW};
    selection-color: {TURKCELL_DARK};
}}

/* ===== Labels ===== */
QLabel {{
    color: {TEXT_PRIMARY};
}}

QLabel#headerLabel {{
    font-size: 24px;
    font-weight: 700;
    color: {TURKCELL_BLUE};
    padding: 10px 0;
}}

QLabel#subHeaderLabel {{
    font-size: 16px;
    font-weight: 500;
    color: {TEXT_SECONDARY};
}}

QLabel#statValue {{
    font-size: 32px;
    font-weight: 700;
    color: {TURKCELL_BLUE};
}}

QLabel#statLabel {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ===== Scroll Bars ===== */
QScrollBar:vertical {{
    background-color: {BG_GRAY};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: #CCCCCC;
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TURKCELL_BLUE};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {BG_GRAY};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: #CCCCCC;
    border-radius: 6px;
    min-width: 30px;
}}

/* ===== Group Box ===== */
QGroupBox {{
    border: 2px solid {BORDER_GRAY};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    background-color: {BG_WHITE};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {TURKCELL_BLUE};
}}

/* ===== Check Box ===== */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {BORDER_GRAY};
    background-color: {BG_WHITE};
}}

QCheckBox::indicator:checked {{
    background-color: {TURKCELL_YELLOW};
    border-color: {TURKCELL_YELLOW};
}}

/* ===== Tooltips ===== */
QToolTip {{
    background-color: {TURKCELL_DARK};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {BG_WHITE};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {BORDER_GRAY};
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    border: none;
    border-radius: 8px;
    background-color: {BORDER_GRAY};
    text-align: center;
    color: {TEXT_PRIMARY};
}}

QProgressBar::chunk {{
    background-color: {TURKCELL_YELLOW};
    border-radius: 8px;
}}

/* ===== Message Box ===== */
QMessageBox {{
    background-color: {BG_WHITE};
}}

/* ===== Dialog ===== */
QDialog {{
    background-color: {BG_WHITE};
}}
"""

# ============================================================
# LOGIN SCREEN STYLESHEET
# ============================================================

LOGIN_STYLESHEET = f"""
QWidget#loginWidget {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
        stop:0 {TURKCELL_DARK}, stop:1 {TURKCELL_BLUE});
}}

QLabel#titleLabel {{
    font-size: 28px;
    font-weight: 700;
    color: white;
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
}}

QLabel#formLabel {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
    font-weight: 500;
}}

QLineEdit#loginInput {{
    background-color: {BG_WHITE};
    border: 2px solid {BORDER_GRAY};
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QLineEdit#loginInput:focus {{
    border-color: {TURKCELL_YELLOW};
}}

QPushButton#loginButton {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
    border: none;
    border-radius: 8px;
    padding: 14px 32px;
    font-size: 16px;
    font-weight: 600;
}}

QPushButton#loginButton:hover {{
    background-color: #E6B800;
}}

QPushButton#loginButton:pressed {{
    background-color: #CCa300;
}}

QLabel#errorLabel {{
    color: {COLOR_CRITICAL};
    font-size: 12px;
    font-weight: 500;
}}
"""

# ============================================================
# CARD STYLES
# ============================================================

CARD_STYLE = f"""
    background-color: {BG_WHITE};
    border: 1px solid {BORDER_GRAY};
    border-radius: 12px;
    padding: 20px;
"""

STAT_CARD_STYLE = f"""
    background-color: {BG_WHITE};
    border: 1px solid {BORDER_GRAY};
    border-radius: 16px;
    padding: 24px;
"""

# ============================================================
# HEADER STYLE
# ============================================================

HEADER_STYLE = f"""
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 {TURKCELL_DARK}, stop:1 {TURKCELL_BLUE});
    padding: 15px 20px;
"""
