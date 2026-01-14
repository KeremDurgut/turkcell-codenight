"""
Turkcell Decision Engine - PyQt6 Styles
Modern, premium dark theme inspired by Turkcell brand
"""

# Turkcell Brand Colors
TURKCELL_YELLOW = "#FFD100"
TURKCELL_DARK = "#1A1A2E"
TURKCELL_DARKER = "#16213E"
TURKCELL_ACCENT = "#0F3460"
TURKCELL_TEXT = "#EAEAEA"
TURKCELL_TEXT_DIM = "#8B8B8B"

# Risk Level Colors
RISK_COLORS = {
    'CRITICAL': '#FF4757',
    'HIGH': '#FFA502',
    'MEDIUM': '#FFD100',
    'LOW': '#2ED573'
}

# Action Type Colors
ACTION_COLORS = {
    'CRITICAL_ALERT': '#FF4757',
    'SPEND_ALERT': '#FFA502',
    'DATA_USAGE_WARNING': '#FF6B81',
    'CONTENT_COOLDOWN_SUGGESTION': '#5352ED',
    'DATA_USAGE_NUDGE': '#70A1FF',
    'SPEND_NUDGE': '#7BED9F'
}

# Main Application Stylesheet
MAIN_STYLESHEET = f"""
/* ===== Global Styles ===== */
QMainWindow, QWidget {{
    background-color: {TURKCELL_DARK};
    color: {TURKCELL_TEXT};
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    border: 1px solid {TURKCELL_ACCENT};
    background-color: {TURKCELL_DARKER};
    border-radius: 8px;
    padding: 5px;
}}

QTabBar::tab {{
    background-color: {TURKCELL_ACCENT};
    color: {TURKCELL_TEXT};
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: #1F4068;
}}

/* ===== Tables ===== */
QTableWidget, QTableView {{
    background-color: {TURKCELL_DARKER};
    alternate-background-color: #1E2746;
    border: 1px solid {TURKCELL_ACCENT};
    border-radius: 8px;
    gridline-color: #2A3F5F;
    selection-background-color: {TURKCELL_YELLOW};
    selection-color: {TURKCELL_DARK};
}}

QTableWidget::item, QTableView::item {{
    padding: 8px;
    border-bottom: 1px solid #2A3F5F;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
}}

QHeaderView::section {{
    background-color: {TURKCELL_ACCENT};
    color: {TURKCELL_YELLOW};
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
    background-color: {TURKCELL_ACCENT};
    color: {TURKCELL_TEXT};
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-weight: 500;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: #1F4068;
}}

QPushButton:pressed {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
}}

QPushButton#primaryButton {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background-color: #E6BC00;
}}

QPushButton#dangerButton {{
    background-color: #FF4757;
    color: white;
}}

QPushButton#dangerButton:hover {{
    background-color: #FF6B81;
}}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    background-color: {TURKCELL_DARKER};
    color: {TURKCELL_TEXT};
    border: 2px solid {TURKCELL_ACCENT};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {TURKCELL_YELLOW};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid {TURKCELL_YELLOW};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {TURKCELL_DARKER};
    border: 1px solid {TURKCELL_ACCENT};
    selection-background-color: {TURKCELL_YELLOW};
    selection-color: {TURKCELL_DARK};
}}

/* ===== Labels ===== */
QLabel {{
    color: {TURKCELL_TEXT};
}}

QLabel#headerLabel {{
    font-size: 24px;
    font-weight: 700;
    color: {TURKCELL_YELLOW};
    padding: 10px 0;
}}

QLabel#subHeaderLabel {{
    font-size: 16px;
    font-weight: 500;
    color: {TURKCELL_TEXT_DIM};
}}

QLabel#statValue {{
    font-size: 32px;
    font-weight: 700;
    color: {TURKCELL_YELLOW};
}}

QLabel#statLabel {{
    font-size: 12px;
    color: {TURKCELL_TEXT_DIM};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ===== Scroll Bars ===== */
QScrollBar:vertical {{
    background-color: {TURKCELL_DARKER};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {TURKCELL_ACCENT};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TURKCELL_YELLOW};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {TURKCELL_DARKER};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {TURKCELL_ACCENT};
    border-radius: 6px;
    min-width: 30px;
}}

/* ===== Group Box ===== */
QGroupBox {{
    border: 2px solid {TURKCELL_ACCENT};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {TURKCELL_YELLOW};
}}

/* ===== Check Box ===== */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {TURKCELL_ACCENT};
}}

QCheckBox::indicator:checked {{
    background-color: {TURKCELL_YELLOW};
    border-color: {TURKCELL_YELLOW};
}}

/* ===== Tooltips ===== */
QToolTip {{
    background-color: {TURKCELL_DARKER};
    color: {TURKCELL_TEXT};
    border: 1px solid {TURKCELL_YELLOW};
    border-radius: 4px;
    padding: 8px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {TURKCELL_DARKER};
    color: {TURKCELL_TEXT_DIM};
    border-top: 1px solid {TURKCELL_ACCENT};
}}

/* ===== Menu Bar ===== */
QMenuBar {{
    background-color: {TURKCELL_DARKER};
    color: {TURKCELL_TEXT};
    border-bottom: 1px solid {TURKCELL_ACCENT};
}}

QMenuBar::item:selected {{
    background-color: {TURKCELL_ACCENT};
}}

QMenu {{
    background-color: {TURKCELL_DARKER};
    border: 1px solid {TURKCELL_ACCENT};
}}

QMenu::item:selected {{
    background-color: {TURKCELL_YELLOW};
    color: {TURKCELL_DARK};
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    border: none;
    border-radius: 8px;
    background-color: {TURKCELL_ACCENT};
    text-align: center;
    color: {TURKCELL_TEXT};
}}

QProgressBar::chunk {{
    background-color: {TURKCELL_YELLOW};
    border-radius: 8px;
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {TURKCELL_ACCENT};
}}

QSplitter::handle:hover {{
    background-color: {TURKCELL_YELLOW};
}}
"""

# Card Widget Style
CARD_STYLE = f"""
    background-color: {TURKCELL_DARKER};
    border: 1px solid {TURKCELL_ACCENT};
    border-radius: 12px;
    padding: 20px;
"""

# Stat Card Style
STAT_CARD_STYLE = f"""
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
        stop:0 {TURKCELL_ACCENT}, stop:1 {TURKCELL_DARKER});
    border: none;
    border-radius: 16px;
    padding: 24px;
"""
