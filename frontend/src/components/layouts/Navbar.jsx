import React, { useState, useEffect, memo } from 'react';
import { Menu, X } from 'lucide-react';
import ParallaxLogo from '../ParallaxLogo'; // Assuming this stays or moved
import ThemeToggle from '../ui/ThemeToggle';
import { Button } from '../ui/Button';

// Helper hook if not present in separate file yet
const useDarkMode = () => {
    const [dark, setDark] = useState(() => {
        if (typeof window === 'undefined') return false;
        const ls = localStorage.getItem('carScraperTheme');
        return ls ? ls === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    });

    useEffect(() => {
        if (typeof window !== 'undefined') {
            document.documentElement.classList.toggle('dark', dark);
            localStorage.setItem('carScraperTheme', dark ? 'dark' : 'light');
        }
    }, [dark]);

    return [dark, setDark];
};

const Navbar = memo(({ onLinkClick }) => {
    const [mobile, setMobile] = useState(false);
    const [dark, setDark] = useDarkMode();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <header className={`sticky top-0 z-50 transition-all duration-300 ${scrolled
                ? 'bg-white/90 dark:bg-slate-950/90 backdrop-blur-md border-b border-slate-200/60 dark:border-slate-800/60 shadow-sm'
                : 'bg-transparent border-transparent'
            }`}>
            <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
                <a href="#" className="flex items-center group">
                    {/* If ParallaxLogo depends on imports, we might need to update it too. For now assume it works or imports are adjusted in App */}
                    <ParallaxLogo />
                </a>

                <ul className="hidden md:flex items-center gap-10 text-sm font-semibold">
                    {['Live Feed', 'Funkcie', 'Cenník'].map((t) => (
                        <li key={t}>
                            <a
                                href={`#${t.toLowerCase().replace(' ', '')}`}
                                onClick={onLinkClick}
                                className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-white transition-colors relative group"
                            >
                                {t}
                                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-indigo-600 transition-all duration-300 group-hover:w-full"></span>
                            </a>
                        </li>
                    ))}
                </ul>

                <div className="flex items-center gap-4">
                    <div className="hidden md:block">
                        <ThemeToggle dark={dark} setDark={setDark} />
                    </div>
                    <Button
                        className="hidden md:flex bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 shadow-none hover:shadow-lg"
                    >
                        Začať zdarma
                    </Button>
                    <button
                        onClick={() => setMobile(!mobile)}
                        className="md:hidden p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                        aria-label="Toggle menu"
                    >
                        {mobile ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            {mobile && (
                <div className="md:hidden bg-white/95 dark:bg-slate-950/95 backdrop-blur-xl border-t border-slate-200 dark:border-slate-800 absolute w-full left-0 shadow-2xl">
                    <div className="p-4 space-y-2">
                        {['Live Feed', 'Funkcie', 'Cenník'].map((t) => (
                            <a
                                key={t}
                                href={`#${t.toLowerCase().replace(' ', '')}`}
                                onClick={(e) => { setMobile(false); onLinkClick(e); }}
                                className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-xl transition-colors font-medium"
                            >
                                {t}
                            </a>
                        ))}
                    </div>
                    {/* Mobile Theme Toggle */}
                    <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                            {dark ? '🌙 Tmavý režim' : '☀️ Svetlý režim'}
                        </span>
                        <ThemeToggle dark={dark} setDark={setDark} size="lg" />
                    </div>
                    <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                        <Button className="w-full h-12 text-base">Začať zdarma</Button>
                    </div>
                </div>
            )}
        </header>
    );
});

export default Navbar;
