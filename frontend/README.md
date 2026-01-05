# CarScraper Pro - Frontend

React frontend pre CarScraper Pro aplikáciu.

## 🚀 Rýchly štart

### 1. Inštalácia závislostí

```bash
cd frontend
npm install
```

### 2. Spustenie development servera

```bash
npm run dev
```

Frontend beží na `http://localhost:3000` a automaticky proxy API požiadavky na `http://localhost:6002`

### 3. Build pre produkciu

```bash
npm run build
```

Build sa vytvorí v `../static/carscraper/` a Flask ho automaticky servuje na `/carscraper`

## 📁 Štruktúra

```
frontend/
├── src/
│   ├── App.jsx          # Hlavný React komponent
│   ├── main.jsx         # Entry point
│   └── index.css        # Tailwind CSS
├── index.html           # HTML template
├── package.json         # NPM závislosti
├── vite.config.js       # Vite konfigurácia
├── tailwind.config.js   # Tailwind konfigurácia
└── postcss.config.js    # PostCSS konfigurácia
```

## 🎨 Funkcie

- ✅ **Dark Mode** - Automatická detekcia a prepínanie
- ✅ **Real-time Data** - Automatické obnovovanie každých 30s
- ✅ **Responsive Design** - Funguje na mobile, tablete, desktop
- ✅ **Animácie** - Smooth transitions a hover efekty
- ✅ **API Integration** - Kompletná integrácia s Flask backendom

## 🔧 Konfigurácia

### Zmena API URL

V `vite.config.js`:
```js
proxy: {
  '/api': {
    target: 'http://localhost:6002',  // Zmeň podľa potreby
    changeOrigin: true
  }
}
```

### Zmena portu

V `vite.config.js`:
```js
server: {
  port: 3000,  // Zmeň podľa potreby
}
```

## 📦 Závislosti

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Ikony
- **clsx** - Conditional classes

## 🐛 Riešenie problémov

### Port už používaný

```bash
# Nájdite proces
lsof -ti:3000

# Zastavte ho
kill -9 $(lsof -ti:3000)
```

### API nefunguje

1. Skontroluj, či Flask backend beží na porte 6002
2. Skontroluj CORS nastavenia v `app.py`
3. Skontroluj proxy konfiguráciu v `vite.config.js`

### Build zlyhá

```bash
# Vymaž node_modules a reinstaluj
rm -rf node_modules package-lock.json
npm install
```

## 📚 Dokumentácia

- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/)

