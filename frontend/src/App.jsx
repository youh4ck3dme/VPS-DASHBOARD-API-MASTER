import React, { useState, useEffect, useCallback, useRef, memo } from 'react';
import {
  BarChart3,
  Check,
  ChevronRight,
  ShieldAlert,
  TrendingUp,
  Search,
  Bell,
  Menu,
  X,
  ArrowUpRight,
  Database,
  Moon,
  Sun,
  Zap,
  Target,
  Award,
  Clock
} from 'lucide-react';
import ParallaxLogo from './components/ParallaxLogo';
import SlovakiaMap from './components/SlovakiaMap';

// ------------------ 💡 Helpers / Hooks ------------------
const useDarkMode = () => {
  const [dark, setDark] = useState(() => {
    const ls = localStorage.getItem('carScraperTheme');
    return ls ? ls === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('carScraperTheme', dark ? 'dark' : 'light');
  }, [dark]);

  return [dark, setDark];
};

// ------------------ 🔢 Animated Counter ------------------
const CountUp = ({ value, duration = 1500, className = "" }) => {
  const el = useRef(null);
  useEffect(() => {
    let start = 0;
    const startTime = performance.now();
    const step = (ts) => {
      const progress = Math.min((ts - startTime) / duration, 1);
      const current = Math.floor(progress * value);
      if (el.current) el.current.textContent = current.toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [value, duration]);
  return <span ref={el} className={className}>0</span>;
};

// ------------------ 📡 API Client ------------------
// ------------------ 🎭 Mock Data (Demo Mode) ------------------
const MOCK_STATS = {
  total_deals: 3274,
  good_deals: 132,
  total_profit: 48500.00,
  success_rate: 14.5
};

const MOCK_DEALS = [
  {
    id: 1,
    title: "Škoda Octavia III 2.0 TDI Style",
    price: 8500,
    market_value: 11200,
    profit: 2700,
    verdict: "KÚPIŤ",
    risk_level: "Nízke",
    reason: "Výrazne pod trhovou cenou (Z-Score: -1.8). Čistá história, prvý majiteľ.",
    source: "Bazoš.sk",
    link: "#",
    image_url: "",  // Demo - reálne naplní scraper
    created_at: new Date().toISOString(),
    description: "Top stav, garážované, servisná knižka."
  },
  {
    id: 2,
    title: "Volkswagen Golf VII 1.4 TSI",
    price: 9200,
    market_value: 10500,
    profit: 1300,
    verdict: "KÚPIŤ",
    risk_level: "Stredné",
    reason: "Dobrá cena, ale vyšší nájazd km. Vhodné na rýchly otoč.",
    source: "Autobazar.eu",
    link: "#",
    image_url: "",  // Demo - reálne naplní scraper
    created_at: new Date(Date.now() - 3600000).toISOString(),
    description: "Nebúrané, sezónne prezutie."
  },
  {
    id: 3,
    title: "BMW 320d Touring xDrive",
    price: 15900,
    market_value: 14500,
    profit: -1400,
    verdict: "NEKUPOVAŤ",
    risk_level: "Vysoké",
    reason: "Cena nad trhovým priemerom. Podozrenie na stočené km podľa STK.",
    source: "Bazoš.sk",
    link: "#",
    image_url: "",  // Demo - reálne naplní scraper
    created_at: new Date(Date.now() - 7200000).toISOString(),
    description: "Dovoz Nemecko, plná výbava."
  }
];

// ------------------ 📡 API Client ------------------
const API_BASE = '/api/carscraper';

const fetchDeals = async (verdict = null) => {
  try {
    const url = verdict ? `${API_BASE}/deals?verdict=${verdict}` : `${API_BASE}/deals`;
    const response = await fetch(url, {
      credentials: 'include'
    });

    // Check Content-Type to avoid parsing HTML as JSON (redirects)
    const contentType = response.headers.get("content-type");
    if (!response.ok || !contentType || !contentType.includes("application/json")) {
      console.warn('API not accessible or returned HTML (login redirect). Using Demo Data.');
      // Filter mock deals if needed
      const deals = verdict
        ? MOCK_DEALS.filter(d => d.verdict === verdict)
        : MOCK_DEALS;
      return { deals, total: deals.length };
    }

    return await response.json();
  } catch (error) {
    console.error('API Error (Demo Fallback):', error);
    return { deals: MOCK_DEALS, total: MOCK_DEALS.length };
  }
};

const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/stats`, {
      credentials: 'include'
    });

    const contentType = response.headers.get("content-type");
    if (!response.ok || !contentType || !contentType.includes("application/json")) {
      console.warn('API Stats not accessible. Using Mock Stats.');
      return MOCK_STATS;
    }

    return await response.json();
  } catch (error) {
    console.error('Stats Error (Demo Fallback):', error);
    return MOCK_STATS;
  }
};

// ------------------ 🌙 Theme Toggle ------------------
const ThemeToggle = memo(({ dark, setDark }) => (
  <button
    onClick={() => setDark(!dark)}
    aria-label="Toggle dark mode"
    className="p-1.5 rounded-md bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
  >
    {dark ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-800" />}
  </button>
));

// ------------------ 🧭 Navbar ------------------
const Navbar = memo(({ onLinkClick }) => {
  const [mobile, setMobile] = useState(false);
  const [dark] = useDarkMode();

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md border-b border-gray-200/60 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/80 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center group -ml-4">
          <ParallaxLogo />
        </a>

        <ul className="hidden md:flex items-center gap-8 text-sm font-medium">
          {['Live Feed', 'Funkcie', 'Cenník'].map((t) => (
            <li key={t}>
              <a
                href={`#${t.toLowerCase().replace(' ', '')}`}
                onClick={onLinkClick}
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                {t}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-4">
          <ThemeToggle dark={dark} setDark={useDarkMode()[1]} />
          <button className="hidden md:block bg-gray-900 hover:bg-gray-800 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
            Začať zdarma
          </button>
          <button
            onClick={() => setMobile(!mobile)}
            className="md:hidden p-1 text-gray-600 dark:text-gray-300"
            aria-label="Toggle menu"
          >
            {mobile ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </nav>

      {mobile && (
        <div className="md:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          {['Live Feed', 'Funkcie', 'Cenník'].map((t) => (
            <a
              key={t}
              href={`#${t.toLowerCase().replace(' ', '')}`}
              onClick={() => { setMobile(false); onLinkClick(); }}
              className="block px-6 py-4 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              {t}
            </a>
          ))}
        </div>
      )}
    </header>
  );
});

