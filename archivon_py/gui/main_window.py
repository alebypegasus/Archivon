from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QLabel, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from utils.icons import get_svg_icon
from core.download_manager import DownloadManager
from .downloads_tab import DownloadsTab
from .library_tab import LibraryTab
from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Archivon — Gestor de Acervos & Sanitizador")
        self.resize(1140, 780)
        self.setMinimumSize(980, 660)
        
        self._apply_global_styles()

        # Instância compartilhada do núcleo de download
        self.download_manager = DownloadManager()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Container
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(230)
        sidebar_container.setObjectName("sidebarContainer")
        
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(14, 24, 14, 24)
        sidebar_layout.setSpacing(12)
        
        # Logo / Brand Header
        brand_widget = QWidget()
        brand_layout = QVBoxLayout(brand_widget)
        brand_layout.setContentsMargins(8, 0, 8, 12)
        brand_layout.setSpacing(4)
        
        logo_label = QLabel("ARCHIVON")
        logo_label.setObjectName("brandLogo")
        logo_label.setStyleSheet("font-size: 19px; font-weight: 900; color: #6366F1; letter-spacing: 2px;")
        
        subtitle_label = QLabel("Sanitizer & AI Librarian")
        subtitle_label.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600;")
        
        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(subtitle_label)
        sidebar_layout.addWidget(brand_widget)
        
        # Sidebar Navigation List
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setIconSize(QSize(18, 18))
        
        nav_items = [
            ("Downloads", "download", 0),
            ("Biblioteca", "library", 1),
            ("Configurações", "settings", 2)
        ]
        
        for text, icon_name, idx in nav_items:
            item = QListWidgetItem(get_svg_icon(icon_name, "#94A3B8", 18), f"  {text}")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.sidebar.addItem(item)
            
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()
        
        # Version tag
        version_label = QLabel("Versão 2.5 • Gemini 2.0")
        version_label.setStyleSheet("font-size: 11px; color: #475569; padding-left: 8px;")
        sidebar_layout.addWidget(version_label)
        
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
        
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.pages)

    def _apply_global_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
            }
            QWidget {
                color: #F8FAFC;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }
            QWidget#sidebarContainer {
                background-color: #1E293B;
                border-right: 1px solid #334155;
            }
            QListWidget#sidebar {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget#sidebar::item {
                height: 42px;
                padding-left: 10px;
                margin-bottom: 4px;
                border-radius: 6px;
                font-size: 13.5px;
                font-weight: 600;
                color: #94A3B8;
            }
            QListWidget#sidebar::item:hover {
                background-color: #334155;
                color: #F1F5F9;
            }
            QListWidget#sidebar::item:selected {
                background-color: #4F46E5;
                color: #FFFFFF;
            }
            QStackedWidget#pagesContainer {
                background-color: #0F172A;
            }
            QPushButton {
                background-color: #4F46E5;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12.5px;
            }
            QPushButton:hover {
                background-color: #6366F1;
            }
            QPushButton:pressed {
                background-color: #4338CA;
            }
            QLineEdit, QTextEdit, QTextBrowser {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #F8FAFC;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: #6366F1;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #6366F1;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E293B;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #475569;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
