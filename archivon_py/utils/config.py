import json
import os

CONFIG_FILE = os.path.expanduser("~/.archivon_settings.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "gemini_api_key": "",
        "temp_folder": os.path.expanduser("~/Downloads/Archivon_Temp"),
        "output_folder": os.path.expanduser("~/Documents/Archivon_Biblioteca")
    }

def save_config(config_dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False
