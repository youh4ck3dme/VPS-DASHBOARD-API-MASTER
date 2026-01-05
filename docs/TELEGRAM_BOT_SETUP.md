# 🤖 Telegram Bot Setup - Kompletný Návod

Tento návod ťa prevedie vytvorením Telegram bota pre CarScraper Pro notifikácie.

---

## 📋 Prehľad

Bot bude:

- Posielať **SUPER_DEAL** alerty okamžite
- Posielať **denný digest** o 18:00 s top 5 ponukami
- Umožňovať prepojenie účtu cez `/start` príkaz

---

## Krok 1: Vytvorenie Bota cez @BotFather

### 1.1 Otvor Telegram a nájdi @BotFather

1. Otvor Telegram (mobil alebo desktop)
2. V search bare napíš `@BotFather`
3. Klikni na prvý výsledok (overený s modrým ✓)

### 1.2 Vytvor nového bota

1. Napíš `/newbot`
2. BotFather sa opýta na **názov bota** (display name):

   ```text
   CarScraper Pro Alerts
   ```

3. Potom sa opýta na **username** (musí končiť na `bot`):

   ```text
   carscraper_pro_bot
   ```

   (ak je obsadený, skús: `carscraper_alerts_bot`, `carscraper_sk_bot`, atď.)

### 1.3 Získaj API Token

Po vytvorení dostaneš správu:

```text
Done! Congratulations on your new bot. You will find it at t.me/carscraper_pro_bot.

Use this token to access the HTTP API:
7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**⚠️ DÔLEŽITÉ: Okopíruj si token!** Tento token je tvoj `TELEGRAM_BOT_TOKEN`.

---

## Krok 2: Konfigurácia Bota

### 2.1 Nastav popis a avatar

Stále v @BotFather:

```text
/setdescription
```

Vyber svojho bota a napíš:

```text
🚗 CarScraper Pro - Inteligentné vyhľadávanie najlepších ponúk jazdeniek.

Dostávaj okamžité upozornenia na SUPER DEAL ponuky priamo do Telegramu!
```

```text
/setabouttext
```

```text
CarScraper Pro ti pomáha nájsť najlepšie ponuky jazdeniek. Sleduj najvýhodnejšie autá zo všetkých bazárov.
```

```text
/setuserpic
```

Nahraj obrázok (logo auta, napr. 512x512px PNG)

### 2.2 Nastav príkazy

```text
/setcommands
```

Vyber svojho bota a pošli:

```text
start - Prepoj účet s CarScraper Pro
status - Zobraz stav notifikácií
stop - Zastav notifikácie
help - Zobraz pomoc
```

---

## Krok 3: Získanie Chat ID

Potrebuješ zistiť svoje Chat ID aby ti bot mohol posielať správy.

### Možnosť A: Použij @userinfobot

1. Nájdi `@userinfobot` v Telegrame
2. Napíš `/start`
3. Dostaneš správu s tvojím **ID** (číslo, napr. `123456789`)

### Možnosť B: Použij vlastného bota

1. Napíš svojmu novému botovi správu (čokoľvek)
2. Otvor v browseri:

   ```text
   https://api.telegram.org/bot<TVOJ_TOKEN>/getUpdates
   ```

3. Nájdi v JSON odpovedi `"chat":{"id": 123456789}`

---

## Krok 4: Konfigurácia v Projekte

### 4.1 Uprav `.env` súbor

```bash
nano /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER/.env
```

Pridaj riadky:

```ini
# Telegram Notifikácie
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
TELEGRAM_ADMIN_CHAT_ID=123456789
```

### 4.2 Nainštaluj knižnicu

```bash
cd /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER
source venv/bin/activate
pip install python-telegram-bot==20.7
```

### 4.3 Aktualizuj requirements.txt

```bash
echo "python-telegram-bot==20.7" >> requirements.txt
```

---

## Krok 5: Test Notifikácie

Vytvor testovací skript:

```python
# test_telegram.py
import asyncio
from telegram import Bot

TOKEN = "7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"  # Tvoj token
CHAT_ID = "123456789"  # Tvoje chat ID

async def send_test():
    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🚗 *Test CarScraper Pro*\n\nNotifikácie fungujú! ✅",
        parse_mode='Markdown'
    )
    print("✅ Správa odoslaná!")

asyncio.run(send_test())
```

Spusti:

```bash
python test_telegram.py
```

Ak dostaneš správu v Telegrame, všetko funguje! 🎉

---

## Krok 6: Integrácia do CarScraper

### 6.1 Automatické SUPER_DEAL alerty

V `app/blueprints/carscraper/routes.py` po uložení deals:

```python
from app.blueprints.carscraper.notifications import send_deal_notification

