#!/bin/bash
# Script de Build do Archivon para macOS (Standalone App + DMG)
set -e

echo "🔨 Iniciando compilação do Archivon para macOS..."

# Ativa venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instala pyinstaller se necessário
pip install pyinstaller -q

# Limpa builds anteriores
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

echo "💿 Criando imagem de disco DMG..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "Archivon" -srcfolder "dist/Archivon.app" -ov -format UDZO "dist/Archivon-macOS.dmg"
    echo "✅ DMG criado com sucesso em: dist/Archivon-macOS.dmg"
else
    cd dist && zip -r "Archivon-macOS.zip" "Archivon.app" && cd ..
    echo "✅ Zip criado em: dist/Archivon-macOS.zip"
fi

echo "🎉 Build concluído com sucesso!"
