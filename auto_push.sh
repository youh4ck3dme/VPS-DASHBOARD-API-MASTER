#!/bin/bash
# Automatický push na GitHub pomocou GitHub CLI

set -e

cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER

echo "🚀 Automatický push na GitHub..."
echo ""

# Kontrola GitHub CLI
if ! command -v gh >/dev/null 2>&1; then
    echo "❌ GitHub CLI nie je nainštalovaný"
    echo ""
    echo "📦 Inštalácia GitHub CLI:"
    echo "   brew install gh"
    echo ""
    echo "🔐 Po inštalácii:"
    echo "   gh auth login"
    echo ""
    exit 1
fi

# Kontrola prihlásenia
if ! gh auth status >/dev/null 2>&1; then
    echo "⚠️  Nie ste prihlásený do GitHub CLI"
    echo ""
    echo "🔐 Prihláste sa:"
    echo "   gh auth login"
    echo ""
    echo "   Vyberte:"
    echo "   - GitHub.com"
    echo "   - HTTPS"
    echo "   - Login with a web browser"
    echo ""
    exit 1
fi

echo "✅ GitHub CLI je pripravený"
echo ""

# Kontrola, či repozitár už existuje
if gh repo view youh4ck3dme/VPS-DASHBOARD-API-MASTER >/dev/null 2>&1; then
    echo "✅ Repozitár už existuje na GitHub"
    echo "📤 Pushujem zmeny..."
    git push -u origin main
else
    echo "📦 Vytváram repozitár a pushujem..."
    gh repo create VPS-DASHBOARD-API-MASTER --public --source=. --remote=origin --push
fi

echo ""
echo "✅ Hotovo! Projekt je na:"
echo "   https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER"

