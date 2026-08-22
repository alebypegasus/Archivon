import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QComboBox, QLineEdit, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont
from utils.icons import get_svg_icon

class DropTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAcceptRichText(False)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() or e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            urls = []
            for url in e.mimeData().urls():
                if url.isLocalFile():
                    urls.append(url.toLocalFile())
                else:
                    urls.append(url.toString())
            self.insertPlainText("\n".join(urls) + "\n")
        elif e.mimeData().hasText():
            self.insertPlainText(e.mimeData().text() + "\n")

class MetricCard(QFrame):
    def __init__(self, title: str, value: str, accent_color: str, icon_name: str):
        super().__init__()
        self.setObjectName("metricCard")
        self.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 10px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setPixmap(get_svg_icon(icon_name, accent_color, 24).pixmap(24, 24))
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;")

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {accent_color};")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)
        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, val):
        self.value_label.setText(str(val))

class DownloadsTab(QWidget):
    def __init__(self, download_manager=None):
        super().__init__()
        self.raw_logs = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Painel de Controle e Processamento")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC;")
        subtitle = QLabel("Esteira automatizada de download, sanitização profunda e classificação com Gemini.")
        subtitle.setStyleSheet("font-size: 12.5px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Metric Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_queue = MetricCard("Fila Pendente", "0", "#38BDF8", "download")
        self.card_active = MetricCard("Processando", "0", "#F59E0B", "cpu")
        self.card_completed = MetricCard("Finalizados", "0", "#10B981", "check")
        self.card_errors = MetricCard("Erros / Reagendados", "0", "#EF4444", "alert")

        cards_layout.addWidget(self.card_queue)
        cards_layout.addWidget(self.card_active)
        cards_layout.addWidget(self.card_completed)
        cards_layout.addWidget(self.card_errors)

        layout.addLayout(cards_layout)

        # Link Input
        self.link_input = DropTextEdit()
        self.link_input.setPlaceholderText("Cole seus links aqui (Google Drive, pastas ou URLs diretas de PDF/DOCX/PPTX)...")
        self.link_input.setFixedHeight(85)
        layout.addWidget(self.link_input)

        # Action Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("Iniciar Processamento")
        self.start_btn.setIcon(get_svg_icon("play", "#FFFFFF", 16))
        self.start_btn.setMinimumHeight(38)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #6366F1;
            }
        """)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("Pausar")
        self.pause_btn.setIcon(get_svg_icon("pause", "#F1F5F9", 16))
        self.pause_btn.setMinimumHeight(38)
        self.pause_btn.setStyleSheet("background-color: #334155; color: #F1F5F9;")
        btn_layout.addWidget(self.pause_btn)

        self.cancel_btn = QPushButton("Cancelar Tudo")
        self.cancel_btn.setIcon(get_svg_icon("alert", "#F87171", 16))
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.setStyleSheet("background-color: #1E293B; border: 1px solid #EF4444; color: #F87171;")
        btn_layout.addWidget(self.cancel_btn)

        self.export_log_btn = QPushButton("Exportar Log")
        self.export_log_btn.setIcon(get_svg_icon("export", "#94A3B8", 16))
        self.export_log_btn.setMinimumHeight(38)
        self.export_log_btn.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; color: #94A3B8;")
        btn_layout.addWidget(self.export_log_btn)

        self.clear_log_btn = QPushButton("Limpar")
        self.clear_log_btn.setIcon(get_svg_icon("trash", "#94A3B8", 16))
        self.clear_log_btn.setMinimumHeight(38)
        self.clear_log_btn.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; color: #94A3B8;")
        btn_layout.addWidget(self.clear_log_btn)

        self.open_folder_btn = QPushButton("Abrir Pasta")
        self.open_folder_btn.setIcon(get_svg_icon("folder", "#94A3B8", 16))
        self.open_folder_btn.setMinimumHeight(38)
        self.open_folder_btn.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; color: #94A3B8;")
        btn_layout.addWidget(self.open_folder_btn)

        layout.addLayout(btn_layout)

        # Log Control / Filter Toolbar
        log_tools_layout = QHBoxLayout()
        log_tools_layout.setSpacing(10)

        self.log_counter = QLabel("Eventos: 0")
        self.log_counter.setStyleSheet("font-size: 12px; font-weight: 700; color: #94A3B8;")
        log_tools_layout.addWidget(self.log_counter)

        log_tools_layout.addStretch()

        # Phase Filter Dropdown
        self.phase_filter = QComboBox()
        self.phase_filter.setFixedHeight(32)
        self.phase_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 2px 10px;
                color: #F8FAFC;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                selection-background-color: #4F46E5;
                color: #F8FAFC;
            }
        """)
        self.phase_filter.addItems([
            "Todas as Fases",
            "Sucesso",
            "IA Gemini",
            "Sanitização",
            "Conversão",
            "Captura & Download",
            "Erros & Avisos"
        ])
        self.phase_filter.currentTextChanged.connect(self.apply_log_filters)
        log_tools_layout.addWidget(self.phase_filter)

        # Log Search Box
        self.log_search = QLineEdit()
        self.log_search.setPlaceholderText("Buscar no histórico...")
        self.log_search.setFixedHeight(32)
        self.log_search.setFixedWidth(180)
        self.log_search.setStyleSheet("font-size: 12px;")
        self.log_search.textChanged.connect(self.apply_log_filters)
        log_tools_layout.addWidget(self.log_search)

        layout.addLayout(log_tools_layout)

        # Structured Table Log
        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels(["Horário", "Fase", "Descrição", "Detalhes"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setStyleSheet("""
            QTableWidget {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 8px;
                gridline-color: #1E293B;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                color: #F1F5F9;
            }
            QTableWidget::item:selected {
                background-color: #1E293B;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #94A3B8;
                font-weight: 700;
                border: none;
                padding: 6px 10px;
            }
        """)
        self.log_table.itemDoubleClicked.connect(self.on_log_double_clicked)
        layout.addWidget(self.log_table)

        # Core logic setup
        if download_manager:
            self.download_manager = download_manager
        else:
            from core.download_manager import DownloadManager
            self.download_manager = DownloadManager()

        self.download_manager.log_event.connect(self.add_log_entry)
        self.download_manager.metrics_update.connect(self.on_metrics_updated)

        self.start_btn.clicked.connect(self.on_start_clicked)
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        self.clear_log_btn.clicked.connect(self.clear_logs)
        self.export_log_btn.clicked.connect(self.export_logs)
        self.open_folder_btn.clicked.connect(self.on_open_folder_clicked)

    @pyqtSlot(dict)
    def on_metrics_updated(self, m: dict):
        self.card_queue.set_value(m.get("queued", 0))
        self.card_active.set_value(m.get("active", 0))
        self.card_completed.set_value(m.get("completed", 0))
        self.card_errors.set_value(m.get("errors", 0))

        is_paused = m.get("paused", False)
        if is_paused:
            self.pause_btn.setText("Retomar")
            self.pause_btn.setIcon(get_svg_icon("play", "#F1F5F9", 16))
            self.pause_btn.setStyleSheet("background-color: #0284C7; color: #FFFFFF; font-weight: 700;")
        else:
            self.pause_btn.setText("Pausar")
            self.pause_btn.setIcon(get_svg_icon("pause", "#F1F5F9", 16))
            self.pause_btn.setStyleSheet("background-color: #334155; color: #F1F5F9;")

    @pyqtSlot(dict)
    def add_log_entry(self, event: dict):
        self.raw_logs.append(event)
        
        row = 0
        self.log_table.insertRow(row)

        time_item = QTableWidgetItem(event.get("time", ""))
        time_item.setForeground(QColor("#64748B"))

        phase_type = event.get("type", "info").lower()
        badge_text, badge_color = self._get_badge_info(phase_type)

        badge_item = QTableWidgetItem(badge_text)
        badge_item.setForeground(QColor(badge_color))
        badge_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        msg_item = QTableWidgetItem(event.get("message", ""))
        if event.get("path"):
            msg_item.setData(Qt.ItemDataRole.UserRole, event.get("path"))

        details_item = QTableWidgetItem(event.get("details", ""))
        details_item.setForeground(QColor("#94A3B8"))

        self.log_table.setItem(row, 0, time_item)
        self.log_table.setItem(row, 1, badge_item)
        self.log_table.setItem(row, 2, msg_item)
        self.log_table.setItem(row, 3, details_item)

        self.apply_log_filters()

    def _get_badge_info(self, phase_type: str) -> tuple[str, str]:
        badges = {
            "intercept": ("CAPTURA", "#38BDF8"),
            "sanitize": ("SANITIZAÇÃO", "#C084FC"),
            "ai": ("IA GEMINI", "#F59E0B"),
            "convert": ("CONVERSÃO", "#2DD4BF"),
            "download": ("DOWNLOAD", "#60A5FA"),
            "success": ("SUCESSO", "#34D399"),
            "retry": ("RETENTATIVA", "#FB923C"),
            "error": ("ERRO", "#F87171"),
            "info": ("INFO", "#94A3B8")
        }
        return badges.get(phase_type, ("INFO", "#94A3B8"))

    def apply_log_filters(self):
        phase = self.phase_filter.currentText()
        query = self.log_search.text().strip().lower()

        visible_count = 0
        total_count = self.log_table.rowCount()

        for r in range(total_count):
            badge_item = self.log_table.item(r, 1)
            msg_item = self.log_table.item(r, 2)
            details_item = self.log_table.item(r, 3)

            badge_text = badge_item.text().upper() if badge_item else ""
            msg_text = msg_item.text().lower() if msg_item else ""
            details_text = details_item.text().lower() if details_item else ""

            # Filtro por Fase
            phase_match = True
            if phase == "Sucesso":
                phase_match = "SUCESSO" in badge_text
            elif phase == "IA Gemini":
                phase_match = "IA GEMINI" in badge_text
            elif phase == "Sanitização":
                phase_match = "SANITIZAÇÃO" in badge_text
            elif phase == "Conversão":
                phase_match = "CONVERSÃO" in badge_text
            elif phase == "Captura & Download":
                phase_match = "CAPTURA" in badge_text or "DOWNLOAD" in badge_text
            elif phase == "Erros & Avisos":
                phase_match = "ERRO" in badge_text or "RETENTATIVA" in badge_text

            # Filtro por Busca de Texto
            search_match = True
            if query:
                search_match = (query in msg_text) or (query in details_text)

            is_visible = phase_match and search_match
            self.log_table.setRowHidden(r, not is_visible)
            if is_visible:
                visible_count += 1

        self.log_counter.setText(f"Exibindo {visible_count} de {total_count} eventos")

    def on_log_double_clicked(self, item):
        row = item.row()
        msg_item = self.log_table.item(row, 2)
        if msg_item:
            file_path = msg_item.data(Qt.ItemDataRole.UserRole)
            if file_path and os.path.exists(file_path):
                subprocess.run(["open", file_path])

    def clear_logs(self):
        self.log_table.setRowCount(0)
        self.raw_logs.clear()
        self.log_counter.setText("Eventos: 0")

    def export_logs(self):
        if not self.raw_logs:
            QMessageBox.information(self, "Aviso", "Não há registros de log para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório de Log", "archivon_log.txt", "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=== RELATÓRIO DE PROCESSAMENTO ARCHIVON ===\n\n")
                    for entry in self.raw_logs:
                        f.write(f"[{entry.get('time')}] [{entry.get('type').upper()}] {entry.get('message')}")
                        if entry.get('details'):
                            f.write(f" -> {entry.get('details')}")
                        f.write("\n")
                QMessageBox.information(self, "Sucesso", "Log exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar log: {e}")

    def on_start_clicked(self):
        links = self.link_input.toPlainText()
        added_count = self.download_manager.add_links(links)
        
        if added_count > 0:
            self.link_input.clear()
            self.download_manager.start_downloads()
        else:
            QMessageBox.warning(self, "Aviso", "Nenhum link válido foi encontrado no campo de texto.")

    def on_pause_clicked(self):
        self.download_manager.toggle_pause()

    def on_cancel_clicked(self):
        reply = QMessageBox.question(
            self, "Confirmar Cancelamento",
            "Deseja cancelar todas as tarefas pendentes na fila?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.download_manager.cancel_all()

    def on_open_folder_clicked(self):
        from utils.config import load_config
        config = load_config()
        out_folder = os.path.abspath(config.get("output_folder", "Biblioteca"))
        os.makedirs(out_folder, exist_ok=True)
        subprocess.run(["open", out_folder])
