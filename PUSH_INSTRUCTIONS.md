# Inštrukcie na Push na GitHub

## ✅ Čo je už pripravené:

- ✅ Git repozitár inicializovaný
- ✅ Všetky súbory commitnuté (3 commity)
- ✅ Git konfigurácia nastavená:
  - Username: `youh4ck3dme`
  - Email: `h4ck3d@h4ck3d.me`
- ✅ Remote nastavený: `https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER.git`
- ✅ Branch: `main`

## 📋 Krok 1: Vytvorte repozitár na GitHub

1. Choďte na: **https://github.com/new**
2. Vyplňte:
   - **Repository name:** `VPS-DASHBOARD-API-MASTER`
   - **Description:** `Flask-based VPS Dashboard API with comprehensive testing, CRUD operations, authentication, and payment integration`
   - **Visibility:** Public alebo Private
   - **⚠️ DÔLEŽITÉ:** NEOZAČÍNAJTE s README, .gitignore alebo licenciou! (Už máme)

## 📋 Krok 2: Push na GitHub

### Možnosť A: HTTPS (s Personal Access Token)

```bash
cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER

# Ak ešte nie je nastavený remote
git remote add origin https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER.git

# Push (bude požadovať username a token)
git push -u origin main
```

**Username:** `youh4ck3dme`  
**Password:** Použite **Personal Access Token** (nie heslo!)

**Ako vytvoriť token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Vyberte: `repo` (full control)
4. Skopírujte token a použite ho ako heslo

### Možnosť B: SSH (ak máte SSH kľúče)

```bash
cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER

# Remote je už nastavený na SSH
git push -u origin main
```

**Ako nastaviť SSH kľúče (ak ešte nemáte):**
```bash
# Vygenerujte SSH kľúč
ssh-keygen -t ed25519 -C "h4ck3d@h4ck3d.me"

# Pridajte kľúč do ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Skopírujte verejný kľúč
cat ~/.ssh/id_ed25519.pub

# Pridajte ho na GitHub:
# Settings → SSH and GPG keys → New SSH key
```

### Možnosť C: GitHub CLI (najjednoduchšie)

```bash
# Nainštalujte GitHub CLI (ak ešte nemáte)
brew install gh

# Prihláste sa
gh auth login

# Vytvorte repozitár a pushnite naraz
cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER
gh repo create VPS-DASHBOARD-API-MASTER --public --source=. --remote=origin --push
```

## ✅ Po úspešnom pushnutí

Váš projekt bude dostupný na:
**https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER**

## 🔍 Overenie

```bash
git remote -v
git log --oneline
git status
```

## 📊 Štatistiky projektu

- **62 súborov** v repozitári
- **3 commity**
- **80 testov** (100% úspešnosť)
- **5 kategórií testov**

---

**Poznámka:** Ak máte problémy s autentifikáciou, použite **Personal Access Token** namiesto hesla pri HTTPS push.

