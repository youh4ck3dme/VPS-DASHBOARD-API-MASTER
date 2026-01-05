import React, { useState, useEffect, memo } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Lock, Unlock } from 'lucide-react';
import { Container } from '../ui/Container';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';

const TOP_DEMO_DEALS = [
    {
        id: 'demo-1',
        title: 'Škoda Octavia III 2.0 TDI Style',
        price: 8900,
        market_value: 10500,
        profit: 1600,
        verdict: 'KÚPIŤ',
        image_url: '/static/demo_skoda.png',
        year: 2017,
        km: 145000
    },
    {
        id: 'demo-2',
        title: 'Volkswagen Golf VII 1.4 TSI',
        price: 7200,
        market_value: 8800,
        profit: 1600,
        verdict: 'KÚPIŤ',
        image_url: '/static/demo_golf.png',
        year: 2016,
        km: 98000
    },
    {
        id: 'demo-3',
        title: 'BMW 320d Touring xDrive',
        price: 12500,
        market_value: 11900,
        profit: -600,
        verdict: 'NEKUPOVAŤ',
        image_url: '/static/demo_bmw.png',
        year: 2015,
        km: 195000
    }
];

const TopDeals = memo(() => {
    const [unlocked, setUnlocked] = useState(false);
    const [topDeals, setTopDeals] = useState([]);

    useEffect(() => {
        // Fetch real top deals from API
        const loadTopDeals = async () => {
            try {
                const response = await fetch('/api/top-deals', { credentials: 'include' });
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.length > 0) {
                        setTopDeals(data);
                    }
                }
            } catch (error) {
                console.error('Error fetching top deals:', error);
            }
        };
        loadTopDeals();
    }, []);

    const handleUnlock = () => {
        // In production, trigger Stripe checkout
        alert('💳 Platba 0.99€ - Toto je demo. V produkčnej verzii sa otvorí Stripe checkout.');
        setUnlocked(true);
    };

    const dealsToShow = unlocked ? topDeals : TOP_DEMO_DEALS;

    return (
        <section className="py-24 bg-gradient-to-b from-amber-50/50 to-white dark:from-amber-900/10 dark:to-gray-950 border-y border-amber-100/50 dark:border-amber-900/20">
            <Container>
                <div className="text-center mb-16 max-w-3xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 mb-6"
                    >
                        <Badge variant="warning" className="px-3 py-1 bg-amber-100/80 dark:bg-amber-900/50 text-amber-900 dark:text-amber-200 border-amber-200 dark:border-amber-700">
                            <Trophy className="w-3.5 h-3.5 mr-1" /> PREMIUM BONUS
                        </Badge>
                    </motion.div>

                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-3xl md:text-5xl font-bold text-slate-900 dark:text-white mb-6"
                    >
                        TOP 6 Ponúk Dňa
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed"
                    >
                        AI každý deň o polnoci vyhodnotí stovky inzerátov a vyberie 6 najziskovejších.
                        Tieto ponuky sú exkluzívne pre prémiových používateľov.
                    </motion.p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                    {dealsToShow.slice(0, 3).map((deal, index) => (
                        <motion.div
                            key={deal.id}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <Card
                                hoverEffect
                                className={`group relative overflow-hidden border-2 h-full flex flex-col ${deal.verdict === 'KÚPIŤ'
                                    ? 'border-emerald-500/50 dark:border-emerald-500/30'
                                    : 'border-red-500/50 dark:border-red-500/30'
                                    }`}
                            >
                                {/* Verdict Badge */}
                                <Badge
                                    className={`absolute top-4 left-4 z-20 font-bold shadow-lg ${deal.verdict === 'KÚPIŤ' ? 'bg-emerald-500 text-white border-0' : 'bg-red-500 text-white border-0'
                                        }`}
                                >
                                    {deal.verdict}
                                </Badge>

                                {/* Profit Badge */}
                                {deal.profit > 0 && (
                                    <Badge variant="warning" className="absolute top-4 right-4 z-20 font-bold shadow-lg bg-amber-400 text-amber-950 border-0">
                                        +{deal.profit.toLocaleString()}€ ZISK
                                    </Badge>
                                )}

                                {/* Image */}
                                <div className="relative h-56 bg-slate-100 dark:bg-slate-800 overflow-hidden">
                                    <img
                                        src={deal.image_url}
                                        alt={deal.title}
                                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>
                                </div>

                                {/* Content */}
                                <div className="p-6 flex-1 flex flex-col">
                                    <h3 className="font-bold text-xl text-slate-900 dark:text-white mb-4 line-clamp-2 leading-tight">
                                        {deal.title}
                                    </h3>

                                    <div className="flex justify-between items-end mb-6">
                                        <div>
                                            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">Cena</span>
                                            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                                                {deal.price.toLocaleString()}<span className="text-xl align-top ml-0.5">€</span>
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">Trhová</span>
                                            <p className="text-lg font-medium text-slate-500 dark:text-slate-400 line-through decoration-slate-400/50">
                                                {deal.market_value.toLocaleString()}€
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex gap-3 mt-auto">
                                        <Badge variant="default" className="bg-slate-100 dark:bg-slate-800 border-0 text-slate-600 dark:text-slate-300">
                                            {deal.year}
                                        </Badge>
                                        <Badge variant="default" className="bg-slate-100 dark:bg-slate-800 border-0 text-slate-600 dark:text-slate-300">
                                            {(deal.km / 1000).toFixed(0)}k km
                                        </Badge>
                                    </div>

                                    {!unlocked && (
                                        <div className="absolute inset-0 z-30 bg-gradient-to-br from-white/60 via-white/80 to-white/95 dark:from-slate-900/60 dark:via-slate-900/80 dark:to-slate-900/95 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center border-t border-white/20 dark:border-white/5 transition-all duration-500">
                                            <div className="bg-gradient-to-br from-amber-400 to-orange-600 p-4 rounded-full shadow-2xl shadow-amber-500/30 mb-5 relative group-hover:scale-110 transition-transform duration-500">
                                                <Lock className="w-8 h-8 text-white drop-shadow-md" />
                                            </div>
                                            <p className="text-slate-900 dark:text-white font-black text-xl mb-2 drop-shadow-sm tracking-tight">
                                                Prémiová ponuka
                                            </p>
                                            <p className="text-slate-600 dark:text-slate-400 text-sm font-medium max-w-[200px]">
                                                Odomknite pre zobrazenie detailov a analýzy
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        </motion.div>
                    ))}
                </div>

                {!unlocked && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center"
                    >
                        <Button
                            onClick={handleUnlock}
                            size="lg"
                            className="px-10 py-8 text-lg rounded-2xl shadow-xl shadow-amber-500/20 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 border-0"
                        >
                            <Unlock className="w-6 h-6 mr-3" />
                            Odomknúť TOP 6 dňa za 0.99€
                        </Button>
                        <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mt-4">
                            Jednorazová platba • Platí do polnoci • Nové ponuky každý deň
                        </p>
                    </motion.div>
                )}
            </Container>
        </section>
    );
});

export default TopDeals;
