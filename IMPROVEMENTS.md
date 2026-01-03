# Návrhy na vylepšenie projektu

Tento dokument obsahuje konkrétne návrhy na vylepšenie VPS Dashboard API projektu, zoradené podľa priority a dôležitosti.

## 🔴 Vysoká priorita (Kritické vylepšenia)

### 1. **Odstránenie debug logovania z produkčného kódu**
**Problém**: V `app.py` je stále aktívne debug logovanie, ktoré zapisuje do súboru pri každom volaní.
**Riešenie**: 
- Odstrániť všetky `#region agent log` bloky
- Použiť len štandardné Flask logging
- Debug logovanie zapnúť len v development režime

**Kód**: `app.py` riadky 70-113 (check_password), 372-460 (login)

---

### 2. **Zmena hesla používateľa**
**Problém**: Chýba možnosť zmeniť heslo po prihlásení.
**Riešenie**:
- Pridať route `/settings` alebo `/change-password`
- Formulár na zmenu hesla
- Validácia starého hesla
- Flash notifikácia po úspešnej zmene

**Priorita**: 🔴 Vysoká (bezpečnosť)

---

### 3. **Mazanie a editácia projektov**
**Problém**: Projekty sa dajú len vytvárať, nie mazať ani editovať.
**Riešenie**:
- Pridať `DELETE /projects/<id>` endpoint
- Pridať `PUT /projects/<id>` endpoint
- UI tlačidlá na mazanie/editáciu
- Potvrdenie pred zmazaním

**Priorita**: 🔴 Vysoká (základná funkcionalita)

---

### 4. **Lepšie error handling**
**Problém**: Niektoré chyby nie sú správne zachytené a zobrazujú sa technické detaily.
**Riešenie**:
- Pridať error handlers pre všetky bežné chyby
- User-friendly error messages
- Logovanie chýb bez zobrazovania citlivých informácií
- Error tracking (napr. Sentry)

**Priorita**: 🔴 Vysoká (UX a bezpečnosť)

---

## 🟡 Stredná priorita (Dôležité vylepšenia)

### 5. **Paginácia a vyhľadávanie**
**Problém**: Ak je veľa projektov, dashboard sa môže stať pomalým.
**Riešenie**:
- Paginácia projektov (napr. 10 na stránku)
- Vyhľadávanie projektov podľa názvu
- Filtrovanie podľa stavu (aktívny/neaktívny)
- Zoradenie (podľa dátumu, názvu)

**Priorita**: 🟡 Stredná (UX)

---

### 6. **API Key rotácia a regenerácia**
**Problém**: API kľúče sa generujú len pri vytvorení projektu.
**Riešenie**:
- Tlačidlo "Regenerovať API kľúč"
- História API kľúčov
- Možnosť deaktivovať staré kľúče
- Notifikácia pri zmene kľúča

**Priorita**: 🟡 Stredná (bezpečnosť)

---

### 7. **Statistiky a Analytics Dashboard**
**Problém**: Chýba prehľad o používaní systému.
**Riešenie**:
- Počet projektov, platieb, automatizácií
- Grafy používania (napr. Chart.js)
- História aktivít
- API usage statistics

**Priorita**: 🟡 Stredná (monitoring)

---

### 8. **Email notifikácie**
**Problém**: Žiadne emailové notifikácie o dôležitých udalostiach.
**Riešenie**:
- SMTP konfigurácia v `.env`
- Notifikácie pri: nových platbách, chybách automatizácií, zmene hesla
- Email templates
- Možnosť vypnúť notifikácie

**Priorita**: 🟡 Stredná (UX)

---

### 9. **Export dát (CSV/JSON)**
**Problém**: Chýba možnosť exportovať dáta.
**Riešenie**:
- Export projektov do CSV/JSON
- Export platieb
- Export AI požiadaviek
- Bulk operácie

**Priorita**: 🟡 Stredná (funkcionalita)

---

### 10. **Lepšie validácia formulárov**
**Problém**: Niektoré formuláre nemajú dostatočnú validáciu.
**Riešenie**:
- Validácia emailov
- Validácia cron rozvrhu
- Validácia API kľúčov
- Client-side validácia (JavaScript)

**Priorita**: 🟡 Stredná (bezpečnosť)

---

## 🟢 Nízka priorita (Nice to have)

### 11. **Dark mode**
**Problém**: Chýba dark mode pre lepšiu prácu v noci.
**Riešenie**:
- CSS pre dark mode
- Toggle tlačidlo
- Uloženie preferencie v localStorage
- Bootstrap dark theme

**Priorita**: 🟢 Nízka (UX)

---

### 12. **Multi-language podpora**
**Problém**: Aplikácia je len v slovenčine.
**Riešenie**:
- Flask-Babel integrácia
- Podpora SK, EN, CS
- Prepínanie jazykov
- Lokalizácia dátumov a čísel

**Priorita**: 🟢 Nízka (internacionalizácia)

---

### 13. **WebSocket pre real-time aktualizácie**
**Problém**: Zmeny sa aktualizujú len po refreshi.
**Riešenie**:
- Flask-SocketIO integrácia
- Real-time notifikácie
- Live aktualizácie dashboardu
- WebSocket pre monitoring

**Priorita**: 🟢 Nízka (modernizácia)

---

### 14. **2FA (Dvojfaktorová autentifikácia)**
**Problém**: Len základné prihlásenie.
**Riešenie**:
- TOTP (Google Authenticator)
- SMS verifikácia (voliteľné)
- Backup kódy
- Povinné 2FA pre adminov