// ------------------ 🎯 Hero Section ------------------
const Hero = memo(() => {
  const [stats, setStats] = useState({ total_deals: 0, good_deals: 0 });

  useEffect(() => {
    fetchStats().then(setStats);
  }, []);

  return (
    <section className="relative isolate overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-900/20 pt-24 pb-20">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.1),transparent)]"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/40 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold mb-6 animate-pulse">
          <span className="flex h-2 w-2 rounded-full bg-indigo-600 animate-ping"></span>
          AI Detekcia Rizík v2.0
        </span>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-6 leading-tight">
          Obchodujte s autami na základe <br />
          <span className="text-indigo-600 dark:text-indigo-400">tvrdých dát, nie pocitov.</span>
        </h1>

        <p className="max-w-2xl mx-auto text-lg text-gray-600 dark:text-gray-400 mb-10 leading-relaxed">
          Automatizovaný systém, ktorý monitoruje trh 24/7. Analyzuje ceny, marže a riziká v reálnom čase pomocou AI,
          aby ste vy mohli kupovať len to, čo zarába.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
          <a
            href="#pricing"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3.5 rounded-lg text-sm font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
          >
            Vyskúšať Demo <ChevronRight size={18} />
          </a>
          <a
            href="#features"
            className="inline-flex items-center gap-2 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 px-8 py-3.5 rounded-lg text-sm font-semibold transition-all"
          >
            Ako to funguje?
          </a>
        </div>

        <div className="mt-12 flex justify-center gap-12 text-gray-900 dark:text-gray-200">
          <div className="text-center">
            <CountUp value={stats.total_deals || 3274} className="text-3xl font-bold text-indigo-600 dark:text-indigo-400 block" />
            <span className="block text-sm mt-1 text-gray-600 dark:text-gray-400">Analyzovaných áut</span>
          </div>
          <div className="text-center">
            <CountUp value={stats.good_deals || 132} className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 block" />
            <span className="block text-sm mt-1 text-gray-600 dark:text-gray-400">Super dealov</span>
          </div>
          <div className="text-center">
            <CountUp value={48} className="text-3xl font-bold text-purple-600 dark:text-purple-400 block" />
            <span className="block text-sm mt-1 text-gray-600 dark:text-gray-400">Spokojných klientov</span>
          </div>
        </div>
      </div>
    </section>
  );
});

