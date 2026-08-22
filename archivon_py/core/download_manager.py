import os
import re
import threading
import queue
import time
import shutil
import subprocess
import hashlib
from PyQt6.QtCore import QObject, pyqtSignal

import requests

class DownloadManager(QObject):
    status_update = pyqtSignal(str)
    log_event = pyqtSignal(dict)  # {'time': str, 'type': str, 'message': str, 'details': str, 'path': str}
    metrics_update = pyqtSignal(dict)  # {'queued': int, 'active': int, 'completed': int, 'errors': int, 'paused': bool}
    book_organized = pyqtSignal(str, str, str)  # (title, category, final_path)

    def __init__(self):
        super().__init__()
        self.link_queue = queue.Queue()
        self.process_queue = queue.Queue()
        self.is_downloading = False
        
        self.running_event = threading.Event()
        self.running_event.set()
        self.is_paused = False
        
        self.retry_counts = {}
        self.max_retries = 3
        
        self.active_tasks_lock = threading.Lock()
        self.active_downloads = 0
        self.active_processors = 0
        self.completed_count = 0
        self.error_count = 0
        
        self._gdown_patched = False
        self._threads_started = False
        self.workers = []

    def _now(self) -> str:
        return time.strftime("%H:%M:%S")

    def _emit_log(self, event_type: str, message: str, details: str = "", path: str = ""):
        event = {
            "time": self._now(),
            "type": event_type,
            "message": message,
            "details": details,
            "path": path
        }
        self.log_event.emit(event)
        self.status_update.emit(f"[{event_type.upper()}] {message}")

    def _emit_metrics(self):
        with self.active_tasks_lock:
            metrics = {
                "queued": self.link_queue.qsize() + self.process_queue.qsize(),
                "active": self.active_downloads + self.active_processors,
                "completed": self.completed_count,
                "errors": self.error_count,
                "paused": self.is_paused
            }
        self.metrics_update.emit(metrics)

    def _compute_sha256(self, filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def toggle_pause(self) -> bool:
        if self.is_paused:
            self.running_event.set()
            self.is_paused = False
            self._emit_log("info", "Pipeline retomado.", "Todas as etapas continuam normalmente.")
        else:
            self.running_event.clear()
            self.is_paused = True
            self._emit_log("info", "Pipeline pausado.", "Downloads e processamento pausados imediatamente.")
        
        self._emit_metrics()
        return self.is_paused

    def cancel_all(self):
        while not self.link_queue.empty():
            try:
                self.link_queue.get_nowait()
                self.link_queue.task_done()
            except:
                break

        while not self.process_queue.empty():
            try:
                self.process_queue.get_nowait()
                self.process_queue.task_done()
            except:
                break

        self.running_event.set()
        self.is_paused = False
        self.is_downloading = False
        self._emit_log("info", "Pipeline cancelado.", "Filas de espera foram limpas.")
        self._emit_metrics()
        
    def add_links(self, text: str) -> int:
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        found_links = url_pattern.findall(text)
        count = 0
        for link in found_links:
            clean_link = link.strip().rstrip('.,;:)')
            if clean_link:
                self.link_queue.put(clean_link)
                count += 1
                
        self._emit_metrics()
        return count

    def start_downloads(self):
        self.is_downloading = True
        self.running_event.set()
        self.is_paused = False
        self._apply_gdown_monkey_patch()
        self._ensure_workers()
        self._emit_metrics()

    def _ensure_workers(self):
        if self._threads_started:
            return

        for i in range(2):
            t = threading.Thread(target=self._downloader_worker, name=f"Downloader-{i}", daemon=True)
            t.start()
            self.workers.append(t)

        for i in range(3):
            t = threading.Thread(target=self._processor_worker, name=f"Processor-{i}", daemon=True)
            t.start()
            self.workers.append(t)

        self._threads_started = True

    def _apply_gdown_monkey_patch(self):
        if self._gdown_patched:
            return
            
        try:
            import gdown
            import sys
            import gdown.download_folder
            gdown_folder_module = sys.modules.get('gdown.download_folder')
            
            original_download = gdown.download
            
            def patched_download(*args, **kwargs):
                self.running_event.wait()
                out_path = original_download(*args, **kwargs)
                self.running_event.wait()
                
                if out_path and isinstance(out_path, str):
                    full_path = os.path.abspath(out_path)
                    if os.path.isfile(full_path):
                        self.process_queue.put(full_path)
                        self._emit_log("intercept", f"Arquivo capturado: {os.path.basename(full_path)}", "Enviado para a esteira de sanitização", full_path)
                        self._emit_metrics()
                return out_path
                
            gdown.download = patched_download
            if gdown_folder_module:
                gdown_folder_module.download = patched_download
                
            self._gdown_patched = True
        except Exception as e:
            self._emit_log("error", f"Falha no interceptador GDown: {e}")

    def _check_completion(self):
        with self.active_tasks_lock:
            total_active = self.active_downloads + self.active_processors
            queues_empty = self.link_queue.empty() and self.process_queue.empty()
            
            if queues_empty and total_active == 0 and self.is_downloading:
                self.is_downloading = False
                self._emit_log("success", "Processamento finalizado com sucesso!", "Todas as filas foram esgotadas.")
                self._emit_metrics()

    def _downloader_worker(self):
        while True:
            self.running_event.wait()

            try:
                link = self.link_queue.get(timeout=1.5)
            except queue.Empty:
                self._check_completion()
                continue

            self.running_event.wait()

            with self.active_tasks_lock:
                self.active_downloads += 1
            self._emit_metrics()

            try:
                self._download_task(link)
            except Exception as e:
                self._emit_log("error", f"Erro no download: {link}", str(e))
                with self.active_tasks_lock:
                    self.error_count += 1
            finally:
                with self.active_tasks_lock:
                    self.active_downloads -= 1
                self.link_queue.task_done()
                self._emit_metrics()
                self._check_completion()

    def _processor_worker(self):
        from core.pdf_sanitizer import PDFSanitizer
        from core.ai_categorizer import AICategorizer
        from utils.config import load_config
        
        config = load_config()
        sanitizer = PDFSanitizer()
        categorizer = AICategorizer(
            api_key=config.get("gemini_api_key", ""),
            preferred_model=config.get("gemini_model", "")
        )

        while True:
            self.running_event.wait()

            try:
                filepath = self.process_queue.get(timeout=1.5)
            except queue.Empty:
                self._check_completion()
                continue

            self.running_event.wait()

            with self.active_tasks_lock:
                self.active_processors += 1
            self._emit_metrics()

            try:
                fresh_config = load_config()
                self._process_task(filepath, sanitizer, categorizer, fresh_config)
            except Exception as e:
                self._emit_log("error", f"Falha no processamento ({os.path.basename(filepath)})", str(e))
                with self.active_tasks_lock:
                    self.error_count += 1
            finally:
                with self.active_tasks_lock:
                    self.active_processors -= 1
                self.process_queue.task_done()
                self._emit_metrics()
                self._check_completion()

    def _download_task(self, link):
        from utils.config import load_config
        config = load_config()
        temp_dir = os.path.abspath(config.get("temp_folder", "temp"))
        cookies_file = config.get("cookies_file", "").strip()
        use_cookies = bool(cookies_file and os.path.exists(cookies_file))
        
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            self.running_event.wait()
            self._emit_log("download", f"Iniciando download: {link}")
            
            if "drive.google.com" in link:
                import gdown
                orig_cwd = os.getcwd()
                os.chdir(temp_dir)
                try:
                    if "/folders/" in link:
                        self._emit_log("download", f"Baixando pasta do Google Drive...", link)
                        if use_cookies:
                            gdown.download_folder(link, quiet=True, use_cookies=True, proxy=None)
                        else:
                            gdown.download_folder(link, quiet=True, use_cookies=False)
                    else:
                        if use_cookies:
                            gdown.download(link, quiet=True, fuzzy=True, use_cookies=True)
                        else:
                            gdown.download(link, quiet=True, fuzzy=True, use_cookies=False)
                finally:
                    os.chdir(orig_cwd)
                    
            elif any(link.lower().endswith(ext) for ext in [".pdf", ".docx", ".doc", ".pptx", ".ppt"]):
                filename = link.split("/")[-1].split("?")[0]
                if not filename:
                    filename = f"download_{int(time.time())}.pdf"
                dest_path = os.path.join(temp_dir, filename)
                
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                response = requests.get(link, stream=True, headers=headers, timeout=30)
                response.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        self.running_event.wait()
                        if chunk:
                            f.write(chunk)
                            
                self.process_queue.put(dest_path)
                self._emit_log("download", f"Download concluído: {filename}", "Enviado para a esteira", dest_path)
            else:
                import gdown
                orig_cwd = os.getcwd()
                os.chdir(temp_dir)
                try:
                    gdown.download(link, quiet=True, fuzzy=True, use_cookies=use_cookies)
                finally:
                    os.chdir(orig_cwd)

        except Exception as e:
            retries = self.retry_counts.get(link, 0)
            if retries < self.max_retries:
                self.retry_counts[link] = retries + 1
                self._emit_log("retry", f"Reagendando tentativa {self.retry_counts[link]}/{self.max_retries}: {link}", str(e))
                time.sleep(2)
                self.link_queue.put(link)
            else:
                self._emit_log("error", f"Falha definitiva após {self.max_retries} tentativas: {link}", str(e))
                with self.active_tasks_lock:
                    self.error_count += 1

    def _convert_to_pdf(self, input_path: str, temp_dir: str) -> str:
        soffice_bin = shutil.which("soffice")
        if not soffice_bin and os.path.exists("/Applications/LibreOffice.app/Contents/MacOS/soffice"):
            soffice_bin = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

        if not soffice_bin:
            raise FileNotFoundError("LibreOffice não encontrado no sistema.")

        cmd = [soffice_bin, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        
        if proc.returncode != 0:
            raise RuntimeError(f"Erro na conversão (código {proc.returncode}): {proc.stderr}")

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        expected_pdf = os.path.join(temp_dir, f"{base_name}.pdf")
        if os.path.exists(expected_pdf):
            return expected_pdf
        raise FileNotFoundError(f"PDF convertido não encontrado em: {expected_pdf}")

    def _find_exact_duplicate(self, clean_temp: str, output_dir: str) -> str | None:
        temp_hash = self._compute_sha256(clean_temp)
        temp_size = os.path.getsize(clean_temp)

        for root, _, files in os.walk(output_dir):
            for f in files:
                if f.lower().endswith(".pdf"):
                    existing_path = os.path.join(root, f)
                    if os.path.getsize(existing_path) == temp_size:
                        if self._compute_sha256(existing_path) == temp_hash:
                            return existing_path
        return None

    def _process_task(self, filepath, sanitizer, categorizer, config):
        if not os.path.exists(filepath):
            return

        self.running_event.wait()

        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        temp_dir = os.path.abspath(config.get("temp_folder", "temp"))
        output_dir = os.path.abspath(config.get("output_folder", "Biblioteca"))
        compress_pdf = config.get("compress_pdf", True)
        os.makedirs(output_dir, exist_ok=True)

        supported_conversions = [".doc", ".docx", ".ppt", ".pptx"]
        target_pdf_path = filepath
        created_converted_file = False

        try:
            # 1. Conversão Office
            if ext in supported_conversions:
                self.running_event.wait()
                self._emit_log("convert", f"Convertendo apresentação/documento: {filename}")
                try:
                    target_pdf_path = self._convert_to_pdf(filepath, temp_dir)
                    created_converted_file = True
                except Exception as conv_err:
                    self._emit_log("error", f"Erro na conversão de {filename}", str(conv_err))
                    return
            elif ext != ".pdf":
                return

            self.running_event.wait()

            # 2. Sanitização e Compressão
            pdf_name = os.path.basename(target_pdf_path)
            clean_temp = os.path.join(temp_dir, f"clean_{pdf_name}")
            self._emit_log("sanitize", f"Higienizando e otimizando: {pdf_name}")
            
            success, msg = sanitizer.sanitize(target_pdf_path, clean_temp, compress=compress_pdf)
            if not success or not os.path.exists(clean_temp):
                clean_temp = target_pdf_path

            self.running_event.wait()

            # 3. Desduplicação por Hash SHA-256
            existing_dup = self._find_exact_duplicate(clean_temp, output_dir)
            if existing_dup:
                self._emit_log("info", f"Duplicata exata descartada: {pdf_name}", f"Já existe como: {os.path.basename(existing_dup)}", existing_dup)
                with self.active_tasks_lock:
                    self.completed_count += 1
                return

            # 4. Categorização com IA (com suporte a Gemini Vision se escaneado)
            self._emit_log("ai", f"Analisando metadados com IA: {pdf_name}")
            meta = categorizer.categorize_pdf(clean_temp)
            
            titulo = meta.get("titulo", os.path.splitext(pdf_name)[0]).strip()
            autor = meta.get("autor", "Desconhecido").strip()
            categoria = meta.get("categoria", "Geral").strip()
            
            self.running_event.wait()

            # 5. Organização e Versionamento
            cat_folder = os.path.join(output_dir, categoria)
            os.makedirs(cat_folder, exist_ok=True)
            
            base_filename = f"{titulo} - Autor: {autor}.pdf"
            final_path = os.path.join(cat_folder, base_filename)
            
            if os.path.exists(final_path):
                counter = 2
                while True:
                    candidate = os.path.join(cat_folder, f"{titulo} (V{counter}) - Autor: {autor}.pdf")
                    if not os.path.exists(candidate):
                        final_path = candidate
                        break
                    counter += 1
            
            shutil.move(clean_temp, final_path)
            self._emit_log("success", f"Organizado: {os.path.basename(final_path)}", f"Destino: [{categoria}]", final_path)
            self.book_organized.emit(titulo, categoria, final_path)
            
            with self.active_tasks_lock:
                self.completed_count += 1

        finally:
            if os.path.exists(filepath) and filepath != target_pdf_path:
                try:
                    os.remove(filepath)
                except:
                    pass
                    
            if created_converted_file and os.path.exists(target_pdf_path):
                try:
                    os.remove(target_pdf_path)
                except:
                    pass
                    
            if 'clean_temp' in locals() and os.path.exists(clean_temp) and clean_temp != target_pdf_path:
                try:
                    os.remove(clean_temp)
                except:
                    pass
