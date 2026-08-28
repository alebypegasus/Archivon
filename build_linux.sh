#!/bin/bash
# Script de Build do Archivon para Linux (Binário Standalone)
set -e

echo "🐧 Iniciando compilação do Archivon para Linux..."

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install pyinstaller -q

rm -rf build dist

pyinstaller --noconfirm --windowed --onefile \
    --name "Archivon" \
    --add-data "archivon_py:archivon_py" \
    --add-data "assets:assets" \
    --hidden-import "PyQt6.QtSvg" \
    --hidden-import "PyQt6.QtCore" \
    --hidden-import "PyQt6.QtGui" \
    --hidden-import "PyQt6.QtWidgets" \
    --collect-all "google.generativeai" \
    --collect-all "google.ai.generativelanguage" \
    --collect-all "google.api_core" \
    --collect-all "pymupdf" \
    --collect-all "fitz" \
    --collect-all "gdown" \
    --copy-metadata "google-generativeai" \
    --copy-metadata "google-ai-generativelanguage" \
    --copy-metadata "pymupdf" \
    --copy-metadata "gdown" \
    archivon_py/main.py

cd dist
tar -czvf "Archivon-Linux-x86_64.tar.gz" "Archivon"
cd ..

echo "🎉 Build Linux concluído: dist/Archivon-Linux-x86_64.tar.gz"
