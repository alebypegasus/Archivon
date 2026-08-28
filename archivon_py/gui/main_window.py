import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QLabel, QListWidgetItem, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from utils.icons import get_svg_icon
from utils.theme import get_current_theme_name, set_current_theme_name, get_theme_colors, generate_global_stylesheet
from core.download_manager import DownloadManager
from .downloads_tab import DownloadsTab
from .library_tab import LibraryTab
from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Archivon — Gestor de Acervos, Sanitizador & IA")
        self.resize(1180, 800)
        self.setMinimumSize(1000, 680)
        
        # Define o ícone da aplicação
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(__file__)))
        icon_candidates = [
            os.path.join(base_dir, "assets", "icon.png"),
            os.path.join(base_dir, "archivon_py", "assets", "icon.png"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        ]
        icon_path = next((p for p in icon_candidates if os.path.exists(p)), None)
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        self.current_theme = get_current_theme_name()
        
        # Instância compartilhada do núcleo de download
        self.download_manager = DownloadManager()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Container
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(240)
        self.sidebar_container.setObjectName("sidebarContainer")
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(14)
        
        # Logo & Brand Header with App Icon
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(12)

        self.logo_img = QLabel()
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_img.setPixmap(pix)
            self.logo_img.setFixedSize(38, 38)
            brand_layout.addWidget(self.logo_img)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        self.logo_label = QLabel("ARCHIVON")
        self.logo_label.setObjectName("brandLogo")
        self.logo_label.setStyleSheet("font-size: 18px; font-weight: 900; letter-spacing: 1.5px;")
        
        self.subtitle_label = QLabel("AI Sanitizer & Librarian")
        self.subtitle_label.setStyleSheet("font-size: 10.5px; font-weight: 600; opacity: 0.7;")
        
        title_vbox.addWidget(self.logo_label)
        title_vbox.addWidget(self.subtitle_label)
        brand_layout.addLayout(title_vbox)
        sidebar_layout.addLayout(brand_layout)
        
        # Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: rgba(148, 163, 184, 0.15); max-height: 1px;")
        sidebar_layout.addWidget(divider)

        # Navigation List
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setIconSize(QSize(20, 20))
        
        self.nav_items_data = [
            ("Downloads", "download", 0),
            ("Biblioteca", "library", 1),
            ("Configurações", "settings", 2)
        ]
        
        self._populate_sidebar_items()
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()
        
        # Theme Switcher Button
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedHeight(38)
        self.theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

        # Version tag
        self.version_label = QLabel("Versão 3.6.0 • Gemini 2.0")
        self.version_label.setStyleSheet("font-size: 11px; padding-left: 6px; opacity: 0.6;")
        sidebar_layout.addWidget(self.version_label)
        
        # Stacked Pages
        self.pages = QStackedWidget()
        self.pages.setObjectName("pagesContainer")
        
        self.downloads_tab = DownloadsTab(download_manager=self.download_manager)
        self.library_tab = LibraryTab(download_manager=self.download_manager)
        self.settings_tab = SettingsTab()
        
        self.pages.addWidget(self.downloads_tab)
        self.pages.addWidget(self.library_tab)
        self.pages.addWidget(self.settings_tab)
        
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        
        main_layout.addWidget(self.sidebar_container)
        main_layout.addWidget(self.pages)

        self._apply_theme()

    def _populate_sidebar_items(self):
        self.sidebar.clear()
        colors = get_theme_colors(self.current_theme)
        icon_color = colors["text_secondary"]
        for text, icon_name, idx in self.nav_items_data:
            item = QListWidgetItem(get_svg_icon(icon_name, icon_color, 20), f"  {text}")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.sidebar.addItem(item)

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.current_theme = new_theme
        set_current_theme_name(new_theme)
        self._apply_theme()

    def _apply_theme(self):
        t = get_theme_colors(self.current_theme)
        
        # Update theme button icon and text
        if self.current_theme == "dark":
            self.theme_btn.setText("  Modo Claro")
            self.theme_btn.setIcon(get_svg_icon("sun", "#F59E0B", 18))
            self.theme_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    color: #F8FAFC;
                    text-align: left;
                    padding-left: 14px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #334155;
                }
            """)
        else:
            self.theme_btn.setText("  Modo Escuro")
            self.theme_btn.setIcon(get_svg_icon("moon", "#6366F1", 18))
            self.theme_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    border: 1px solid #E2E8F0;
                    color: #0F172A;
                    text-align: left;
                    padding-left: 14px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
            """)

        self.logo_label.setStyleSheet(f"font-size: 18px; font-weight: 900; letter-spacing: 1.5px; color: {t['accent']};")
        self.subtitle_label.setStyleSheet(f"font-size: 10.5px; font-weight: 600; color: {t['text_secondary']};")
        self.version_label.setStyleSheet(f"font-size: 11px; padding-left: 6px; color: {t['text_muted']};")

        # Global stylesheet
        qss = f"""
            QMainWindow {{
                background-color: {t['bg_primary']};
            }}
            QWidget#sidebarContainer {{
                background-color: {t['sidebar_bg']};
                border-right: 1px solid {t['border']};
            }}
            QListWidget#sidebar {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget#sidebar::item {{
                height: 44px;
                padding-left: 12px;
                margin-bottom: 6px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                color: {t['text_secondary']};
            }}
            QListWidget#sidebar::item:hover {{
                background-color: {t['sidebar_btn_hover']};
                color: {t['text_primary']};
            }}
            QListWidget#sidebar::item:selected {{
                background-color: {t['accent']};
                color: #FFFFFF;
            }}
            QStackedWidget#pagesContainer {{
                background-color: {t['bg_primary']};
            }}
            {generate_global_stylesheet(self.current_theme)}
        """
        self.setStyleSheet(qss)
        self._populate_sidebar_items()
