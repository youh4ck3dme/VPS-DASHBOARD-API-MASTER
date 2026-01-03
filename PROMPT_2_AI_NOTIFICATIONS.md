# 🤖 PROMPT 2: AI Analýza a Notifikácie

## Úloha
Implementuj skutočnú OpenAI analýzu pre CarScraper Pro a systém notifikácií.

## Čo treba implementovať:

### 1. SKUTOČNÁ OPENAI ANALÝZA
**Problém**: Aktuálne používa fallback matematiku (cena * 1.15), nie skutočnú AI.

**Riešenie**:
- Uprav `scripts/car_scraper.py` funkciu `analyze_with_ai()`:
  - Skontroluj, či `app.config['OPENAI_API_KEY']` existuje
  - Ak áno, použij OpenAI API:
    ```python
    from openai import OpenAI
    client = OpenAI(api_key=app.config['OPENAI_API_KEY'])
    
    prompt = f"""
    Si expert na obchodovanie s autami na slovenskom trhu.
    Analyzuj tento inzerát:
    
    Auto: {car_data['title']}
    Cena: {car_data['price']} EUR
    Popis: {car_data['description']}
    
    Tvoja úloha:
    1. Odhadni reálnu trhovú cenu tohto auta (v EUR)
    2. Rozhodni verdikt: "KÚPIŤ" (ak je cena o 15%+ nižšia), "RIZIKO" (5-15%), "NEKUPOVAŤ" (menej ako 5%)
    3. Urči risk_level: "Nízke", "Stredné", "Vysoké"
    4. Napíš krátke vysvetlenie (max 2 vety)
    
    Vráť odpoveď len v JSON formáte (bez markdown):
    {{
        "odhad_ceny_cislo": <číslo>,
        "verdikt": "KÚPIŤ|RIZIKO|NEKUPOVAŤ",
        "risk_level": "Nízke|Stredné|Vysoké",
        "dovod_skratene": "<vysvetlenie>"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # alebo gpt-3.5-turbo pre nižšie náklady
        messages=[
            {"role": "system", "content": "Si expert na autá. Vždy vráť validný JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},  # Vynúti JSON výstup
        temperature=0.3,  # Nižšia teplota = konzistentnejšie výsledky
        max_tokens=300
    )
    
    # Parsuj JSON odpoveď
    import json
    analysis = json.loads(response.choices[0].message.content)
    ```
  - Ak OpenAI nie je dostupné, použij fallback (súčasný kód)
  - Error handling: ak OpenAI zlyhá, použij fallback
  - Loguj všetky OpenAI volania (pre debugging a cost tracking)

### 2. EMAIL NOTIFIKÁCIE
**Problém**: Žiadne upozornenia na nové "KÚPIŤ" deals.

**Riešenie**:
- Vytvor nový modul `utils/notifications.py`:
  ```python
  from flask_mail import Mail, Message
  from app import app
  
  mail = Mail(app)
  
  def send_deal_notification(user_email, deal):
      """Pošle email notifikáciu o novom super deale"""
      msg = Message(
          subject=f"🚗 Nový super deal: {deal['title']}",
          recipients=[user_email],
          html=f"""
          <h2>Našiel sa nový super deal!</h2>
          <p><strong>{deal['title']}</strong></p>
          <p>Cena: {deal['price']} EUR</p>
          <p>Trhová hodnota: {deal['market_value']} EUR</p>
          <p>Potenciálny zisk: {deal['profit']} EUR</p>
          <p>Verdikt: {deal['verdict']}</p>
          <p><a href="{deal['link']}">Otvoriť inzerát</a></p>
          """
      )
      mail.send(msg)
  ```
- V `scripts/car_scraper.py` v `save_deals_to_db()`:
  - Po uložení deal s `verdict='KÚPIŤ'`
  - Získaj email používateľa z projektu
  - Zavolaj `send_deal_notification()`
  - Loguj odoslanie emailu
- Pridaj do `requirements.txt`: `flask-mail==0.9.1`
- Pridaj do `.env.example`:
  ```
  MAIL_SERVER=smtp.gmail.com
  MAIL_PORT=587
  MAIL_USE_TLS=True
  MAIL_USERNAME=your_email@gmail.com
  MAIL_PASSWORD=your_app_password
  ```

### 3. TELEGRAM NOTIFIKÁCIE (voliteľné, ale odporúčané)
**Problém**: Email môže byť pomalý, Telegram je instantný.

