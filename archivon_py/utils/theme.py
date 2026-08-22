import os
from utils.config import load_config, save_config

THEMES = {
    "dark": {
        "bg_primary": "#0B0F19",
        "bg_secondary": "#151D2E",
        "bg_surface": "#1E293B",
        "bg_input": "#0F172A",
        "border": "#334155",
        "border_focus": "#6366F1",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#6366F1",
        "accent_hover": "#4F46E5",
        "accent_light": "#818CF8",
        "sidebar_bg": "#0B1120",
        "sidebar_btn_hover": "#1E293B",
        "sidebar_btn_active": "#312E81",
        "card_bg": "#1E293B",
        "card_border": "#334155",
        "table_header": "#0F172A",
        "table_row_alt": "#162032"
    },
    "light": {
        "bg_primary": "#F8FAFC",
        "bg_secondary": "#F1F5F9",
        "bg_surface": "#FFFFFF",
        "bg_input": "#FFFFFF",
        "border": "#E2E8F0",
        "border_focus": "#4F46E5",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "accent": "#4F46E5",
        "accent_hover": "#4338CA",
        "accent_light": "#6366F1",
        "sidebar_bg": "#FFFFFF",
        "sidebar_btn_hover": "#F1F5F9",
        "sidebar_btn_active": "#EEF2FF",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "table_header": "#F1F5F9",
        "table_row_alt": "#F8FAFC"
    }
}

def get_current_theme_name() -> str:
    config = load_config()
    return config.get("theme", "dark")

def set_current_theme_name(theme_name: str):
    config = load_config()
    config["theme"] = theme_name
    save_config(config)

def get_theme_colors(theme_name: str = None) -> dict:
    if not theme_name:
        theme_name = get_current_theme_name()
    return THEMES.get(theme_name, THEMES["dark"])

def generate_global_stylesheet(theme_name: str = None) -> str:
    t = get_theme_colors(theme_name)
    return f"""
        QMainWindow, QWidget {{
            background-color: {t['bg_primary']};
            color: {t['text_primary']};
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
        }}
        QLabel {{
            color: {t['text_primary']};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {t['bg_input']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: {t['accent']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {t['border_focus']};
            background-color: {t['bg_surface']};
        }}
        QPushButton {{
            background-color: {t['accent']};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {t['accent_hover']};
        }}
        QPushButton:disabled {{
            background-color: {t['border']};
            color: {t['text_muted']};
        }}
        QProgressBar {{
            background-color: {t['bg_input']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            text-align: center;
            color: {t['text_primary']};
            font-weight: 600;
            font-size: 11px;
            height: 12px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #38BDF8);
            border-radius: 5px;
        }}
        QScrollBar:vertical {{
            background: {t['bg_primary']};
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {t['border']};
            min-height: 24px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['text_muted']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """
