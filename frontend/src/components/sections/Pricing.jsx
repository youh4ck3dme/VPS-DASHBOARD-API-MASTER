import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { Container } from '../ui/Container';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';

const Pricing = memo(() => {
    return (
        <section id="pricing" className="py-24 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl pointer-events-none">
                <div className="absolute top-[20%] left-[10%] w-72 h-72 bg-indigo-500/5 rounded-full blur-3xl"></div>
                <div className="absolute bottom-[20%] right-[10%] w-96 h-96 bg-purple-500/5 rounded-full blur-3xl"></div>
            </div>

            <Container className="relative">
                <div className="text-center max-w-2xl mx-auto mb-16">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white mb-6 tracking-tight"
                    >
                        Transparentné ceny
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-slate-600 dark:text-slate-400"
                    >
                        Žiadne skryté poplatky. Plaťte len za to, čo využijete. Investícia, ktorá sa vráti pri prvom nákupe.
                    </motion.p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start max-w-6xl mx-auto">
                    {/* Starter Plan */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                    >
                        <Card className="p-8 h-full flex flex-col hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Starter</h3>
                            <div className="mb-6 flex items-baseline gap-1">
                                <span className="text-4xl font-black text-slate-900 dark:text-white">49€</span>
                                <span className="text-slate-500 dark:text-slate-400 font-medium">/mes</span>
                            </div>
                            <ul className="space-y-4 mb-8 flex-1">
                                {[
                                    '100 analýz denne',
                                    'Email notifikácie',
                                    'Základný filter',
                                    'Historické ceny (30 dní)'
                                ].map((item) => (
                                    <li key={item} className="flex items-center text-sm text-slate-600 dark:text-slate-300">
                                        <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-3 shrink-0" /> {item}
                                    </li>
                                ))}
                            </ul>
                            <Button variant="outline" className="w-full" size="lg">
                                Vybrať Starter
                            </Button>
                        </Card>
                    </motion.div>

                    {/* Professional Plan */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="relative z-10"
                    >
                        <div className="absolute -inset-[2px] rounded-[24px] bg-gradient-to-b from-indigo-500 to-purple-600 -z-10 blur-sm opacity-50"></div>
                        <Card className="p-8 h-full flex flex-col border-0 relative shadow-2xl bg-white dark:bg-slate-900">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                <Badge className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-0 px-4 py-1.5 shadow-lg shadow-indigo-500/20">
                                    NAJPOPULÁRNEJŠIE
                                </Badge>
                            </div>

                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2 mt-2">Professional</h3>
                            <div className="mb-6 flex items-baseline gap-1">
                                <span className="text-5xl font-black text-slate-900 dark:text-white">99€</span>
                                <span className="text-slate-500 dark:text-slate-400 font-medium">/mes</span>
                            </div>

                            <ul className="space-y-4 mb-8 flex-1">
                                {[
                                    'Neobmedzené analýzy',
                                    'Instantné Telegram notifikácie',
                                    'AI detekcia rizík (NLP)',
                                    'Prednostný support',
                                    'TOP 6 Dňa prístup'
                                ].map((item) => (
                                    <li key={item} className="flex items-center text-sm font-medium text-slate-900 dark:text-white">
                                        <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-3 shrink-0" /> {item}
                                    </li>
                                ))}
                            </ul>

                            <Button className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white border-0 shadow-lg shadow-indigo-500/25" size="lg">
                                Vybrať Professional
                            </Button>
                        </Card>
                    </motion.div>

                    {/* Enterprise Plan */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3 }}
                    >
                        <Card className="p-8 h-full flex flex-col hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Enterprise</h3>
                            <div className="mb-6 flex items-baseline gap-1">
                                <span className="text-4xl font-black text-slate-900 dark:text-white">249€</span>
                                <span className="text-slate-500 dark:text-slate-400 font-medium">/mes</span>
                            </div>
                            <ul className="space-y-4 mb-8 flex-1">
                                {[
                                    'API Prístup',
                                    'Export dát (CSV, XML)',
                                    'Dedikovaná podpora',
                                    'White-label reporty',
                                    'Vlastné integrácie'
                                ].map((item) => (
                                    <li key={item} className="flex items-center text-sm text-slate-600 dark:text-slate-300">
                                        <Check className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mr-3 shrink-0" /> {item}
                                    </li>
                                ))}
                            </ul>
                            <Button variant="outline" className="w-full" size="lg">
                                Kontaktovať obchod
                            </Button>
                        </Card>
                    </motion.div>
                </div>
            </Container>
        </section>
    );
});

export default Pricing;
