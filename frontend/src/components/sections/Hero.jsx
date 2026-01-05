import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { Container } from '../ui/Container';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

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

const Hero = () => {
    // Basic stats state (could be moved to a context or prop if needed globally)
    const [stats, setStats] = useState({ total_deals: 3274, good_deals: 132 });

    // Simulate fetch stats effect (or replace with real fetch if API logic is moved)
    useEffect(() => {
        // fetchStats logic would go here
    }, []);

    return (
        <section className="relative min-h-[90svh] flex items-center overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-indigo-950/20 pt-20 pb-20">
            {/* Background Elements */}
            <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.05),transparent)]"></div>
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/10 to-transparent"></div>

            <Container>
                <div className="text-center max-w-4xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="flex justify-center mb-8"
                    >
                        <Badge variant="primary" className="pl-2 pr-3 py-1.5 text-sm gap-2 bg-white/50 dark:bg-indigo-950/30 backdrop-blur-sm shadow-sm border-indigo-100 dark:border-indigo-800/50">
                            <span className="relative flex h-2.5 w-2.5">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
                            </span>
                            AI Detekcia Rizík v2.0
                        </Badge>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-8 leading-[1.1]"
                    >
                        Obchodujte s autami na základe{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
                            tvrdých dát
                        </span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="max-w-2xl mx-auto text-xl text-slate-600 dark:text-slate-400 mb-12 leading-relaxed"
                    >
                        Automatizovaný systém, ktorý monitoruje trh 24/7. Analyzuje ceny, marže a riziká v reálnom čase pomocou AI,
                        aby ste vy mohli kupovať len to, čo zarába.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="flex flex-col sm:flex-row justify-center gap-5 mb-20"
                    >
                        <Button size="lg" className="rounded-full shadow-indigo-500/20 shadow-xl px-10 h-14 text-lg group" onClick={() => document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })}>
                            Vyskúšať Demo
                            <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                        <Button size="lg" variant="outline" className="rounded-full px-10 h-14 text-lg bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm border-slate-200 dark:border-slate-800" onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}>
                            Ako to funguje?
                        </Button>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8, delay: 0.5 }}
                        className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-8 border-t border-slate-200/60 dark:border-slate-800/60 max-w-3xl mx-auto"
                    >
                        <div className="text-center">
                            <div className="text-4xl font-bold text-slate-900 dark:text-white mb-1 tracking-tight">
                                <CountUp value={stats.total_deals} className="text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Analyzovaných áut</div>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-slate-900 dark:text-white mb-1 tracking-tight">
                                <CountUp value={stats.good_deals} className="text-emerald-500" />
                            </div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Super dealov</div>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-slate-900 dark:text-white mb-1 tracking-tight">
                                <CountUp value={48} className="text-purple-500" />
                            </div>
                            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Spokojných klientov</div>
                        </div>
                    </motion.div>
                </div>
            </Container>
        </section>
    );
};

export default Hero;