**Priorita**: 🟢 Nízka (bezpečnosť)

---

### 15. **API Rate Limiting per projekt**
**Problém**: Rate limiting je globálny, nie per projekt.
**Riešenie**:
- Rate limiting per API kľúč
- Rôzne limity pre rôzne projekty
- Usage tracking
- Upgrade limitu cez platby

**Priorita**: 🟢 Nízka (monetizácia)

---

### 16. **Webhook podpora**
**Problém**: Chýba možnosť notifikovať externé služby.
**Riešenie**:
- Webhook URL konfigurácia per projekt
- Notifikácie pri: platbách, chybách, úspechoch
- Retry mechanizmus
- Webhook history

**Priorita**: 🟢 Nízka (integrace)

---

### 17. **Dockerizácia**
**Problém**: Inštalácia je manuálna.
**Riešenie**:
- Dockerfile
- docker-compose.yml
- Docker Hub image
- Kubernetes manifests

**Priorita**: 🟢 Nízka (deployment)

---

### 18. **Swagger/OpenAPI dokumentácia**
**Problém**: API dokumentácia je len základná.
**Riešenie**:
- Flask-RESTX alebo Flask-Swagger
- Interaktívna API dokumentácia
- Try it out funkcionalita
- Export OpenAPI spec

**Priorita**: 🟢 Nízka (dokumentácia)

---

### 19. **Unit a Integration testy**
**Problém**: Testy existujú, ale môžu byť rozšírené.
**Riešenie**:
- Viac testov pre kritické funkcie
- Test coverage report
- CI/CD integrácia
- E2E testy

**Priorita**: 🟢 Nízka (kvalita kódu)

---

### 20. **Admin panel pre správu používateľov**
**Problém**: Chýba admin rozhranie.
**Riešenie**:
- Zoznam všetkých používateľov
- Aktivácia/deaktivácia účtov
- Reset hesiel
- Audit log

**Priorita**: 🟢 Nízka (administrácia)

---

## 🛠️ Technické vylepšenia

### 21. **Refaktoring kódu**
- Rozdeliť `app.py` na moduly (routes, models, utils)
- Blueprint architektúra
- Service layer pattern
- Dependency injection

### 22. **Database migrácie**
- Flask-Migrate integrácia
- Verzovanie schémy
- Rollback možnosti
- Seed data

### 23. **Caching stratégia**
- Redis caching pre často používané dáta
- Cache invalidation
- Cache warming
- Performance monitoring

### 24. **Logging vylepšenia**
- Struktúrované logovanie (JSON)
- Log rotation
- Centralizované logovanie (ELK stack)
- Alerting pri chybách

### 25. **Security hardening**
- HTTPS enforcement
- Security headers (CSP, HSTS, atď.)
- SQL injection protection (už je, ale overiť)
- XSS protection
- Rate limiting na login

---

## 📊 UI/UX vylepšenia

### 26. **Loading states**
- Spinner pri načítaní
- Skeleton screens
- Progress indicators
- Optimistic UI updates

### 27. **Toast notifikácie**
- Moderné toast notifikácie namiesto flash messages
- Auto-dismiss
- Rôzne typy (success, error, warning, info)
- Stacking notifikácií

### 28. **Keyboard shortcuts**
- `Ctrl+K` pre vyhľadávanie
- `Ctrl+N` pre nový projekt
- `Esc` pre zatvorenie modálov
- Navigácia klávesnicou

### 29. **Drag & Drop**
- Presúvanie projektov
- Upload súborov drag & drop
- Reorder automatizácií

### 30. **Responsive improvements**
- Lepšia mobilná navigácia
- Touch gestures
- Mobile-first design
- PWA podpora

---

## 🎯 Odporúčaná implementačná postupnosť

### Fáza 1 (Okamžite):
1. ✅ Odstránenie debug logovania
2. ✅ Zmena hesla
3. ✅ Mazanie projektov
4. ✅ Lepšie error handling

### Fáza 2 (Krátkodobo):
5. ✅ Paginácia
6. ✅ API key regenerácia
7. ✅ Statistiky
8. ✅ Email notifikácie

### Fáza 3 (Strednodobo):
9. ✅ Export dát
10. ✅ Validácia formulárov
11. ✅ WebSocket
12. ✅ 2FA

### Fáza 4 (Dlhodobo):
13. ✅ Docker
14. ✅ Swagger
15. ✅ Multi-language
16. ✅ Admin panel

---

## 💡 Zhrnutie

**Najdôležitejšie vylepšenia:**
1. 🔴 Odstránenie debug kódu
2. 🔴 Zmena hesla
3. 🔴 Mazanie/editácia projektov
4. 🔴 Error handling
5. 🟡 Paginácia a vyhľadávanie
6. 🟡 API key regenerácia
7. 🟡 Statistiky
8. 🟡 Email notifikácie

**Odhadovaný čas implementácie:**
- Fáza 1: 4-6 hodín
- Fáza 2: 8-12 hodín
- Fáza 3: 16-24 hodín
- Fáza 4: 32+ hodín

**ROI (Return on Investment):**
- Najvyšší: Bezpečnosť a základná funkcionalita (Fáza 1)
- Stredný: UX a monitoring (Fáza 2)
- Nízky: Nice-to-have features (Fáza 3-4)

