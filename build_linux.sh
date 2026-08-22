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
    --hidden-import "PyQt6.QtSvg" \
    --hidden-import "pymupdf" \
    --hidden-import "google.generativeai" \
    --hidden-import "gdown" \
    archivon_py/main.py

cd dist
tar -czvf "Archivon-Linux-x86_64.tar.gz" "Archivon"
cd ..

echo "🎉 Build Linux concluído: dist/Archivon-Linux-x86_64.tar.gz"
