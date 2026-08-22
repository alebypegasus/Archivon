import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox, QComboBox, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
from utils.config import load_config, save_config
from utils.icons import get_svg_icon

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Header
        title_box = QVBoxLayout()
        title = QLabel("Configurações do Sistema")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC;")
        subtitle = QLabel("Gerencie credenciais de IA, caminhos de armazenamento, LibreOffice e otimizações.")
        subtitle.setStyleSheet("font-size: 12.5px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Settings Card
        settings_card = QFrame()
        settings_card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        form_layout = QFormLayout(settings_card)
        form_layout.setSpacing(16)

        # Load Config
        self.config_data = load_config()

        # Gemini API Key Field
        key_layout = QHBoxLayout()
        self.gemini_api_key = QLineEdit(self.config_data.get("gemini_api_key", ""))
        self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key.setFixedHeight(38)
        key_layout.addWidget(self.gemini_api_key)

        self.toggle_key_btn = QPushButton("Exibir")
        self.toggle_key_btn.setFixedHeight(38)
        self.toggle_key_btn.setStyleSheet("background-color: #334155; color: #F8FAFC; padding: 0 12px;")
        self.toggle_key_btn.clicked.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.toggle_key_btn)

        self.test_api_btn = QPushButton("Testar Conexão")
        self.test_api_btn.setIcon(get_svg_icon("cpu", "#FFFFFF", 16))
        self.test_api_btn.setFixedHeight(38)
        self.test_api_btn.setStyleSheet("background-color: #0284C7; color: #FFFFFF; font-weight: 600;")
        self.test_api_btn.clicked.connect(self.test_gemini_api)
        key_layout.addWidget(self.test_api_btn)

        form_layout.addRow(QLabel("Google Gemini API Key:"), key_layout)

        # Gemini Model Selector
        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(38)
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 12px;
                color: #F8FAFC;
                font-weight: 600;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                selection-background-color: #4F46E5;
                color: #F8FAFC;
            }
        """)
        
        default_models = [
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        self.model_combo.addItems(default_models)
        saved_model = self.config_data.get("gemini_model", "gemini-2.0-flash-lite")
        idx = self.model_combo.findText(saved_model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.insertItem(0, saved_model)
            self.model_combo.setCurrentIndex(0)

        form_layout.addRow(QLabel("Modelo Gemini Ativo:"), self.model_combo)

        # LibreOffice Path / Status
        soffice_layout = QVBoxLayout()
        soffice_layout.setSpacing(4)
        
        soffice_row = QHBoxLayout()
        self.soffice_path_edit = QLineEdit(self.config_data.get("soffice_path", ""))
        self.soffice_path_edit.setPlaceholderText("Automático (detectado no sistema ou pasta local)")
        self.soffice_path_edit.setFixedHeight(38)
        soffice_row.addWidget(self.soffice_path_edit)

        btn_soffice = QPushButton("Procurar...")
        btn_soffice.setFixedHeight(38)
        btn_soffice.setStyleSheet("background-color: #334155; color: #F8FAFC;")
        btn_soffice.clicked.connect(self.select_soffice_binary)
        soffice_row.addWidget(btn_soffice)

        self.soffice_status_label = QLabel()
        self._update_soffice_status()

        soffice_layout.addLayout(soffice_row)
        soffice_layout.addWidget(self.soffice_status_label)
        form_layout.addRow(QLabel("Motor LibreOffice (soffice):"), soffice_layout)

        # Cookies File Selector
        self.cookies_file = QLineEdit(self.config_data.get("cookies_file", ""))
        self.cookies_file.setReadOnly(True)
        self.cookies_file.setPlaceholderText("Opcional: selecione o arquivo cookies.txt para pastas privadas")
        self.cookies_file.setFixedHeight(38)
        
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(self.cookies_file)
        btn_cookies = QPushButton("Selecionar...")
        btn_cookies.setFixedHeight(38)
        btn_cookies.setStyleSheet("background-color: #334155; color: #F8FAFC;")
        btn_cookies.clicked.connect(self.select_cookies_file)
        cookies_layout.addWidget(btn_cookies)
        form_layout.addRow(QLabel("Cookies Google Drive (cookies.txt):"), cookies_layout)

        # Temp Folder Selector
        self.temp_folder = QLineEdit(self.config_data.get("temp_folder", "temp"))
        self.temp_folder.setReadOnly(True)
        self.temp_folder.setFixedHeight(38)
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temp_folder)
        btn_temp = QPushButton("Navegar...")
        btn_temp.setFixedHeight(38)
        btn_temp.setStyleSheet("background-color: #334155; color: #F8FAFC;")
        btn_temp.clicked.connect(lambda: self.select_folder(self.temp_folder))
        temp_layout.addWidget(btn_temp)
        form_layout.addRow(QLabel("Pasta Temporária:"), temp_layout)

        # Output Folder Selector
        self.output_folder = QLineEdit(self.config_data.get("output_folder", "Biblioteca"))
        self.output_folder.setReadOnly(True)
        self.output_folder.setFixedHeight(38)
        
        out_layout = QHBoxLayout()
        out_layout.addWidget(self.output_folder)
        btn_out = QPushButton("Navegar...")
        btn_out.setFixedHeight(38)
        btn_out.setStyleSheet("background-color: #334155; color: #F8FAFC;")
        btn_out.clicked.connect(lambda: self.select_folder(self.output_folder))
        out_layout.addWidget(btn_out)
        form_layout.addRow(QLabel("Pasta da Biblioteca:"), out_layout)

        # Compression Checkbox
        self.compress_check = QCheckBox("Comprimir e otimizar imagens/fontes dos PDFs durante a higienização")
        self.compress_check.setChecked(self.config_data.get("compress_pdf", True))
        self.compress_check.setStyleSheet("font-size: 13px; color: #F1F5F9;")
        form_layout.addRow(QLabel("Otimização de PDF:"), self.compress_check)

        layout.addWidget(settings_card)

        # Save Button
        self.save_btn = QPushButton("Salvar Configurações")
        self.save_btn.setIcon(get_svg_icon("check", "#FFFFFF", 16))
        self.save_btn.setFixedHeight(42)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                font-weight: 700;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def _update_soffice_status(self):
        from core.download_manager import DownloadManager
        dm = DownloadManager()
        detected = dm._get_soffice_binary(self.config_data)
        if detected:
            self.soffice_status_label.setText(f"Status: Conectado ({detected})")
            self.soffice_status_label.setStyleSheet("font-size: 11.5px; color: #34D399; font-weight: 600;")
        else:
            self.soffice_status_label.setText("Status: Não detectado (necessário para converter PPTX/DOCX)")
            self.soffice_status_label.setStyleSheet("font-size: 11.5px; color: #F87171; font-weight: 600;")

    def select_soffice_binary(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o executável soffice", "", "Executáveis (soffice soffice.exe *);;Todos os Arquivos (*)")
        if file_path:
            self.soffice_path_edit.setText(file_path)
            self.config_data["soffice_path"] = file_path
            self._update_soffice_status()

    def toggle_key_visibility(self):
        if self.gemini_api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("Ocultar")
        else:
            self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("Exibir")

    def test_gemini_api(self):
        key = self.gemini_api_key.text().strip()
        if not key:
            QMessageBox.warning(self, "Aviso", "Insira uma chave de API antes de testar.")
            return

        from core.ai_categorizer import AICategorizer
        categorizer = AICategorizer(api_key=key)
        success, message, models = categorizer.test_connection()

        if success:
            if models:
                self.model_combo.clear()
                self.model_combo.addItems(models)
            QMessageBox.information(self, "Conexão Estabelecida", f"{message}\n\nModelos atualizados no menu.")
        else:
            QMessageBox.critical(self, "Erro de Conexão", message)

    def select_cookies_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo cookies.txt", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.cookies_file.setText(file_path)

    def select_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Selecione o Diretório")
        if folder:
            line_edit.setText(folder)

    def save_settings(self):
        self.config_data["gemini_api_key"] = self.gemini_api_key.text().strip()
        self.config_data["gemini_model"] = self.model_combo.currentText().strip()
        self.config_data["soffice_path"] = self.soffice_path_edit.text().strip()
        self.config_data["cookies_file"] = self.cookies_file.text().strip()
        self.config_data["temp_folder"] = self.temp_folder.text().strip()
        self.config_data["output_folder"] = self.output_folder.text().strip()
        self.config_data["compress_pdf"] = self.compress_check.isChecked()

        if save_config(self.config_data):
            self._update_soffice_status()
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Houve um problema ao salvar as configurações.")
