# Rýchly štart - Lokálne testovanie

Tento návod je pre rýchle spustenie aplikácie na tvojom lokálnom počítači (nie na VPS).

## Prerekvizity

- Python 3.8+
- MySQL alebo MariaDB
- Redis (voliteľné, aplikácia beží aj bez neho)

## Kroky

### 1. Vytvor virtuálne prostredie

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# alebo
venv\Scripts\activate  # Windows
```

### 2. Nainštaluj závislosti

```bash
pip install -r requirements.txt
```

### 3. Nastav .env súbor

```bash
cp .env.example .env
```

Minimálna konfigurácia pre lokálne testovanie:

```ini
SECRET_KEY=dev_secret_key_123
DATABASE_URL=mysql://root:@localhost/api_dashboard
```

### 4. Vytvor databázu

```bash
# Prihlás sa do MySQL
mysql -u root -p

# Vytvor databázu
CREATE DATABASE api_dashboard;
EXIT;
```

### 5. Načítaj schému databázy

```bash
mysql -u root -p api_dashboard < database/init_db.sql
```

### 6. Spusti aplikáciu

```bash
python3 app.py
```

### 7. Otvor prehliadač

Prejdi na `http://localhost:6002` (alebo port z .env súboru)

**Prihlásenie:**
- **URL**: `http://localhost:6002/login`
- **Užívateľské meno**: `admin`
- **Heslo**: `admin123`

⚠️ **Zmeň heslo po prvom prihlásení!**

## Poznámky

- **Redis**: Ak nemáš Redis, aplikácia bude fungovať, ale môžu sa zobrazovať varovania
- **Stripe**: Pre testovanie platieb potrebuješ test API kľúče z https://dashboard.stripe.com/test/apikeys
- **OpenAI**: Pre AI funkcie potrebuješ API kľúč z https://platform.openai.com/api-keys

## Vývojársky režim

Aplikácia beží v debug režime, takže zmeny v kóde sa automaticky načítajú.

## Zastavenie aplikácie

Stlač `Ctrl+C` v termináli.

---

**Poznámka:** Pre produkčné nasadenie na VPS postupuj podľa hlavného [README.md](README.md)
