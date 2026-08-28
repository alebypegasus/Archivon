import sys
import os
import traceback

# Garante a resolução correta de módulos internos (utils, core, gui)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

def global_exception_handler(exctype, value, tb):
    """
    Captura exceções globais não tratadas para evitar que o aplicativo feche
    silenciosamente no PyQt6, registrando no log e informando o usuário.
    """
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(f"CRITICAL ERROR:\n{error_msg}", file=sys.stderr)
    
    # Tenta salvar no log de crash
    try:
        log_dir = os.path.expanduser("~/.archivon_logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "crash.log"), "a", encoding="utf-8") as f:
            f.write(f"\n--- CRASH REPORT ---\n{error_msg}\n")
    except Exception:
        pass

    # Exibe caixa de diálogo amigável se a aplicação Qt estiver ativa
    if QApplication.instance():
        try:
            QMessageBox.critical(
                None,
                "Erro Inesperado - Archivon",
                f"Ocorreu um erro inesperado no aplicativo:\n\n{str(value)}\n\n"
                "As operações foram protegidas. Detalhes foram salvos no log."
            )
        except Exception:
            pass

def main():
    sys.excepthook = global_exception_handler
    
    app = QApplication(sys.argv)
    app.setApplicationName("Archivon")
    app.setOrganizationName("Archivon")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
