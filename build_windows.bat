@echo off
REM Script de Build do Archivon para Windows (Executavel Standalone)
echo Iniciando compilacao do Archivon para Windows...

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

pip install pyinstaller -q

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

set ICON_FLAG=
if exist assets\icon.ico (
    set ICON_FLAG=--icon assets\icon.ico
) else if exist assets\icon.png (
    set ICON_FLAG=--icon assets\icon.png
)

echo Empacotando com PyInstaller...
pyinstaller --noconfirm --windowed --onefile %ICON_FLAG% ^
    --name "Archivon" ^
    --add-data "archivon_py;archivon_py" ^
    --add-data "assets;assets" ^
    --hidden-import "PyQt6.QtSvg" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --collect-all "google.generativeai" ^
    --collect-all "google.ai.generativelanguage" ^
    --collect-all "google.api_core" ^
    --collect-all "pymupdf" ^
    --collect-all "fitz" ^
    --collect-all "gdown" ^
    --copy-metadata "google-generativeai" ^
    --copy-metadata "google-ai-generativelanguage" ^
    --copy-metadata "pymupdf" ^
    --copy-metadata "gdown" ^
    archivon_py\main.py

echo Build concluido com sucesso! O executavel esta em: dist\Archivon.exe
pause
