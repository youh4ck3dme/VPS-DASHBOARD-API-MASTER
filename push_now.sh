#!/bin/bash
# Script na push na GitHub s Personal Access Token

echo "🚀 Push na GitHub: https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER"
echo ""

cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER

# Overenie remote
echo "📋 Remote konfigurácia:"
git remote -v
echo ""

# Overenie branch
echo "🌿 Aktuálny branch:"
git branch
echo ""

# Overenie commitov
echo "📝 Commity na push:"
git log --oneline origin/main..main 2>/dev/null || git log --oneline -5
echo ""

echo "⚠️  Pre push potrebujete Personal Access Token"
echo ""
echo "1. Vytvorte token na: https://github.com/settings/tokens"
echo "2. Generate new token (classic)"
echo "3. Vyberte: repo (full control)"
echo "4. Skopírujte token"
echo ""

read -p "Máte už token? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📝 Vytvorte token a spustite tento script znova."
    echo "   Alebo použite: git push -u origin main"
    exit 0
fi

echo ""
echo "🔐 Pri pushnutí použite:"
echo "   Username: youh4ck3dme"
echo "   Password: (vložte váš Personal Access Token)"
echo ""
echo "📤 Pushujem..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Úspešne pushnuté na GitHub!"
    echo "   https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER"
else
    echo ""
    echo "❌ Push zlyhal. Skontrolujte:"
    echo "   1. Je token správny?"
    echo "   2. Má token oprávnenie 'repo'?"
    echo "   3. Je repozitár vytvorený na GitHub?"
fi

