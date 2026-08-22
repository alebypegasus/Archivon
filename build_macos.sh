#!/bin/bash
# Script de Build do Archivon para macOS (Universal / Nativo)
set -e

ARCH_NAME=$(uname -m)
echo "🔨 Iniciando compilação do Archivon para macOS (Arquitetura: $ARCH_NAME)..."

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install pyinstaller -q

rm -rf build dist

echo "📦 Empacotando com PyInstaller..."
pyinstaller --noconfirm --windowed \
    --name "Archivon" \
    --add-data "archivon_py:archivon_py" \
    --hidden-import "PyQt6.QtSvg" \
    --hidden-import "pymupdf" \
    --hidden-import "google.generativeai" \
    --hidden-import "gdown" \
    archivon_py/main.py

DMG_OUTPUT="dist/Archivon-macOS.dmg"
if [ "$1" != "" ]; then
    DMG_OUTPUT="dist/Archivon-macOS-$1.dmg"
fi

echo "💿 Criando imagem de disco DMG ($DMG_OUTPUT)..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "Archivon" -srcfolder "dist/Archivon.app" -ov -format UDZO "$DMG_OUTPUT"
    echo "✅ DMG criado com sucesso em: $DMG_OUTPUT"
else
    cd dist && zip -r "Archivon-macOS.zip" "Archivon.app" && cd ..
    echo "✅ Zip criado em: dist/Archivon-macOS.zip"
fi

echo "🎉 Build macOS concluído com sucesso!"
