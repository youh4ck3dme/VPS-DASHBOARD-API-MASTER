#!/bin/bash

# Script na pridanie projektu na GitHub
# Použitie: ./push_to_github.sh

set -e

echo "🚀 Pridanie projektu na GitHub"
echo ""

# Kontrola, či sme v správnom adresári
if [ ! -d ".git" ]; then
    echo "❌ Chyba: Nie ste v git repozitári!"
    exit 1
fi

# Kontrola, či už existuje remote
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  Remote 'origin' už existuje:"
    git remote get-url origin
    read -p "Chcete ho prepísať? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Zrušené."
        exit 0
    fi
    git remote remove origin
fi

# Získanie údajov od používateľa
read -p "Zadajte váš GitHub username: " GITHUB_USERNAME
read -p "Zadajte názov repozitára (alebo stlačte Enter pre 'VPS-DASHBOARD-API-MASTER'): " REPO_NAME

# Predvolený názov repozitára
REPO_NAME=${REPO_NAME:-VPS-DASHBOARD-API-MASTER}

echo ""
echo "📋 Konfigurácia:"
echo "   Username: $GITHUB_USERNAME"
echo "   Repozitár: $REPO_NAME"
echo ""

read -p "Pokračovať? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Zrušené."
    exit 0
fi

# Pridanie remote
echo ""
echo "🔗 Pridávam remote..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" || {
    echo "❌ Chyba pri pridávaní remote. Možno už existuje?"
    exit 1
}

# Nastavenie branch na main
echo "🌿 Nastavujem branch na main..."
git branch -M main

# Push na GitHub
echo ""
echo "📤 Pushujem na GitHub..."
echo "   (Ak repozitár ešte neexistuje, vytvorte ho najprv na https://github.com/new)"
echo ""

read -p "Je repozitár už vytvorený na GitHub? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📝 Vytvorte repozitár na: https://github.com/new"
    echo "   Názov: $REPO_NAME"
    echo "   NEOZAČÍNAJTE s README, .gitignore alebo licenciou!"
    echo ""
    read -p "Stlačte Enter keď bude repozitár vytvorený..."
fi

echo ""
echo "🚀 Pushujem..."
git push -u origin main

echo ""
echo "✅ Hotovo! Projekt je na GitHub:"
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

