import os
import json
import sys
import time
import io
import re

# Compatibilidade universal para Protobuf em todas as versões do Python (3.10 a 3.14+)
if sys.version_info >= (3, 14):
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    sys.modules["google._upb._message"] = None
else:
    try:
        import google._upb._message
    except Exception:
        os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
        sys.modules["google._upb._message"] = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class AICategorizer:
    _discovered_model_name = None

    def __init__(self, api_key: str = "", preferred_model: str = None):
        self.enabled = False
        self.api_key = str(api_key).strip().strip("'\"") if api_key else ""
        self.preferred_model = preferred_model.strip() if preferred_model and preferred_model.strip() else None
        self.model = None
        self.model_name = self.preferred_model or "gemini-2.0-flash-lite"
        
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self.model_name = self._resolve_best_model(self.preferred_model)
                if self.model_name:
                    self.model = genai.GenerativeModel(self.model_name)
                    self.enabled = True
            except Exception as e:
                print(f"Aviso ao inicializar IA Gemini: {e}")
                self.enabled = False

    def _resolve_best_model(self, preferred: str = None) -> str:
        if preferred and preferred.strip():
            return preferred.strip()

        if AICategorizer._discovered_model_name:
            return AICategorizer._discovered_model_name

        candidate_order = [
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

        if genai is None or not self.api_key:
            return "gemini-2.0-flash-lite"

        try:
            available_models = []
            for m in genai.list_models():
                methods = getattr(m, "supported_generation_methods", [])
                if "generateContent" in methods:
                    clean_name = m.name.replace("models/", "")
                    available_models.append(clean_name)
            
            for candidate in candidate_order:
                if candidate in available_models:
                    AICategorizer._discovered_model_name = candidate
                    return candidate

            if available_models:
                AICategorizer._discovered_model_name = available_models[0]
                return available_models[0]
        except Exception:
            pass

        return "gemini-2.0-flash-lite"

    def test_connection(self) -> tuple[bool, str, list[str]]:
        if genai is None:
            return False, "Biblioteca google-generativeai não está instalada ou falhou ao carregar.", []

        clean_key = str(self.api_key).strip().strip("'\"")
        if not clean_key:
            return False, "Chave de API não informada.", []

        try:
            genai.configure(api_key=clean_key)
            supported = []
            for m in genai.list_models():
                methods = getattr(m, "supported_generation_methods", [])
                if "generateContent" in methods:
                    clean_name = m.name.replace("models/", "")
                    supported.append(clean_name)
            
            if not supported:
                return False, "Chave aceita, mas nenhum modelo com suporte a 'generateContent' foi retornado pela API.", []
                
            return True, f"Conexão bem-sucedida! {len(supported)} modelo(s) disponíveis.", supported
        except Exception as e:
            err_msg = str(e)
            if "API_KEY_INVALID" in err_msg or "400" in err_msg:
                return False, "Chave de API inválida. Verifique os caracteres e tente novamente.", []
            elif "PERMISSION_DENIED" in err_msg or "403" in err_msg:
                return False, "Permissão negada. A chave pode estar desativada ou sem acesso ao Gemini API.", []
            return False, f"Falha de comunicação com a API do Gemini: {err_msg}", []

    def _clean_fallback_title(self, raw_name: str) -> str:
        name = raw_name.replace(".pdf", "")
        if name.startswith("clean_"):
            name = name[6:]
        name = name.replace("_", " ").replace("-", " ")
        name = " ".join(name.split())
        return name.title() if name else "Documento Sem Titulo"

    def categorize_pdf(self, pdf_path: str) -> dict:
        """
        Analisa o PDF através de texto ou visão computacional (Gemini Vision)
        caso seja um livro escaneado em imagem.
        """
        raw_basename = os.path.basename(pdf_path)
        fallback_title = self._clean_fallback_title(raw_basename)

        default_result = {
            "titulo": fallback_title,
            "autor": "Desconhecido",
            "categoria": "Geral",
            "sinopse": "Obra bibliográfica catalogada no acervo."
        }

        if not self.enabled or not self.model:
            return default_result

        try:
            import pymupdf as fitz
            
            text_sample = ""
            cover_image_bytes = None
            total_pages = 0

            with fitz.open(pdf_path) as doc:
                total_pages = len(doc)
                if total_pages == 0:
                    return default_result
                
                # Coleta texto das primeiras 8 páginas
                for i in range(min(8, total_pages)):
                    try:
                        page_text = doc[i].get_text()
                        if page_text:
                            text_sample += f"--- PÁGINA {i+1} ---\n" + page_text + "\n"
                    except Exception:
                        pass

                # Coleta de amostra intermediária
                if total_pages > 12:
                    mid_idx = total_pages // 2
                    for i in range(mid_idx, min(mid_idx + 3, total_pages)):
                        try:
                            page_text = doc[i].get_text()
                            if page_text:
                                text_sample += f"--- PÁGINA CENTRAL {i+1} ---\n" + page_text + "\n"
                        except Exception:
                            pass

                # Se o PDF for um scanner puro sem OCR (< 40 caracteres de texto), extrai a imagem da capa
                if len(text_sample.strip()) < 40:
                    try:
                        first_page = doc[0]
                        pix = first_page.get_pixmap(dpi=150)
                        cover_image_bytes = pix.tobytes("png")
                    except Exception as img_err:
                        print(f"Aviso ao extrair capa para Vision: {img_err}")

            prompt_instructions = """
Você é um bibliotecário e curador bibliográfico de elite especializado em acervos raros, literatura ocultista, esotérica, histórica, religiosa e acadêmica.

SUA MISSÃO:
1. Identifique o TÍTULO REAL DA OBRA. Formate em Title Case elegante (Ex: 'A Bruxa Solitária', 'Tratado Elemental de Magia Prática'). NUNCA use caixa alta integral (ALL CAPS) e NUNCA inclua prefixos como 'clean_'.
2. Identifique o AUTOR PRINCIPAL oficial (Ex: 'Rae Beth', 'Papus', 'Helena P. Blavatsky'). Se não houver autor identificado com certeza, use 'Desconhecido'.
3. Classifique a obra na CATEGORIA TEMÁTICA mais precisa entre as seguintes opções:
   - Bruxaria
   - Ocultismo
   - Magia
   - Hermetismo & Alquimia
   - Maçonaria & Ordens
   - Umbanda & Candomble
   - Espiritualismo & Teosofia
   - Filosofia & Mitologia
   - Historia & Sociedade
   - Psicologia & Autoconhecimento
   - Geral
4. Escreva uma breve SINOPSE (1 ou 2 frases) explicando a essência da obra.

RETORNE EXCLUSIVAMENTE UM JSON PURO:
{
  "titulo": "Título formatado em Title Case",
  "autor": "Nome do Autor Principal",
  "categoria": "Categoria exata da lista",
  "sinopse": "Breve síntese da obra"
}
"""

            # Prepara o payload (Texto ou Imagem da Capa via Gemini Vision)
            content_payload = []
            if cover_image_bytes:
                content_payload = [
                    {"mime_type": "image/png", "data": cover_image_bytes},
                    f"{prompt_instructions}\n\n[ATENÇÃO: Este livro é um scanner sem texto digital. Analise a imagem da capa fornecida acima para identificar o título, autor e tema da obra.]"
                ]
            else:
                content_payload = [
                    f"{prompt_instructions}\n\nTexto extraído do documento:\n{text_sample[:4500]}"
                ]

            max_retries = 3
            response_text = ""
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(content_payload)
                    if response:
                        try:
                            # Acesso seguro a response.text prevenindo ValueError de filtros de segurança
                            response_text = response.text
                        except Exception:
                            # Tenta extrair das partes manualmente
                            if hasattr(response, "candidates") and response.candidates:
                                candidate = response.candidates[0]
                                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                                    for part in candidate.content.parts:
                                        if hasattr(part, "text") and part.text:
                                            response_text += part.text
                        if response_text and response_text.strip():
                            break
                except Exception as api_err:
                    err_msg = str(api_err).lower()
                    if "404" in err_msg or "not found" in err_msg:
                        new_model_name = self._resolve_best_model()
                        self.model = genai.GenerativeModel(new_model_name)
                    
                    if attempt < max_retries - 1:
                        time.sleep(1.5 * (attempt + 1))
                    else:
                        return default_result

            if not response_text or not response_text.strip():
                return default_result

            # Extração segura de JSON via regex
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                return default_result

            data = json.loads(json_match.group(0))

            titulo = str(data.get("titulo", fallback_title)).replace("/", "-").replace("\\", "-").strip()
            if titulo.startswith("clean_"):
                titulo = titulo[6:].strip()
            if not titulo or len(titulo) < 2:
                titulo = fallback_title

            autor = str(data.get("autor", "Desconhecido")).replace("/", "-").replace("\\", "-").strip()
            categoria = str(data.get("categoria", "Geral")).replace("/", "-").replace("\\", "-").strip()
            sinopse = str(data.get("sinopse", default_result["sinopse"])).strip()

            return {
                "titulo": titulo,
                "autor": autor,
                "categoria": categoria,
                "sinopse": sinopse
            }

        except Exception as e:
            print(f"Aviso durante categorização com IA: {e}")
            return default_result
