import React, { memo } from 'react';
import { BarChart3 } from 'lucide-react';
import { Container } from '../ui/Container';

const Footer = memo(() => (
    <footer className="bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 py-16">
        <Container>
            <div className="flex flex-col md:flex-row justify-between items-center gap-8 md:gap-4">
                <div className="flex items-center gap-2.5">
                    <div className="bg-indigo-600 p-1.5 rounded-lg">
                        <BarChart3 className="h-5 w-5 text-white" />
                    </div>
                    <span className="font-bold text-xl text-slate-900 dark:text-white tracking-tight">CarScraper Pro</span>
                </div>

                <div className="flex flex-wrap justify-center gap-8 text-sm font-medium text-slate-500 dark:text-slate-400">
                    <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Ochrana údajov</a>
                    <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Obchodné podmienky</a>
                    <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Podpora</a>
                    <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Kontakt</a>
                </div>

                <div className="text-sm text-slate-400 dark:text-slate-600 font-medium">
                    © {new Date().getFullYear()} DataDriven Solutions s.r.o.
                </div>
            </div>
        </Container>
    </footer>
));

export default Footer;
