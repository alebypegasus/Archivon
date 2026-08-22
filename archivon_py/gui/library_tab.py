import os
import subprocess
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton,
    QHBoxLayout, QLineEdit, QHeaderView, QSplitter, QFrame, QScrollArea, QApplication,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QFileSystemWatcher, QSize
from PyQt6.QtGui import QPixmap, QImage, QColor
from utils.config import load_config
from utils.icons import get_svg_icon
from utils.theme import get_theme_colors, get_current_theme_name

class LibraryTab(QWidget):
    def __init__(self, download_manager=None):
        super().__init__()
        self.selected_file_path = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)
        
        # Header Row
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Biblioteca & Acervo Organizado")
        title.setStyleSheet("font-size: 22px; font-weight: 800;")
        
        self.stats_label = QLabel("Carregando acervo...")
        self.stats_label.setStyleSheet("font-size: 12.5px; opacity: 0.75;")
        title_box.addWidget(title)
        title_box.addWidget(self.stats_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.export_catalog_btn = QPushButton("Exportar Catálogo")
        self.export_catalog_btn.setIcon(get_svg_icon("export", "#FFFFFF", 16))
        self.export_catalog_btn.clicked.connect(self.export_catalog)
        header_layout.addWidget(self.export_catalog_btn)

        self.refresh_btn = QPushButton("Atualizar")
        self.refresh_btn.setIcon(get_svg_icon("refresh", "#FFFFFF", 16))
        self.refresh_btn.clicked.connect(self.refresh_list)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(header_layout)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por título, autor ou categoria em tempo real...")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.filter_tree)
        main_layout.addWidget(self.search_input)

        # Splitter Layout (Left: Tree, Right: Preview Inspector)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(148, 163, 184, 0.2);
                width: 2px;
            }
        """)

        # Left Container: Tree View
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Título da Obra / Categoria", "Tamanho"])
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QTreeWidget::item {
                height: 32px;
                padding: 2px 4px;
                border-radius: 4px;
            }
            QHeaderView::section {
                font-weight: 700;
                border: none;
                padding: 6px 10px;
            }
        """)
        self.tree_widget.itemClicked.connect(self.on_item_selected)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        left_layout.addWidget(self.tree_widget)
        splitter.addWidget(left_widget)

        # Right Container: Book Inspector Panel
        self.right_panel = QFrame()
        self.right_panel.setObjectName("inspectorCard")
        self.right_panel.setStyleSheet("""
            QFrame#inspectorCard {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 10px;
            }
        """)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        self.inspector_title = QLabel("Detalhes da Obra")
        self.inspector_title.setStyleSheet("font-size: 13px; font-weight: 800; text-transform: uppercase; opacity: 0.8;")
        right_layout.addWidget(self.inspector_title)

        # Cover Thumbnail
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedHeight(210)
        self.cover_label.setStyleSheet("border-radius: 8px; border: 1px dashed rgba(148, 163, 184, 0.3);")
        self.cover_label.setText("Selecione um livro para pré-visualizar")
        right_layout.addWidget(self.cover_label)

        # Meta fields
        self.book_title_label = QLabel("Nenhum livro selecionado")
        self.book_title_label.setWordWrap(True)
        self.book_title_label.setStyleSheet("font-size: 16px; font-weight: 800;")
        right_layout.addWidget(self.book_title_label)

        self.book_cat_label = QLabel("Categoria: —")
        self.book_cat_label.setStyleSheet("font-size: 12.5px; color: #38BDF8; font-weight: 600;")
        right_layout.addWidget(self.book_cat_label)

        self.book_pages_label = QLabel("Páginas: — | Tamanho: —")
        self.book_pages_label.setStyleSheet("font-size: 12px; opacity: 0.75;")
        right_layout.addWidget(self.book_pages_label)

        # Action Buttons in Inspector
        insp_btn_layout = QVBoxLayout()
        insp_btn_layout.setSpacing(8)

        self.open_pdf_btn = QPushButton("Abrir no Leitor de PDF")
        self.open_pdf_btn.setIcon(get_svg_icon("book", "#FFFFFF", 16))
        self.open_pdf_btn.setFixedHeight(36)
        self.open_pdf_btn.setEnabled(False)
        self.open_pdf_btn.clicked.connect(self.open_selected_pdf)
        insp_btn_layout.addWidget(self.open_pdf_btn)

        self.reveal_btn = QPushButton("Revelar no Finder")
        self.reveal_btn.setIcon(get_svg_icon("folder", "#FFFFFF", 16))
        self.reveal_btn.setFixedHeight(36)
        self.reveal_btn.setEnabled(False)
        self.reveal_btn.clicked.connect(self.reveal_selected_finder)
        insp_btn_layout.addWidget(self.reveal_btn)

        self.copy_path_btn = QPushButton("Copiar Caminho do Arquivo")
        self.copy_path_btn.setIcon(get_svg_icon("copy", "#94A3B8", 16))
        self.copy_path_btn.setFixedHeight(36)
        self.copy_path_btn.setEnabled(False)
        self.copy_path_btn.clicked.connect(self.copy_selected_path)
        insp_btn_layout.addWidget(self.copy_path_btn)

        right_layout.addLayout(insp_btn_layout)
        right_layout.addStretch()

        splitter.addWidget(self.right_panel)
        splitter.setSizes([650, 350])
        main_layout.addWidget(splitter)

        # Live Real-Time Auto-Watcher
        self.fs_watcher = QFileSystemWatcher(self)
        self.fs_watcher.directoryChanged.connect(self.refresh_list)

        if download_manager:
            download_manager.book_organized.connect(self.on_book_organized_live)

        self.refresh_list()

    @pyqtSlot(str, str, str)
    def on_book_organized_live(self, title: str, category: str, path: str):
        self.refresh_list()

    def _format_size(self, bytes_size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"

    def refresh_list(self):
        self.tree_widget.clear()
        config_data = load_config()
        out_folder = os.path.abspath(config_data.get("output_folder", "Biblioteca"))
        
        if not os.path.exists(out_folder):
            self.stats_label.setText(f"Pasta de destino não encontrada: {out_folder}")
            return

        current_paths = self.fs_watcher.directories()
        if out_folder not in current_paths:
            self.fs_watcher.addPath(out_folder)

        total_books = 0
        categories_count = 0

        entries = sorted(os.listdir(out_folder))
        folder_icon = get_svg_icon("folder", "#38BDF8", 16)
        book_icon = get_svg_icon("book", "#818CF8", 16)

        for entry in entries:
            full_entry_path = os.path.join(out_folder, entry)
            
            if os.path.isdir(full_entry_path):
                if full_entry_path not in current_paths:
                    try:
                        self.fs_watcher.addPath(full_entry_path)
                    except:
                        pass

                cat_item = QTreeWidgetItem(self.tree_widget, [entry, ""])
                cat_item.setIcon(0, folder_icon)
                cat_item.setExpanded(True)
                cat_books = 0
                
                for file_name in sorted(os.listdir(full_entry_path)):
                    if file_name.lower().endswith(".pdf"):
                        file_path = os.path.join(full_entry_path, file_name)
                        file_size = self._format_size(os.path.getsize(file_path))
                        
                        book_item = QTreeWidgetItem(cat_item, [file_name, file_size])
                        book_item.setIcon(0, book_icon)
                        book_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                        book_item.setData(0, Qt.ItemDataRole.UserRole + 1, entry)
                        cat_books += 1
                        total_books += 1

                if cat_books > 0:
                    cat_item.setText(1, f"{cat_books} item(ns)")
                    categories_count += 1
                else:
                    self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(cat_item))
                    
            elif entry.lower().endswith(".pdf"):
                file_size = self._format_size(os.path.getsize(full_entry_path))
                book_item = QTreeWidgetItem(self.tree_widget, [entry, file_size])
                book_item.setIcon(0, book_icon)
                book_item.setData(0, Qt.ItemDataRole.UserRole, full_entry_path)
                book_item.setData(0, Qt.ItemDataRole.UserRole + 1, "Geral")
                total_books += 1

        self.stats_label.setText(f"Total: {total_books} livro(s) em {categories_count} categoria(s)")

    def filter_tree(self, text: str):
        query = text.strip().lower()
        
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            match_found_in_cat = False
            
            if top_item.childCount() > 0:
                for c in range(top_item.childCount()):
                    child = top_item.child(c)
                    if query in child.text(0).lower():
                        child.setHidden(False)
                        match_found_in_cat = True
                    else:
                        child.setHidden(True)
                        
                top_item.setHidden(not match_found_in_cat and query not in top_item.text(0).lower())
            else:
                top_item.setHidden(query not in top_item.text(0).lower())

    def on_item_selected(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        category = item.data(0, Qt.ItemDataRole.UserRole + 1)
        
        if path and os.path.exists(path):
            self.selected_file_path = path
            self.open_pdf_btn.setEnabled(True)
            self.reveal_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)
            
            filename = os.path.basename(path).replace(".pdf", "")
            self.book_title_label.setText(filename)
            self.book_cat_label.setText(f"Categoria: {category if category else 'Geral'}")
            
            try:
                import pymupdf as fitz
                with fitz.open(path) as doc:
                    pages = len(doc)
                    size = self._format_size(os.path.getsize(path))
                    self.book_pages_label.setText(f"Páginas: {pages} | Tamanho: {size}")
                    
                    if pages > 0:
                        pix = doc[0].get_pixmap(dpi=100)
                        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                        pixmap = QPixmap.fromImage(img)
                        scaled_pixmap = pixmap.scaled(180, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.cover_label.setPixmap(scaled_pixmap)
                        self.cover_label.setStyleSheet("border-radius: 8px; border: 1px solid #4F46E5;")
            except Exception as e:
                self.cover_label.setText("Capa indisponível")
                self.cover_label.setStyleSheet("border-radius: 8px; border: 1px dashed rgba(148, 163, 184, 0.3);")
        else:
            self.selected_file_path = None
            self.open_pdf_btn.setEnabled(False)
            self.reveal_btn.setEnabled(False)
            self.copy_path_btn.setEnabled(False)
            self.book_title_label.setText("Pasta de Categoria")
            self.book_cat_label.setText(f"Categoria: {item.text(0)}")
            self.book_pages_label.setText(item.text(1))
            self.cover_label.clear()
            self.cover_label.setText("Selecione um livro individual")

    def on_item_double_clicked(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            subprocess.run(["open", path])

    def open_selected_pdf(self):
        if self.selected_file_path and os.path.exists(self.selected_file_path):
            subprocess.run(["open", self.selected_file_path])

    def reveal_selected_finder(self):
        if self.selected_file_path and os.path.exists(self.selected_file_path):
            subprocess.run(["open", "-R", self.selected_file_path])

    def copy_selected_path(self):
        if self.selected_file_path:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.selected_file_path)

    def export_catalog(self):
        config_data = load_config()
        out_folder = os.path.abspath(config_data.get("output_folder", "Biblioteca"))

        if not os.path.exists(out_folder):
            QMessageBox.warning(self, "Aviso", "A pasta da biblioteca não foi encontrada.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Catálogo de Livros", "catalogo_archivon.html", "Página Web HTML (*.html);;Planilha CSV (*.csv)"
        )
        if not file_path:
            return

        try:
            books_data = []
            for root, _, files in os.walk(out_folder):
                category = os.path.basename(root) if root != out_folder else "Geral"
                for f in sorted(files):
                    if f.lower().endswith(".pdf"):
                        full_p = os.path.join(root, f)
                        size_str = self._format_size(os.path.getsize(full_p))
                        books_data.append({
                            "title": f.replace(".pdf", ""),
                            "category": category,
                            "size": size_str,
                            "path": full_p
                        })

            if file_path.lower().endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["title", "category", "size", "path"])
                    writer.writeheader()
                    writer.writerows(books_data)
            else:
                rows_html = ""
                for idx, b in enumerate(books_data, 1):
                    rows_html += f"""
                    <tr>
                        <td style='padding:10px; border-bottom:1px solid rgba(148, 163, 184, 0.2);'>{idx}</td>
                        <td style='padding:10px; border-bottom:1px solid rgba(148, 163, 184, 0.2); font-weight:bold;'>{b['title']}</td>
                        <td style='padding:10px; border-bottom:1px solid rgba(148, 163, 184, 0.2);'><span style='background:#4F46E5; color:#fff; padding:3px 8px; border-radius:4px;'>{b['category']}</span></td>
                        <td style='padding:10px; border-bottom:1px solid rgba(148, 163, 184, 0.2);'>{b['size']}</td>
                    </tr>
                    """
                html_content = f"""
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <title>Catálogo Archivon - {len(books_data)} Obras</title>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0F172A; color: #F8FAFC; padding: 40px; }}
                        h1 {{ color: #6366F1; }}
                        table {{ width: 100%; border-collapse: collapse; background: #1E293B; border-radius: 8px; overflow: hidden; margin-top: 20px; }}
                        th {{ background: #0B1120; color: #94A3B8; padding: 12px; text-align: left; }}
                    </style>
                </head>
                <body>
                    <h1>⚡ Catálogo Geral Archivon</h1>
                    <p>Total de Obras Catalogadas: <strong>{len(books_data)}</strong></p>
                    <table>
                        <thead>
                            <tr><th>#</th><th>Título da Obra & Autor</th><th>Categoria</th><th>Tamanho</th></tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </body>
                </html>
                """
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

            QMessageBox.information(self, "Sucesso", f"Catálogo com {len(books_data)} livro(s) exportado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar catálogo: {e}")
