@echo off
echo Iniciando Archivon no Windows...

:: Verifica se o ambiente virtual existe, se nao, cria
if not exist "venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv venv
)

:: Ativa o ambiente virtual
call venv\Scripts\activate.bat

:: Instala/Atualiza dependencias
echo Verificando dependencias...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

:: Executa o aplicativo
echo Iniciando aplicacao...
python archivon_py/main.py
pause
