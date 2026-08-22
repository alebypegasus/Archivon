# ⚡ ARCHIVON — Gestor de Acervos, Sanitizador de PDFs & Curadoria com IA

<p align="center">
  <img src="https://img.shields.io/badge/Versão-3.5.0-6366F1?style=for-the-badge" alt="Versão 3.5.0">
  <img src="https://img.shields.io/badge/Gemini-2.0%20Flash%20%7C%20Vision-F59E0B?style=for-the-badge" alt="Gemini AI">
  <img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20%26%20Intel-10B981?style=for-the-badge" alt="macOS Universal">
  <img src="https://img.shields.io/badge/Plataformas-macOS%20%7C%20Windows%20%7C%20Linux-38BDF8?style=for-the-badge" alt="Multiplataforma">
</p>

O **Archivon** é um aplicativo desktop autônomo para download massivo, conversão automatizada, higienização profunda de metadados, desduplicação criptográfica e curadoria inteligente de livros e documentos com o **Google Gemini 2.0 Flash & Vision**.

---

## 📥 Como Baixar e Instalar

Não é necessário instalar Python ou clonar código. Basta baixar o instalador pronto para o seu sistema:

👉 **[Clique aqui para acessar a Página Oficial de Releases](https://github.com/alebypegasus/Archivon/releases/latest)**

### 📦 Escolha o seu Sistema:

| Sistema Operacional | Arquitetura | Arquivo de Download | Instruções de Instalação |
| :--- | :--- | :--- | :--- |
| 🍏 **macOS (Apple Silicon)** | **M1, M2, M3, M4** | [**`Archivon-macOS-AppleSilicon.dmg`**](https://github.com/alebypegasus/Archivon/releases/download/v3.5.0/Archivon-macOS-AppleSilicon-M1-M2-M3.dmg) | Abra o `.dmg` e arraste o **Archivon** para a pasta **Aplicativos**. |
| 🍏 **macOS (Intel)** | **Processadores Intel (Core i5/i7/i9)** | [**`Archivon-macOS-Intel.dmg`**](https://github.com/alebypegasus/Archivon/releases/download/v3.5.0/Archivon-macOS-Intel.dmg) | Abra o `.dmg` e arraste o **Archivon** para a pasta **Aplicativos**. |
| 🪟 **Windows** | **64-bit (Windows 10 / 11)** | [**`Archivon-Windows.exe`**](https://github.com/alebypegasus/Archivon/releases/download/v3.5.0/Archivon-Windows.exe) | Dê dois cliques no executável para abrir o aplicativo diretamente. |
| 🐧 **Linux** | **x86_64 (Ubuntu, Debian, Fedora)** | [**`Archivon-Linux-x86_64.tar.gz`**](https://github.com/alebypegasus/Archivon/releases/download/v3.5.0/Archivon-Linux-x86_64.tar.gz) | Extraia o arquivo e execute o binário `Archivon`. |

---

## 🚀 Como Usar o Aplicativo

### 1. Configuração Inicial (Apenas na 1ª vez)
1. Abra o **Archivon** e vá na aba **Configurações**.
2. **Chave de IA (Gratuita):** Obtenha uma chave no [Google AI Studio](https://aistudio.google.com/) e cole no campo *Google Gemini API Key*. Clique em **Testar Conexão**.
3. **Pasta de Destino:** Escolha a pasta onde você deseja que seus livros organizados e higienizados sejam salvos (Padrão: pasta `Biblioteca`).
4. Clique em **Salvar Configurações**.

### 2. Baixando e Organizando Acervos
1. Acesse a aba **Downloads**.
2. Cole os links de arquivos ou **pastas do Google Drive** no campo de texto.
3. Clique em **Iniciar Processamento**.
4. O Archivon cuidará de todo o fluxo automaticamente:
   - Baixa os arquivos.
   - Converte apresentações Word e PowerPoint (`.docx`, `.pptx`) para PDF.
   - Remove metadados ocultos e sensíveis.
   - Analisa o livro com a IA Gemini (inclusive capas de livros escaneados por foto).
   - Descarta duplicatas exatas via Hash criptográfico.
   - Salva os livros renomeados e organizados nas pastas temáticas (*Bruxaria*, *Ocultismo*, *Magia*, *Maçonaria*, *Filosofia*, etc.).

### 3. Consultando a Biblioteca
1. Acesse a aba **Biblioteca** para ver suas obras organizadas em tempo real.
2. Clique em qualquer livro para inspecionar a **capa**, contagem de páginas e tamanho.
3. Use a barra de pesquisa para encontrar títulos instantaneamente.
4. Clique em **Exportar Catálogo** para gerar uma lista de todas as suas obras em formato HTML ou planilha CSV.

---

## 🌟 Recursos em Destaque
* 🧠 **Curadoria Inteligente:** Títulos corrigidos em Title Case elegante e autores identificados.
* 👁️ **Gemini Vision:** Lê capas de livros escaneados antigos mesmo sem texto selecionável.
* 🧹 **Sanitização PyMuPDF:** Remoção de sumários vazados, metadados de criação e histórico.
* 🛡️ **Desduplicação SHA-256:** Economiza espaço descartando cópias idênticas.
* ⏸️ **Pausa e Retomada Instantânea:** Controle total da fila de downloads.
* 📊 **Tabela de Logs Interativa:** Histórico claro com filtros por fase e exportação em `.txt`.
