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

ICON_FLAG=""
if [ -f "assets/icon.icns" ]; then
    ICON_FLAG="--icon assets/icon.icns"
fi

echo "📦 Empacotando com PyInstaller..."
pyinstaller --noconfirm --windowed $ICON_FLAG \
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
