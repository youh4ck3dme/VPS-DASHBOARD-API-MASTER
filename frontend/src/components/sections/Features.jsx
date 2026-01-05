import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { Database, TrendingUp, ShieldAlert, Zap, Check } from 'lucide-react';
import { Container } from '../ui/Container';

const FeatureItem = memo(({ icon: Icon, title, desc, delay }) => (
    <motion.div
        initial={{ opacity: 0, x: -20 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        transition={{ delay }}
        className="flex gap-4 items-start group"
    >
        <div className="bg-indigo-50 dark:bg-indigo-900/20 p-3.5 rounded-2xl shrink-0 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900/40 transition-colors shadow-sm ring-1 ring-inset ring-indigo-500/10 dark:ring-indigo-500/20">
            <Icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
            <h3 className="font-bold text-lg text-slate-900 dark:text-white mb-2">{title}</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{desc}</p>
        </div>
    </motion.div>
));

const Features = () => {
    return (
        <section id="features" className="py-24 bg-white dark:bg-slate-950 overflow-hidden">
            <Container>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center">
                    <div>
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                        >
                            <h2 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white mb-6 tracking-tight">
                                Komplexná analýza v <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">zlomku sekundy</span>.
                            </h2>
                            <p className="text-slate-600 dark:text-slate-400 text-lg mb-12 leading-relaxed max-w-lg">
                                Zatiaľ čo konkurencia hľadá inzeráty manuálne, vy dostávate notifikácie len na tie, ktoré prešli
                                štvorstupňovou kontrolou kvality AI algoritmom.
                            </p>
                        </motion.div>

                        <div className="space-y-8">
                            <FeatureItem
                                delay={0.1}
                                icon={Database}
                                title="Agregácia dát"
                                desc="Zber dát z Bazoš, Autobazar.eu a ďalších portálov do jednej prehľadnej databázy v reálnom čase."
                            />
                            <FeatureItem
                                delay={0.2}
                                icon={TrendingUp}
                                title="Z-Score Analytika"
                                desc="Štatistické vyhodnotenie odchýlky ceny od trhového priemeru pre daný model a rok výroby."
                            />
                            <FeatureItem
                                delay={0.3}
                                icon={ShieldAlert}
                                title="NLP Detekcia rizík"
                                desc="Umelá inteligencia číta popis inzerátu a hľadá kľúčové slová indikujúce technické problémy (klepanie, dym, hrdza)."
                            />
                            <FeatureItem
                                delay={0.4}
                                icon={Zap}
                                title="Real-time Notifikácie"
                                desc="Okamžité upozornenia cez Telegram alebo Email pri nájdení super dealu."
                            />
                        </div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="relative"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl blur-3xl opacity-20 dark:opacity-40 -z-10 transform rotate-3"></div>
                        <div className="bg-slate-50 dark:bg-slate-950/50 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 shadow-2xl">
                            {/* Mock UI for feature visualization */}
                            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 p-6 space-y-6">
                                <div className="flex justify-between items-center pb-6 border-b border-slate-100 dark:border-slate-800">
                                    <span className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
                                        Analýza Inzerátu #4922
                                    </span>
                                    <span className="text-xs bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 px-2.5 py-1 rounded-full font-bold uppercase tracking-wider">
                                        Completed
                                    </span>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-slate-500 dark:text-slate-400 font-medium">Model</span>
                                        <span className="text-slate-900 dark:text-white font-bold bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-lg">Škoda Octavia 2018</span>
                                    </div>
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-slate-500 dark:text-slate-400 font-medium">Cena</span>
                                        <span className="text-slate-900 dark:text-white font-bold">9 500 €</span>
                                    </div>
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-slate-500 dark:text-slate-400 font-medium">Trhový priemer</span>
                                        <span className="text-slate-900 dark:text-white font-bold">13 200 €</span>
                                    </div>
                                </div>

                                <div className="pt-2">
                                    <div className="flex justify-between text-xs font-semibold mb-2">
                                        <span className="text-slate-500 dark:text-slate-400">Výhodnosť kúpy</span>
                                        <span className="text-emerald-600 dark:text-emerald-400">92/100</span>
                                    </div>
                                    <div className="h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            whileInView={{ width: "92%" }}
                                            transition={{ duration: 1.5, ease: "easeOut" }}
                                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                                        />
                                    </div>
                                    <div className="text-xs text-indigo-600 dark:text-indigo-400 font-bold pt-2 text-right">
                                        Potenciálna marža: +3 700 € (28%)
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 flex items-center gap-4 p-4 bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-100 dark:border-emerald-900/20">
                                <div className="bg-emerald-100 dark:bg-emerald-900/30 p-2 rounded-lg text-emerald-600 dark:text-emerald-400">
                                    <Check size={20} strokeWidth={3} />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-slate-900 dark:text-white">Odporúčanie: KÚPIŤ</p>
                                    <p className="text-xs text-slate-600 dark:text-slate-400">Vozidlo je v TOP 5% ponukách trhu.</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </Container>
        </section>
    );
};

export default Features;