# Po uložení deals:
for deal in saved_deals:
    if deal.verdict == 'SUPER_DEAL':
        send_deal_notification(
            deal.to_dict(), 
            current_user.telegram_chat_id
        )
```

### 6.2 Denný Digest (Cron Job)

Vytvor `scripts/telegram_digest.py`:

```python
#!/usr/bin/env python3
"""Denný digest - spúšťaj cez cron o 18:00"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import CarDeal, User
from app.blueprints.carscraper.notifications import send_digest

app = create_app()

with app.app_context():
    # Nájdi všetkých používateľov s Telegram
    users = User.query.filter(User.telegram_chat_id.isnot(None)).all()
    
    for user in users:
        # Top 5 deals za posledných 24h
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        deals = CarDeal.query.filter(
            CarDeal.created_at >= yesterday,
            CarDeal.verdict.in_(['SUPER_DEAL', 'GOOD_DEAL'])
        ).order_by(CarDeal.score.desc()).limit(5).all()
        
        if deals:
            send_digest(
                [d.to_dict() for d in deals],
                user.telegram_chat_id
            )
            print(f"✅ Digest odoslaný pre {user.username}")

print("Done!")
```

### 6.3 Cron Job pre Digest

```bash
crontab -e
```

Pridaj:

```cron
# Telegram digest každý deň o 18:00
0 18 * * * /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER/venv/bin/python /Users/youh4ck3dme/projekty-pwa/VPS-DASHBOARD-API-MASTER/scripts/telegram_digest.py
```

---

## Krok 7: Prepojenie Účtov Používateľov

### 7.1 Endpoint pre prepojenie

V `app/blueprints/carscraper/routes.py`:

```python
@carscraper_bp.route('/api/telegram/link', methods=['POST'])
@login_required
def link_telegram():
    """Vygeneruje link pre prepojenie Telegram účtu"""
    from app.extensions import db
    import secrets
    
    # Vygeneruj jednorazový token
    link_token = secrets.token_urlsafe(32)
    
    # Ulož do Redis (platný 10 minút)
    if redis_client:
        redis_client.setex(f"telegram_link:{link_token}", 600, current_user.id)
    
    bot_username = "carscraper_pro_bot"  # Tvoj bot
    deep_link = f"https://t.me/{bot_username}?start={link_token}"
    
    return jsonify({
        'link': deep_link,
        'expires_in': 600
    })
```

### 7.2 Webhook pre bot

Bot príjme `/start {token}` a prepojí účet:

```python
# V samostatnom bot serveri alebo webhook
async def handle_start(update, context):
    token = context.args[0] if context.args else None
    
    if token and redis_client:
        user_id = redis_client.get(f"telegram_link:{token}")
        if user_id:
            # Prepoj účet
            user = User.query.get(int(user_id))
            user.telegram_chat_id = str(update.effective_chat.id)
            db.session.commit()
            
            await update.message.reply_text(
                f"✅ Účet prepojený!\n\n"
                f"Budeš dostávať notifikácie o SUPER DEAL ponukách."
            )
            redis_client.delete(f"telegram_link:{token}")
            return
    
    await update.message.reply_text(
        "👋 Vitaj v CarScraper Pro!\n\n"
        "Pre prepojenie účtu použi link z webovej aplikácie."
    )
```

---

## 📋 Checklist

- [ ] Vytvorený bot cez @BotFather
- [ ] Uložený TOKEN do `.env`
- [ ] Získané Chat ID
- [ ] Nainštalovaný `python-telegram-bot`
- [ ] Otestovaná notifikácia
- [ ] Nastavený cron job pre digest

---

## 🔒 Bezpečnostné Tipy

1. **Nikdy nedávaj TOKEN do git** - už máš v `.gitignore`
2. **Používaj webhook** namiesto polling v produkcii
3. **Rate limiting** - Telegram má limit 30 správ/sekundu
4. **Error handling** - vždy ošetri chyby pri posielaní

---

## 📞 Troubleshooting

### "Unauthorized" chyba

- Skontroluj, či je token správny
- Token sa mení ak ho resetuješ v @BotFather

### Správa nepríde

- Napíš botovi `/start` pred prvou správou
- Skontroluj Chat ID

### Rate limit

- Nepošli viac ako 30 správ za sekundu
- Použi `asyncio.sleep(0.05)` medzi správami

---

**Hotovo!** 🎉 Tvoj Telegram bot je pripravený na notifikácie.
