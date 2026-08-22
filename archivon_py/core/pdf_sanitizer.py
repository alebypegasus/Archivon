import os
import pymupdf as fitz # PyMuPDF

class PDFSanitizer:
    def __init__(self):
        pass
        
    def sanitize(self, input_path: str, output_path: str, compress: bool = True) -> tuple[bool, str]:
        """
        Limpeza profunda de metadados e otimização de tamanho usando PyMuPDF.
        Remove metadados embutidos, histórico, TOC e reescreve com garbage collection máximo.
        """
        try:
            if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
                return False, "Arquivo vazio ou inacessível."

            with fitz.open(input_path) as doc:
                if doc.page_count == 0:
                    return False, "Documento não possui páginas válidas."

                # Limpa dicionário de metadados
                doc.set_metadata({})
                
                # Apaga sumário sensível se existir
                try:
                    doc.set_toc([])
                except:
                    pass
                
                # Salva com garbage collection e compressão máxima
                doc.save(
                    output_path,
                    garbage=4,
                    deflate=True,
                    clean=True,
                    deflate_images=compress,
                    deflate_fonts=compress
                )

            return True, "PDF higienizado e otimizado com sucesso."
        except Exception as e:
            return False, f"Erro ao higienizar PDF: {str(e)}"
