# ⚡ ARCHIVON — Gestor de Acervos, Sanitizador de PDFs & Curadoria com IA

<p align="center">
  <img src="https://img.shields.io/badge/Versão-3.5.0-6366F1?style=for-the-badge" alt="Versão 3.5.0">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.14-38BDF8?style=for-the-badge" alt="Python Version">
  <img src="https://img.shields.io/badge/Gemini-2.0%20Flash%20%7C%20Vision-F59E0B?style=for-the-badge" alt="Gemini AI">
  <img src="https://img.shields.io/badge/Plataformas-macOS%20%7C%20Windows%20%7C%20Linux-10B981?style=for-the-badge" alt="Multiplataforma">
</p>

O **Archivon** é uma suíte profissional para download massivo, conversão automatizada, higienização profunda de metadados, desduplicação criptográfica e curadoria inteligente de livros e documentos com o **Google Gemini 2.0 Flash & Vision**.

---

## 📥 Downloads Oficiais dos Instaladores

Baixe a versão correspondente ao seu sistema operacional diretamente na [Aba de Releases](https://github.com/alebypegasus/Archivon/releases/latest):

| Sistema Operacional | Formato | Como Instalar |
| :--- | :--- | :--- |
| 🍏 **macOS** (Apple Silicon & Intel) | `Archivon-macOS.dmg` | Abra o `.dmg` e arraste o ícone do **Archivon** para a pasta `Aplicativos`. |
| 🪟 **Windows** (10 & 11) | `Archivon-Windows.exe` | Baixe e execute o arquivo `.exe` diretamente (sem necessidade de instalação). |
| 🐧 **Linux** (Ubuntu, Debian, Fedora) | `Archivon-Linux-x86_64.tar.gz` | Extraia o arquivo `.tar.gz` e execute o binário `./Archivon`. |

---

## 🌟 Principais Recursos e Funcionalidades

### 1. 🏎️ Esteira Automatizada de Downloads (Pipeline Contínuo)
- Suporta links de arquivos individuais ou **pastas inteiras do Google Drive**.
- Interceptação em tempo real: assim que o download de um arquivo termina, ele é enviado imediatamente para a higienização e IA sem esperar o restante da pasta terminar.
- Sistema de **Pausa Atômica e Retomada** que congela todos os processos instantaneamente sem travar o app.
- Suporte a `cookies.txt` para baixar pastas privadas ou com permissão restrita no Google Drive.

### 2. 🧹 Sanitização Profunda de Metadados (PyMuPDF)
- Remove metadados sensíveis embutidos (autor original de criação, software de edição, histórico de revisões e sumários vazados).
- Reescreve o PDF aplicando **Garbage Collection nível 4** e descarte de lixo digital.
- **Compressão Inteligente:** Reduz o tamanho de arquivos pesados aplicando deflação em imagens e fontes sem perda de legibilidade.

### 3. 🔄 Conversor Integrado de Documentos (LibreOffice)
- Detecta e converte apresentações e documentos de texto (`.docx`, `.doc`, `.pptx`, `.ppt`) diretamente para PDF antes da higienização.
- Detecção automática do motor `soffice` no Windows, macOS e Linux, com opção de definir caminho customizado ou versão portátil (Portable).

### 4. 🧠 Curadoria Bibliográfica com IA (Google Gemini 2.0 & Vision)
- **Autodescoberta Inteligente:** Conecta-se automaticamente ao modelo mais rápido disponível na sua conta (`gemini-2.0-flash-lite`, `gemini-2.0-flash`, `gemini-1.5-flash`).
- **Leitura em Múltiplos Pontos:** Analisa capa, folha de rosto, ficha catalográfica e miolo do livro.
- **Formatação Elegante em Title Case:** Corrige digitação e maiúsculas soltas (Ex: transforma `-TEXTOS-DE-MAGIA-` em *Textos de Magia em Papiros Gregos*).
- **Gemini Vision para PDFs Escaneados:** Em livros que são apenas fotos/scanners sem camada de texto OCR, a IA analisa a imagem da capa visualmente para extrair título e autor.
- **Categorização Rigorosa:** Organiza os livros em pastas temáticas (*Bruxaria*, *Ocultismo*, *Magia*, *Maçonaria & Ordens*, *Hermetismo*, *Filosofia*, *Espiritualismo*, etc.).

### 5. 🛡️ Desduplicação Inteligente (Hash SHA-256) & Versionamento
- Calcula a impressão digital criptográfica de cada arquivo limpo.
- Se o mesmo livro já existir na sua biblioteca (mesmo baixado com outro nome), ele descarta a cópia redundante para economizar disco.
- Para obras com edições diferentes e mesmo nome, aplica versionamento inteligente (`V1`, `V2`, `V3`).

### 6. 📚 Biblioteca Viva com Inspeção de Capas em Tempo Real
- **Live Sync:** Atualiza a árvore de livros instantaneamente conforme os downloads são concluídos.
- **Painel de Inspeção:** Selecione qualquer obra para visualizar a miniatura da capa renderizada, contagem de páginas, tamanho e botões de ação rápida (*Abrir no Leitor*, *Revelar no Finder* e *Copiar Caminho*).
- **Busca em Tempo Real:** Filtre instantaneamente todo o acervo por título, autor ou categoria.
- **Exportação de Catálogo:** Gera catálogo completo em página Web HTML estilizada ou planilha CSV com um clique.

### 7. 📊 Tabela Estruturada de Logs & Exportação
- Visualização em tabela com colunas dedicadas: `Horário`, `Fase` (com badges coloridos), `Descrição` e `Detalhes`.
- Filtro por fase (*Sucesso*, *IA Gemini*, *Sanitização*, *Conversão*, *Erros*) e busca interna.
- Duplo clique em qualquer linha de sucesso abre o arquivo PDF gerado imediatamente.
- Botão **Exportar Log** para salvar o histórico de processamento em arquivo `.txt`.

---

## ⚙️ Configuração Inicial Rápida

### 1. Obter a Chave da API do Google Gemini (Gratuito)
1. Acesse o [Google AI Studio](https://aistudio.google.com/).
2. Faça login com sua conta do Google e clique em **Get API key**.
3. Crie uma chave e cole-a no Archivon na aba **Configurações**.
4. Clique em **⚡ Testar Conexão** para validar a chave e carregar os modelos suportados.

### 2. Configurar o LibreOffice (Para conversão de .docx e .pptx)
- **macOS:** Instale via Homebrew com o comando:
  ```bash
  brew install --cask libreoffice
  ```
- **Windows:** Baixe o instalador oficial no [Site do LibreOffice](https://www.libreoffice.org/download/download/) ou use uma versão portátil. O Archivon detecta automaticamente.
- **Linux:** Instale via terminal:
  ```bash
  sudo apt-get install libreoffice
  ```

---

## 💻 Para Desenvolvedores (Execução via Código Fonte)

Se desejar rodar ou compilar o projeto diretamente a partir do código fonte:

```bash
# 1. Clonar o repositório
git clone https://github.com/alebypegasus/Archivon.git
cd Archivon

# 2. Executar no macOS
./run_macos.sh

# 3. Executar no Linux
./run_linux.sh

# 4. Executar no Windows
run_windows.bat
```

### Compilando os Instaladores Localmente:
- **macOS (DMG):** `./build_macos.sh`
- **Windows (EXE):** `build_windows.bat`
- **Linux (Tar.gz):** `./build_linux.sh`

---

## 📄 Licença e Uso
Software desenvolvido para arquivamento, higienização e organização privada de acervos bibliográficos digitais.
