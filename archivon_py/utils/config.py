import json
import os
import sys
import shutil

CONFIG_FILE = os.path.expanduser("~/.archivon_settings.json")

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash-lite",
    "soffice_path": "",
    "cookies_file": "",
    "temp_folder": os.path.expanduser("~/Downloads/Archivon_Temp"),
    "output_folder": os.path.expanduser("~/Documents/Archivon_Biblioteca"),
    "compress_pdf": True,
    "theme": "dark"
}

def load_config() -> dict:
    """
    Carrega as configurações salvas do usuário mesclando com os padrões seguros.
    Garante que os caminhos de pastas sejam absolutos e válidos.
    """
    config = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception as e:
            print(f"Aviso: Não foi possível ler o arquivo de configurações ({e}). Usando padrões.")

    # Sanitização e normalização de caminhos
    if config.get("temp_folder"):
        config["temp_folder"] = os.path.abspath(os.path.expanduser(config["temp_folder"]))
    else:
        config["temp_folder"] = DEFAULT_CONFIG["temp_folder"]

    if config.get("output_folder"):
        config["output_folder"] = os.path.abspath(os.path.expanduser(config["output_folder"]))
    else:
        config["output_folder"] = DEFAULT_CONFIG["output_folder"]

    # Sanitização de chave API (remove aspas e espaços acidentais)
    if config.get("gemini_api_key"):
        config["gemini_api_key"] = str(config["gemini_api_key"]).strip().strip("'\"")

    return config

def save_config(config_dict: dict) -> bool:
    """
    Salva o dicionário de configurações no arquivo JSON do usuário.
    Cria os diretórios pai caso necessário e sanitiza os campos.
    """
    try:
        clean_config = dict(DEFAULT_CONFIG)
        clean_config.update(config_dict)

        if clean_config.get("gemini_api_key"):
            clean_config["gemini_api_key"] = str(clean_config["gemini_api_key"]).strip().strip("'\"")

        parent_dir = os.path.dirname(CONFIG_FILE)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações em {CONFIG_FILE}: {e}")
        return False

def get_soffice_binary(config: dict = None) -> str | None:
    """
    Detecta automaticamente o executável do LibreOffice (soffice)
    de forma multiplataforma e resiliente (Windows, macOS, Linux).
    """
    if config:
        custom_path = config.get("soffice_path", "").strip()
        if custom_path and os.path.exists(custom_path):
            return custom_path

    # 1. Procura no PATH global do sistema operacional
    for bin_name in ["soffice", "soffice.exe", "libreoffice"]:
        found = shutil.which(bin_name)
        if found:
            return found

    # 2. Caminhos padrão no macOS
    if sys.platform == "darwin":
        mac_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
            os.path.join(os.getcwd(), "LibreOffice.app/Contents/MacOS/soffice")
        ]
        for p in mac_paths:
            if os.path.exists(p):
                return p

    # 3. Caminhos padrão no Windows
    elif sys.platform.startswith("win"):
        win_candidates = []
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        prog_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", "")

        win_candidates.extend([
            os.path.join(prog_files, "LibreOffice", "program", "soffice.exe"),
            os.path.join(prog_files_x86, "LibreOffice", "program", "soffice.exe"),
            os.path.join(prog_files, "The Document Foundation", "LibreOffice", "program", "soffice.exe"),
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            os.path.join(os.getcwd(), "LibreOffice", "program", "soffice.exe"),
            os.path.join(os.getcwd(), "libreoffice", "program", "soffice.exe"),
            os.path.join(os.path.dirname(os.getcwd()), "LibreOffice", "program", "soffice.exe")
        ])
        if local_app_data:
            win_candidates.append(os.path.join(local_app_data, "Programs", "LibreOffice", "program", "soffice.exe"))

        for p in win_candidates:
            if os.path.exists(p):
                return p

    # 4. Caminhos padrão no Linux
    else:
        linux_paths = [
            "/usr/bin/soffice",
            "/usr/local/bin/soffice",
            "/usr/bin/libreoffice",
            "/usr/local/bin/libreoffice",
            "/usr/lib/libreoffice/program/soffice",
            "/opt/libreoffice/program/soffice",
            "/snap/bin/libreoffice",
            "/var/lib/flatpak/exports/bin/org.libreoffice.LibreOffice"
        ]
        for p in linux_paths:
            if os.path.exists(p):
                return p

    return None
