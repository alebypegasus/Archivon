@echo off
REM Script de Build do Archivon para Windows (Executável Standalone)
echo Iniciando compilacao do Archivon para Windows...

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

pip install pyinstaller -q

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Empacotando com PyInstaller...
pyinstaller --noconfirm --windowed --onefile ^
    --name "Archivon" ^
    --add-data "archivon_py;archivon_py" ^
    --hidden-import "PyQt6.QtSvg" ^
    --hidden-import "pymupdf" ^
    --hidden-import "google.generativeai" ^
    --hidden-import "gdown" ^
    archivon_py\main.py

echo Build concluido com sucesso! O executavel esta em: dist\Archivon.exe
pause
