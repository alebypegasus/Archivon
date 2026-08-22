#!/bin/bash
# Script de Execução para macOS

echo "Iniciando Archivon no macOS..."

# Verifica se o ambiente virtual existe, se não, cria
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Instala/Atualiza dependências
echo "Verificando dependências..."
pip install -r requirements.txt -q

# Executa o aplicativo
echo "Iniciando aplicação..."
python archivon_py/main.py
