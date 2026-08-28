#!/bin/bash
# Script de Build do Archivon para macOS (Universal / Nativo)
set -e

TARGET_ARCH=""
DMG_SUFFIX=""

if [ "$1" = "Intel" ] || [ "$1" = "x86_64" ]; then
    TARGET_ARCH="--target-arch x86_64"
    DMG_SUFFIX="-Intel"
elif [ "$1" = "AppleSilicon" ] || [ "$1" = "arm64" ]; then
    TARGET_ARCH="--target-arch arm64"
    DMG_SUFFIX="-AppleSilicon"
elif [ "$1" = "Universal" ] || [ "$1" = "universal2" ]; then
    TARGET_ARCH="--target-arch universal2"
    DMG_SUFFIX="-Universal"
elif [ -n "$1" ]; then
    DMG_SUFFIX="-$1"
else
    CURRENT_ARCH=$(uname -m)
    if [ "$CURRENT_ARCH" = "x86_64" ]; then
        TARGET_ARCH="--target-arch x86_64"
        DMG_SUFFIX="-Intel"
    else
        TARGET_ARCH="--target-arch arm64"
        DMG_SUFFIX="-AppleSilicon"
    fi
fi

echo "🔨 Iniciando compilação do Archivon para macOS (Target: $TARGET_ARCH)..."

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install pyinstaller -q

rm -rf build dist

ICON_FLAG=""
if [ -f "assets/icon.icns" ]; then
    ICON_FLAG="--icon assets/icon.icns"
fi

echo "📦 Empacotando com PyInstaller ($TARGET_ARCH)..."
pyinstaller --noconfirm --windowed $ICON_FLAG $TARGET_ARCH \
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

DMG_OUTPUT="dist/Archivon-macOS${DMG_SUFFIX}.dmg"

echo "💿 Criando imagem de disco DMG ($DMG_OUTPUT)..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "Archivon" -srcfolder "dist/Archivon.app" -ov -format UDZO "$DMG_OUTPUT"
    echo "✅ DMG criado com sucesso em: $DMG_OUTPUT"
else
    cd dist && zip -r "Archivon-macOS.zip" "Archivon.app" && cd ..
    echo "✅ Zip criado em: dist/Archivon-macOS.zip"
fi

echo "🎉 Build macOS concluído com sucesso!"
