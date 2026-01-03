#!/bin/bash
# Rýchly push na GitHub - nahraďte YOUR_USERNAME a REPO_NAME

GITHUB_USERNAME="${1:-YOUR_USERNAME}"
REPO_NAME="${2:-VPS-DASHBOARD-API-MASTER}"

echo "🚀 Pridávam projekt na GitHub..."
echo "Username: $GITHUB_USERNAME"
echo "Repozitár: $REPO_NAME"
echo ""

cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER

# Odstránenie existujúceho remote (ak existuje)
git remote remove origin 2>/dev/null || true

# Pridanie remote
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Nastavenie branch
git branch -M main

# Push
echo "📤 Pushujem na GitHub..."
git push -u origin main

echo ""
echo "✅ Hotovo! Projekt je na:"
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"

