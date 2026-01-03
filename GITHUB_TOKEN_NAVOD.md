# 📝 Presný Návod: Vytvorenie GitHub Personal Access Token

## 🎯 Účel
Personal Access Token je potrebný na push kódu na GitHub pomocou HTTPS (namiesto hesla).

---

## 📋 Krok za krokom

### **KROK 1: Otvorte GitHub Settings**

1. Prihláste sa na **https://github.com**
2. Kliknite na váš **profilový obrázok** (vpravo hore)
3. Z rozbalovacieho menu vyberte **"Settings"**

   ```
   [Váš profil] ▼
   ├── Your profile
   ├── Your organizations
   ├── Your projects
   ├── Settings  ← KLIKNITE TU
   └── Sign out
   ```

### **KROK 2: Otvorte Developer Settings**

1. V ľavom bočnom menu (Settings) prejdite na koniec
2. Kliknite na **"Developer settings"**

   ```
   Settings
   ├── Profile
   ├── Account
   ├── ...
   └── Developer settings  ← KLIKNITE TU
   ```

### **KROK 3: Otvorte Personal Access Tokens**

1. V ľavom menu kliknite na **"Personal access tokens"**
2. Vyberte **"Tokens (classic)"**

   ```
   Developer settings
   ├── Personal access tokens  ← KLIKNITE TU
   │   ├── Tokens (classic)  ← VYBERTE TÚTO
   │   └── Fine-grained tokens
   └── ...
   ```

### **KROK 4: Vytvorte nový token**

1. Kliknite na tlačidlo **"Generate new token"**
2. Vyberte **"Generate new token (classic)"**

   ⚠️ **NEPOUŽÍVAJTE** "Generate new token (fine-grained)" - ten má iné nastavenia!

### **KROK 5: Vyplňte formulár**

Vyplňte nasledujúce polia:

#### **Note (Názov tokenu):**
```
VPS Dashboard API Push
```
alebo akýkoľvek iný popisný názov

#### **Expiration (Platnosť):**
- Vyberte podľa potreby:
  - **30 days** - pre testovanie
  - **90 days** - pre strednodobé použitie
  - **No expiration** - pre dlhodobé použitie (menej bezpečné)

#### **Select scopes (Vyberte oprávnenia):**

✅ **POVINNÉ:** Zaškrtnite **`repo`**

```
☑️ repo
   ├── repo:status
   ├── repo_deployment
   ├── public_repo
   └── repo:invite
```

**Čo znamená `repo`:**
- Full control of private repositories
- Úplná kontrola nad vašimi repozitármi
- Umožňuje push, pull, clone, atď.

**Ostatné oprávnenia NIE SÚ potrebné** pre základný push.

### **KROK 6: Vygenerujte token**

1. Prejdite na koniec stránky
2. Kliknite na tlačidlo **"Generate token"** (zelené tlačidlo)

### **KROK 7: Skopírujte token**

⚠️ **DÔLEŽITÉ:** Token sa zobrazí **LEN RAZ**!

1. Zobrazí sa stránka s vaším tokenom
2. Token vyzerá takto:
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. **IHNEĎ SKOPÍRUJTE** token (celý text)
4. Uložte ho na bezpečné miesto

   💡 **Tip:** Môžete ho uložiť do poznámok alebo password manageru

---

## 🚀 Použitie tokenu

### **Pri pushnutí na GitHub:**

Keď spustíte:
```bash
git push -u origin main
```

Git vás požiada o:
- **Username:** `youh4ck3dme`
- **Password:** **VLOŽTE VÁŠ TOKEN** (nie heslo!)

### **Príklad:**

```
Username for 'https://github.com': youh4ck3dme
Password for 'https://youh4ck3dme@github.com': ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔒 Bezpečnosť

### **Dobré praktiky:**

1. ✅ **Nezdieľajte token** s nikým
2. ✅ **Nekomitujte token** do git repozitára
3. ✅ **Použite token len na potrebné repozitáre**
4. ✅ **Pravidelne rotujte tokeny** (vytvárajte nové)
5. ✅ **Zmažte token**, ak ho už nepotrebujete

### **Ak token unikne:**

1. Choďte na: https://github.com/settings/tokens
2. Nájdite token v zozname
3. Kliknite na **"Revoke"** (Zrušiť)
4. Vytvorte nový token

---

## 📱 Alternatíva: GitHub CLI

Ak chcete jednoduchšie riešenie, môžete použiť GitHub CLI:

```bash
# Nainštalujte GitHub CLI
brew install gh

# Prihláste sa
gh auth login

# Vytvorte repozitár a pushnite naraz
gh repo create VPS-DASHBOARD-API-MASTER --public --source=. --remote=origin --push
```

---

## ❓ Časté otázky

### **Q: Prečo nemôžem použiť svoje heslo?**
A: GitHub už nepodporuje push cez HTTPS s heslom. Musíte použiť Personal Access Token.

### **Q: Môžem použiť ten istý token viackrát?**
A: Áno, token môžete použiť opakovane, kým nevyprší alebo ho nezrušíte.

### **Q: Ako dlho token platí?**
A: Podľa toho, čo ste nastavili pri vytváraní (30 dní, 90 dní, alebo bez obmedzenia).

### **Q: Čo ak zabudnem token?**
A: Musíte vytvoriť nový token. Starý token sa nedá znovu zobraziť.

### **Q: Môžem mať viacero tokenov?**
A: Áno, môžete mať viacero tokenov pre rôzne účely.

---

## ✅ Kontrolný zoznam

- [ ] Prihlásený na GitHub
- [ ] Otvorené Settings → Developer settings → Personal access tokens → Tokens (classic)
- [ ] Kliknuté na "Generate new token (classic)"
- [ ] Vyplnený názov tokenu
- [ ] Nastavená platnosť
- [ ] Zaškrtnuté oprávnenie `repo`
- [ ] Kliknuté na "Generate token"
- [ ] **SKOPÍROVANÝ token** (dôležité!)
- [ ] Token uložený na bezpečnom mieste

---

## 🎯 Po vytvorení tokenu

Spustite push:

```bash
cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER
git push -u origin main
```

Pri výzve:
- **Username:** `youh4ck3dme`
- **Password:** vložte váš token

---

**Hotovo! 🎉**

Váš projekt bude na: https://github.com/youh4ck3dme/VPS-DASHBOARD-API-MASTER

