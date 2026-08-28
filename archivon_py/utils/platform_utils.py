import os
import sys
import subprocess
import shutil

def open_file_or_folder(path: str) -> bool:
    """
    Abre um arquivo ou diretório no aplicativo padrão do sistema operacional.
    Suporta Windows, macOS e Linux com tratamento completo de erros.
    """
    if not path or not os.path.exists(path):
        return False

    try:
        norm_path = os.path.abspath(path)
        if sys.platform.startswith("win"):
            os.startfile(norm_path)
            return True
        elif sys.platform == "darwin":
            subprocess.run(["open", norm_path], check=True)
            return True
        else:
            # Linux e outros sistemas Unix-like
            if shutil.which("xdg-open"):
                subprocess.run(["xdg-open", norm_path], check=True)
                return True
            elif shutil.which("gio"):
                subprocess.run(["gio", "open", norm_path], check=True)
                return True
            elif shutil.which("kde-open"):
                subprocess.run(["kde-open", norm_path], check=True)
                return True
            elif shutil.which("gnome-open"):
                subprocess.run(["gnome-open", norm_path], check=True)
                return True
            else:
                return False
    except Exception as e:
        print(f"Erro ao abrir arquivo/pasta ({path}): {e}")
        return False

def reveal_in_file_manager(path: str) -> bool:
    """
    Destaca/revela o arquivo no gerenciador de arquivos do sistema operacional:
    - Windows: Explorer com o arquivo selecionado
    - macOS: Finder com o arquivo selecionado (-R)
    - Linux: Abre o diretório contendo o arquivo via gerenciador padrão
    """
    if not path or not os.path.exists(path):
        return False

    try:
        norm_path = os.path.abspath(path)
        if sys.platform.startswith("win"):
            # No Windows, explorer /select, <caminho> seleciona o arquivo
            subprocess.run(["explorer", f"/select,{os.path.normpath(norm_path)}"])
            return True
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", norm_path], check=True)
            return True
        else:
            # Linux
            parent_dir = os.path.dirname(norm_path) if os.path.isfile(norm_path) else norm_path
            return open_file_or_folder(parent_dir)
    except Exception as e:
        print(f"Erro ao revelar no gerenciador de arquivos ({path}): {e}")
        return False