**Riešenie**:
- Vytvor funkciu v `utils/notifications.py`:
  ```python
  import requests
  
  def send_telegram_notification(chat_id, bot_token, deal):
      """Pošle Telegram notifikáciu"""
      url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
      message = f"""
  🚗 *NOVÝ SUPER DEAL!*
  
  *{deal['title']}*
  
  💰 Cena: {deal['price']} EUR
  📊 Trhová hodnota: {deal['market_value']} EUR
  💵 Zisk: {deal['profit']} EUR
  
  ✅ Verdict: {deal['verdict']}
  📝 {deal['reason']}
  
  [Otvoriť inzerát]({deal['link']})
  """
      requests.post(url, json={
          "chat_id": chat_id,
          "text": message,
          "parse_mode": "Markdown"
      })
  ```
- Pridaj do `config.py`:
  ```python
  TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
  TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
  ```
- V `save_deals_to_db()` pridaj volanie Telegram notifikácie
- Pridaj do `.env.example`:
  ```
  TELEGRAM_BOT_TOKEN=your_bot_token
  TELEGRAM_CHAT_ID=your_chat_id
  ```

### 4. DASHBOARD NOTIFICATIONS
**Problém**: Používateľ nevidí nové deals v dashboarde.

**Riešenie**:
- Vytvor nový model `Notification` v `app.py`:
  ```python
  class Notification(db.Model):
      __tablename__ = 'notifications'
      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
      deal_id = db.Column(db.Integer, db.ForeignKey('car_deals.id'), nullable=True)
      message = db.Column(db.String(200), nullable=False)
      is_read = db.Column(db.Boolean, default=False)
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
  ```
- V `save_deals_to_db()` vytvor Notification pre každý "KÚPIŤ" deal
- V `dashboard()` route:
  - Získaj neprečítané notifikácie
  - Pridaj do template context
- V `dashboard.html`:
  - Pridaj bell icon v navigácii s počtom notifikácií
  - Dropdown s notifikáciami
  - Mark as read funkcionalita

### 5. COST TRACKING PRE OPENAI
**Problém**: Nevieš koľko stojí OpenAI analýza.

**Riešenie**:
- Vytvor model `AIUsage` v `app.py`:
  ```python
  class AIUsage(db.Model):
      __tablename__ = 'ai_usage'
      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
      project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
      model = db.Column(db.String(50), nullable=False)
      tokens_used = db.Column(db.Integer, nullable=False)
      cost_eur = db.Column(db.Numeric(10, 4), nullable=False)
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
  ```
- Po každom OpenAI volaní:
  - Vypočítaj cost (podľa modelu a tokens)
  - Ulož do `AIUsage`
- Vytvor route `/settings/ai-usage`:
  - Zobraz históriu použitia
  - Zobraz celkové náklady
  - Zobraz graf (ak je možné)

## Technické požiadavky:

1. **Error Handling**:
   - Ak OpenAI zlyhá → použij fallback
   - Ak email zlyhá → loguj, ale nepokračuj
   - Ak Telegram zlyhá → loguj, ale nepokračuj
   - Všetky chyby musia byť logované

2. **Performance**:
   - OpenAI volania môžu byť pomalé → použij timeout (30s)
   - Email/Telegram pošli asynchronne (background task)
   - Neblokuj scraping kvôli notifikáciám

3. **Cost Management**:
   - Použij `gpt-4o-mini` namiesto `gpt-4` (10x lacnejšie)
   - Limit tokens na 300
   - Track všetky náklady

4. **Bezpečnosť**:
   - API kľúče v `.env`, nikdy v kóde
   - Validácia emailov pred odoslaním
   - Rate limiting pre OpenAI volania

## Očakávaný výsledok:

Po implementácii:
- ✅ OpenAI skutočne analyzuje inzeráty (nie len matematika)
- ✅ Email notifikácie pre "KÚPIŤ" deals
- ✅ Telegram notifikácie (ak je nakonfigurovaný)
- ✅ Dashboard notifikácie s počítadlom
- ✅ Cost tracking pre OpenAI
- ✅ Všetko funguje automaticky

## Súbory na úpravu:

1. `scripts/car_scraper.py` - OpenAI analýza
2. `app.py` - Notification model, routes
3. `utils/notifications.py` - nový súbor
4. `templates/dashboard.html` - notifikácie UI
5. `requirements.txt` - flask-mail, requests
6. `.env.example` - email a Telegram config

## Testovanie:

Po implementácii otestuj:
1. Spusti scraping → OpenAI analyzuje inzeráty
2. Nájde "KÚPIŤ" deal → email sa pošle
3. Nájde "KÚPIŤ" deal → Telegram sa pošle (ak je config)
4. Dashboard zobrazuje notifikácie
5. `/settings/ai-usage` zobrazuje cost tracking

---

**Dôležité**: 
- OpenAI API kľúč už existuje v `.env` (skontroluj ho)
- Použij `gpt-4o-mini` pre nižšie náklady
- Všetky notifikácie musia mať error handling
- Kód musí byť produkčne pripravený