// ------------------ 🎴 Deal Card ------------------
const DealCard = memo(({ deal, onOpenDetail }) => {
  const isGoodDeal = deal.verdict === "KÚPIŤ";
  const timeAgo = deal.created_at ? new Date(deal.created_at).toLocaleString('sk-SK') : 'Pred chvíľou';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col overflow-hidden group transform hover:-translate-y-1">
      <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
        {deal.image_url ? (
          <img
            src={deal.image_url}
            alt={deal.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <BarChart3 className="w-16 h-16" />
          </div>
        )}
        <div className="absolute top-3 right-3 bg-white/90 dark:bg-gray-900/90 backdrop-blur px-2 py-1 rounded text-xs font-semibold text-gray-700 dark:text-gray-300 shadow-sm border border-gray-200 dark:border-gray-700">
          {deal.source || 'Bazoš.sk'}
        </div>
      </div>

      <div className="p-5 flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-snug line-clamp-2">{deal.title}</h3>
          <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap pt-1 ml-2 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {timeAgo}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 my-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide font-medium">Cena Inzerát</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">{Number(deal.price).toLocaleString()} €</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide font-medium">Trhová Hodnota</p>
            <p className="text-xl font-bold text-gray-700 dark:text-gray-300">
              {deal.market_value ? Number(deal.market_value).toLocaleString() : 'N/A'} €
            </p>
          </div>
        </div>

        <div
          className={`rounded-lg p-3 mb-4 text-sm border ${isGoodDeal
            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'
            : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
            }`}
        >
          <div className="flex justify-between items-center mb-1">
            <span
              className={`font-bold flex items-center gap-1 ${isGoodDeal ? 'text-emerald-700 dark:text-emerald-400' : 'text-gray-600 dark:text-gray-400'
                }`}
            >
              {isGoodDeal ? <TrendingUp size={16} /> : <ShieldAlert size={16} />}
              {deal.verdict || 'RIZIKO'}
            </span>
            {deal.profit && (
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded ${isGoodDeal
                  ? 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                  }`}
              >
                Zisk: {deal.profit > 0 ? '+' : ''}{Number(deal.profit).toLocaleString()} €
              </span>
            )}
          </div>
          <p
            className={`text-xs leading-relaxed ${isGoodDeal ? 'text-emerald-800 dark:text-emerald-300' : 'text-gray-600 dark:text-gray-400'
              }`}
          >
            {deal.reason || 'Analýza prebieha...'}
          </p>
        </div>

        <div className="mt-auto flex gap-2">
          <button
            onClick={() => onOpenDetail(deal)}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg transition-colors text-sm flex items-center justify-center gap-2"
          >
            Zobraziť parametre <ChevronRight size={16} />
          </button>
          <a
            href={deal.link || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors flex items-center justify-center shrink-0"
            title="Otvoriť originálny inzerát"
          >
            <ArrowUpRight size={18} className="text-gray-400" />
          </a>
        </div>
      </div>
    </div>
  );
});

// ------------------ 🖼️ Deal Detail Modal ------------------
const DealDetailModal = memo(({ deal, onClose }) => {
  if (!deal) return null;

  const specs = deal.full_specs || {};
  const basic = specs.basic_info || {};
  const tech = specs.technical_details || {};
  const condition = specs.condition || {};
  const equipment = specs.equipment || {};

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div
        className="bg-white dark:bg-gray-900 w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 flex flex-col animate-in zoom-in-95 duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 dark:bg-indigo-900/40 p-2 rounded-lg">
              <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white truncate max-w-md">
              {deal.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Image & Basic Info */}
          <div className="space-y-6">
            <div className="aspect-video w-full rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              {deal.image_url ? (
                <img src={deal.image_url} alt={deal.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <Database size={48} />
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700/50">
                <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Cena</span>
                <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">{Number(deal.price).toLocaleString()} €</span>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700/50">
                <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Najazdené</span>
                <span className="text-2xl font-black text-gray-900 dark:text-white">{Number(deal.km || basic.km || 0).toLocaleString()} km</span>
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider">Popis od predajcu</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed italic">
                {deal.description || "Predajca neuviedol žiadny popis."}
              </p>
            </div>
          </div>

          {/* Right Column: Parameters */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden shadow-sm">
              <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 border-b border-gray-100 dark:border-gray-700">
                <h3 className="text-[10px] font-black uppercase text-gray-500 tracking-widest">Technické parametre</h3>
              </div>
              <div className="divide-y divide-gray-50 dark:divide-gray-700/50">
                {[
                  { label: "Značka", val: basic.brand || deal.brand },
                  { label: "Model", val: basic.model || deal.model },
                  { label: "Ročník", val: basic.year || deal.year },
                  { label: "Palivo", val: basic.fuel_type || deal.fuel_type },
                  { label: "Prevodovka", val: basic.transmission || deal.transmission },
                  { label: "Výkon", val: basic.power_kw ? `${basic.power_kw} kW (${Math.round(basic.power_kw * 1.36)} koní)` : null },
                  { label: "Objem", val: basic.engine_size_ccm ? `${basic.engine_size_ccm} ccm` : null },
                  { label: "Pohon", val: tech.drive_type },
                  { label: "Karoséria", val: tech.body_style },
                  { label: "Farba", val: tech.color }
                ].filter(p => p.val).map((p, i) => (
                  <div key={i} className="flex justify-between items-center px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                    <span className="text-xs text-gray-500">{p.label}</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">{p.val}</span>
                  </div>
                ))}
              </div>
            </div>

            {equipment.other_features && equipment.other_features.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-3">Výbava</h3>
                <div className="flex flex-wrap gap-2">
                  {equipment.other_features.map((item, idx) => (
                    <span key={idx} className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-1 rounded text-[10px] font-medium border border-gray-200 dark:border-gray-700">
                      {item.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-6 mt-6 border-t border-gray-100 dark:border-gray-800">
              <a
                href={deal.link}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20"
              >
                Prejsť na inzerát <ArrowUpRight size={20} />
              </a>
              <p className="text-[10px] text-center text-gray-400 mt-4 uppercase font-bold tracking-tighter">
                ID Ponuky: #{deal.id} • Zdroj: {deal.source}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

const POPULAR_BRANDS = [
  'Skoda', 'Volkswagen', 'Audi', 'BMW', 'Mercedes-Benz',
  'Hyundai', 'Kia', 'Toyota', 'Peugeot', 'Renault',
  'Ford', 'Opel', 'Dacia', 'Fiat', 'Seat'
];

// ------------------ 📰 Live Feed ------------------
const LiveFeed = memo(() => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedDeal, setSelectedDeal] = useState(null);

  const filteredDeals = React.useMemo(() => {
    let result = deals;
    // ...

    // 1. Filter podľa typu/ceny
    if (filter === 'KÚPIŤ') {
      result = result.filter(d => d.verdict === 'KÚPIŤ');
    } else if (filter === 'CHEAP') {
      result = result.filter(d => d.price <= 5000);
    }

    // 2. Filter podľa regiónu
    if (selectedRegion) {
      result = result.filter(d => {
        if (d.region) return d.region === selectedRegion;
        return d.location && d.location.includes(selectedRegion.replace('ý', ''));
      });
    }
    // 3. Filter podľa značky
    if (selectedBrand) {
      result = result.filter(d => d.brand && d.brand.toLowerCase() === selectedBrand.toLowerCase());
    }
    return result;
  }, [deals, selectedRegion, filter, selectedBrand]);

  const loadDeals = useCallback(async () => {
    setLoading(true);
    // API filter posielame len ak je to verdict
    const apiFilter = (filter === 'KÚPIŤ') ? 'KÚPIŤ' : null;
    const data = await fetchDeals(apiFilter);
    setDeals(data.deals || []);
    setLoading(false);
  }, [filter]);

  useEffect(() => {
    loadDeals();
    const interval = setInterval(loadDeals, 30000); // Refresh každých 30s
    return () => clearInterval(interval);
  }, [loadDeals]);

  return (
    <section id="feed" className="py-20 bg-gray-50 dark:bg-gray-900 border-y border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-10 flex-wrap gap-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Live Príležitosti</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Aktuálny prehľad trhu spracovaný naším AI algoritmom.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              System Operational
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter(null)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === null
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
                  }`}
              >
                Všetky
              </button>
              <button
                onClick={() => setFilter('KÚPIŤ')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'KÚPIŤ'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
                  }`}
              >
                Len Kúpiť
              </button>
              <button
                onClick={() => setFilter('CHEAP')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'CHEAP'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
                  }`}
              >
                Lacné (&lt; 5k €)
              </button>
            </div>
          </div>
        </div>

        {/* 🏷️ Brand Filter */}
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            Kategórie podľa značiek
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-8 gap-3">
            <button
              onClick={() => setSelectedBrand(null)}
              className={`p-3 rounded-xl border text-center transition-all ${selectedBrand === null
                ? 'bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-500/20'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-indigo-300'
                }`}
            >
              <div className="text-xs font-bold uppercase">Všetky</div>
              <div className="text-[10px] opacity-70">{deals.length} ks</div>
            </button>
            {POPULAR_BRANDS.map(brand => {
              const count = deals.filter(d => d.brand && d.brand.toLowerCase() === brand.toLowerCase()).length;
              return (
                <button
                  key={brand}
                  onClick={() => setSelectedBrand(selectedBrand === brand ? null : brand)}
                  className={`p-3 rounded-xl border text-center transition-all ${selectedBrand === brand
                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-500/20'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-indigo-300'
                    } ${count === 0 ? 'opacity-40 grayscale' : ''}`}
                >
                  <div className="text-xs font-bold truncate">{brand}</div>
                  <div className="text-[10px] opacity-70">{count} ks</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Region Map Filter */}
        <div className="mb-12">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            Filtrovať podľa lokality (interaktívna mapa)
          </h3>
          <SlovakiaMap selectedRegion={selectedRegion} onRegionSelect={setSelectedRegion} deals={deals} />
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 animate-pulse">
                <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : filteredDeals.length === 0 ? (
          <div className="text-center py-12">
            <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              {selectedRegion
                ? `Žiadne inzeráty pre ${selectedRegion}.`
                : "Žiadne deals na zobrazenie. Spusti scraping skript!"
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredDeals.map((deal) => (
              <DealCard key={deal.id} deal={deal} onOpenDetail={setSelectedDeal} />
            ))}
          </div>
        )}

        {selectedDeal && (
          <DealDetailModal
            deal={selectedDeal}
            onClose={() => setSelectedDeal(null)}
          />
        )}
      </div>
    </section>
  );
});

// ------------------ ⚡ Features ------------------
const FeatureItem = memo(({ icon: Icon, title, desc }) => (
  <div className="flex gap-4 items-start group">
    <div className="bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-lg shrink-0 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900/40 transition-colors">
      <Icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
    </div>
    <div>
      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{title}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{desc}</p>
    </div>
  </div>
));

const Features = memo(() => {
  return (
    <section id="features" className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
              Komplexná analýza v zlomku sekundy.
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8">
              Zatiaľ čo konkurencia hľadá inzeráty manuálne, vy dostávate notifikácie len na tie, ktoré prešli
              štvorstupňovou kontrolou kvality.
            </p>

            <div className="space-y-8">
              <FeatureItem
                icon={Database}
                title="Agregácia dát"
                desc="Zber dát z Bazoš, Autobazar.eu a ďalších portálov do jednej prehľadnej databázy v reálnom čase."
              />
              <FeatureItem
                icon={TrendingUp}
                title="Z-Score Analytika"
                desc="Štatistické vyhodnotenie odchýlky ceny od trhového priemeru pre daný model a rok výroby."
              />
              <FeatureItem
                icon={ShieldAlert}
                title="NLP Detekcia rizík"
                desc="Umelá inteligencia číta popis inzerátu a hľadá kľúčové slová indikujúce technické problémy (klepanie, dym, hrdza)."
              />
              <FeatureItem
                icon={Zap}
                title="Real-time Notifikácie"
                desc="Okamžité upozornenia cez Telegram alebo Email pri nájdení super dealu."
              />
            </div>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
              <div className="flex justify-between items-center pb-4 border-b border-gray-100 dark:border-gray-700">
                <span className="font-semibold text-gray-900 dark:text-white">Analýza Inzerátu #4922</span>
                <span className="text-xs bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 px-2 py-1 rounded-full font-medium">
                  Completed
                </span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Model</span>
                  <span className="text-gray-900 dark:text-white font-medium">Škoda Octavia 2018</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Cena</span>
                  <span className="text-gray-900 dark:text-white font-medium">9 500 €</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Trhový priemer</span>
                  <span className="text-gray-900 dark:text-white font-medium">13 200 €</span>
                </div>
                <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden mt-2">
                  <div className="h-full w-3/4 bg-indigo-600 rounded-full"></div>
                </div>
                <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium pt-1">
                  Potenciálna marža: 28%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
});

// ------------------ 💰 Pricing ------------------
const Pricing = memo(() => {
  return (
    <section id="pricing" className="py-24 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">Transparentné ceny</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-12">Žiadne skryté poplatky. Plaťte len za to, čo využijete.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Starter</h3>
            <div className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
              49€<span className="text-base text-gray-500 dark:text-gray-400 font-normal">/mes</span>
            </div>
            <ul className="space-y-4 text-left mb-8">
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> 100 analýz denne
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> Email notifikácie
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> Základný filter
              </li>
            </ul>
            <button className="w-full py-2.5 border-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors">
              Vybrať Starter
            </button>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border-2 border-indigo-600 dark:border-indigo-500 shadow-xl relative transform scale-105">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase">
              Odporúčané
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Professional</h3>
            <div className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
              99€<span className="text-base text-gray-500 dark:text-gray-400 font-normal">/mes</span>
            </div>
            <ul className="space-y-4 text-left mb-8">
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" />
                <strong>Neobmedzené</strong> analýzy
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" />
                <strong>Instantné</strong> Telegram notifikácie
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> AI detekcia rizík
              </li>
            </ul>
            <button className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition-colors shadow-lg">
              Vybrať Professional
            </button>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Enterprise</h3>
            <div className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
              249€<span className="text-base text-gray-500 dark:text-gray-400 font-normal">/mes</span>
            </div>
            <ul className="space-y-4 text-left mb-8">
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> API Prístup
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> Export dát (CSV, XML)
              </li>
              <li className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-2 shrink-0" /> Dedikovaná podpora
              </li>
            </ul>
            <button className="w-full py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              Kontaktovať obchod
            </button>
          </div>
        </div>
      </div>
    </section>
  );
});

// ------------------ 🦶 Footer ------------------
const Footer = memo(() => (
  <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-12">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div className="flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        <span className="font-bold text-gray-900 dark:text-white">CarScraper Pro</span>
      </div>
      <div className="text-sm text-gray-500 dark:text-gray-400 flex gap-6">
        <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">Ochrana údajov</a>
        <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">Obchodné podmienky</a>
        <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">Podpora</a>
      </div>
      <div className="text-sm text-gray-400 dark:text-gray-500">© 2024 DataDriven Solutions s.r.o.</div>
    </div>
  </footer>
));

// ------------------ 🎬 Main App ------------------
const App = () => {
  const handleLinkClick = useCallback((e) => {
    e.preventDefault();
    const href = e.currentTarget.getAttribute('href');
    if (href && href.startsWith('#')) {
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 font-sans text-gray-900 dark:text-gray-100 antialiased">
      <Navbar onLinkClick={handleLinkClick} />
      <Hero />
      <LiveFeed />
      <Features />
      <Pricing />
      <Footer />
    </div>
  );
};

export default App;

