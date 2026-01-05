import React, { useState, useEffect, useCallback, memo, useMemo } from 'react';
import { Database } from 'lucide-react';
import { Container } from '../ui/Container';
import { Button } from '../ui/Button';
import DealCard from './DealCard';
import DealDetailModal from './DealDetailModal';
import SlovakiaMap from '../SlovakiaMap'; // Assuming this remains in components root/

// ------------------ 📡 API Client Helpers ------------------
// Moved locally or import from utility file in real app
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
        image_url: "",
        created_at: new Date().toISOString(),
        description: "Top stav, garážované, servisná knižka."
    },
    // ... more mock data would be here
];

const API_BASE = '/api/carscraper';

const fetchDeals = async (verdict = null) => {
    try {
        const url = verdict ? `${API_BASE}/deals?verdict=${verdict}` : `${API_BASE}/deals`;
        const response = await fetch(url, { credentials: 'include' });
        const contentType = response.headers.get("content-type");
        if (!response.ok || !contentType || !contentType.includes("application/json")) {
            console.warn('API not accessible. Using Demo Data.');
            const deals = verdict
                ? MOCK_DEALS.filter(d => d.verdict === verdict)
                : MOCK_DEALS;
            return { deals, total: deals.length };
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { deals: MOCK_DEALS, total: MOCK_DEALS.length };
    }
};

const POPULAR_BRANDS = [
    'Skoda', 'Volkswagen', 'Audi', 'BMW', 'Mercedes-Benz',
    'Hyundai', 'Kia', 'Toyota', 'Peugeot', 'Renault',
    'Ford', 'Opel', 'Dacia', 'Fiat', 'Seat'
];

const LiveFeed = memo(() => {
    const [deals, setDeals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState(null);
    const [selectedRegion, setSelectedRegion] = useState(null);
    const [selectedBrand, setSelectedBrand] = useState(null);
    const [selectedDeal, setSelectedDeal] = useState(null); // For modal

    const filteredDeals = useMemo(() => {
        let result = deals;

        if (filter === 'KÚPIŤ') {
            result = result.filter(d => d.verdict === 'KÚPIŤ');
        } else if (filter === 'CHEAP') {
            result = result.filter(d => d.price <= 5000);
        }

        if (selectedRegion) {
            result = result.filter(d => {
                if (d.region) return d.region === selectedRegion;
                return d.location && d.location.includes(selectedRegion.replace('ý', ''));
            });
        }

        if (selectedBrand) {
            result = result.filter(d => d.brand && d.brand.toLowerCase() === selectedBrand.toLowerCase());
        }
        return result;
    }, [deals, selectedRegion, filter, selectedBrand]);

    const loadDeals = useCallback(async () => {
        setLoading(true);
        const apiFilter = (filter === 'KÚPIŤ') ? 'KÚPIŤ' : null;
        const data = await fetchDeals(apiFilter);
        setDeals(data.deals || []);
        setLoading(false);
    }, [filter]);

    useEffect(() => {
        loadDeals();
        const interval = setInterval(loadDeals, 30000);
        return () => clearInterval(interval);
    }, [loadDeals]);

    return (
        <section id="livefeed" className="py-24 bg-slate-50 dark:bg-slate-900/50 border-y border-slate-200 dark:border-slate-800">
            <Container>
                <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                    <div>
                        <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Live Príležitosti</h2>
                        <p className="text-slate-600 dark:text-slate-400">Aktuálny prehľad trhu spracovaný naším AI algoritmom.</p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">
                        <div className="hidden lg:flex items-center gap-2 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/20 px-3 py-1.5 rounded-full">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            System Operational
                        </div>

                        <div className="flex p-1 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm w-full sm:w-auto">
                            {[
                                { id: null, label: 'Všetky' },
                                { id: 'KÚPIŤ', label: 'Len Kúpiť' },
                                { id: 'CHEAP', label: 'Lacné (<5k)' },
                            ].map((opt) => (
                                <button
                                    key={opt.label}
                                    onClick={() => setFilter(opt.id)}
                                    className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-medium transition-all ${filter === opt.id
                                            ? 'bg-indigo-600 text-white shadow-md'
                                            : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                                        }`}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Brand Filter */}
                <div className="mb-10">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 ml-1">
                        Kategórie podľa značiek
                    </h3>
                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={() => setSelectedBrand(null)}
                            className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all ${selectedBrand === null
                                    ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-900'
                                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-300'
                                }`}
                        >
                            Všetky ({deals.length})
                        </button>
                        {POPULAR_BRANDS.map(brand => {
                            const count = deals.filter(d => d.brand && d.brand.toLowerCase() === brand.toLowerCase()).length;
                            return (
                                <button
                                    key={brand}
                                    onClick={() => setSelectedBrand(selectedBrand === brand ? null : brand)}
                                    className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all ${selectedBrand === brand
                                            ? 'bg-indigo-600 text-white border-indigo-600 shadow-lg shadow-indigo-500/20'
                                            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-300'
                                        } ${count === 0 ? 'opacity-50' : ''}`}
                                    disabled={count === 0}
                                >
                                    {brand} <span className="opacity-60 ml-1 text-xs">{count}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Region Map Filter */}
                <div className="mb-16 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-8 shadow-sm">
                    <div className="flex justify-between mb-6">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Mapa Príležitostí</h3>
                        {selectedRegion && (
                            <Button variant="ghost" size="sm" onClick={() => setSelectedRegion(null)} className="text-red-500 hover:text-red-600 hover:bg-red-50">
                                Zrušiť filter: {selectedRegion}
                            </Button>
                        )}
                    </div>
                    <div className="w-full max-w-2xl mx-auto">
                        <SlovakiaMap selectedRegion={selectedRegion} onRegionSelect={setSelectedRegion} deals={deals} />
                    </div>
                </div>

                {/* Grid */}
                <div className="min-h-[400px]">
                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {[1, 2, 3, 4, 5, 6].map((i) => (
                                <div key={i} className="bg-white dark:bg-slate-800 rounded-2xl h-[420px] border border-slate-200 dark:border-slate-700 animate-pulse" />
                            ))}
                        </div>
                    ) : filteredDeals.length === 0 ? (
                        <div className="text-center py-20 bg-white dark:bg-slate-800 rounded-3xl border border-dashed border-slate-300 dark:border-slate-700">
                            <div className="bg-slate-100 dark:bg-slate-900 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                                <Database className="w-8 h-8 text-slate-400" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Žiadne inzeráty sa nenašli</h3>
                            <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                                Pre zvolené filtre momentálne neevidujeme žiadne ponuky. Skúste zmeniť kritériá alebo počkajte na ďalší scrap.
                            </p>
                            <Button variant="outline" className="mt-6" onClick={() => { setFilter(null); setSelectedBrand(null); setSelectedRegion(null); }}>
                                Resetovať filtre
                            </Button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {filteredDeals.map((deal) => (
                                <DealCard key={deal.id} deal={deal} onOpenDetail={setSelectedDeal} />
                            ))}
                        </div>
                    )}
                </div>

                {/* Modal */}
                <DealDetailModal deal={selectedDeal} onClose={() => setSelectedDeal(null)} />

            </Container>
        </section>
    );
});

export default LiveFeed;
