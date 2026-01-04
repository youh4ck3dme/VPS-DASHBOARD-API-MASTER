#!/bin/bash
# Setup script pre CarScraper Pro frontend

set -e

echo "🚀 CarScraper Pro Frontend Setup"
echo "=================================="
echo ""

# Skontroluj Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js nie je nainštalovaný!"
    echo "   Inštaluj: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# Inštaluj závislosti
echo "📦 Inštalujem závislosti..."
npm install

echo ""
echo "✅ Setup dokončený!"
echo ""
echo "Spusti development server:"
echo "  npm run dev"
echo ""
echo "Alebo build pre produkciu:"
echo "  npm run build"

