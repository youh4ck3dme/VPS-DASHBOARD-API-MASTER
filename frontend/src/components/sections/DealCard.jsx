import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Clock, TrendingUp, ShieldAlert, ChevronRight, ArrowUpRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

const DealCard = memo(({ deal, onOpenDetail }) => {
    const isGoodDeal = deal.verdict === "KÚPIŤ";
    const timeAgo = deal.created_at ? new Date(deal.created_at).toLocaleString('sk-SK') : 'Pred chvíľou';

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
            <Card className="h-full flex flex-col overflow-hidden group border-slate-200 dark:border-slate-800">
                <div className="relative h-48 bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    {deal.image_url ? (
                        <img
                            src={deal.image_url}
                            alt={deal.title}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                            loading="lazy"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-400">
                            <BarChart3 className="w-16 h-16 opacity-20" />
                        </div>
                    )}

                    <div className="absolute top-3 right-3">
                        <Badge variant="outline" className="bg-white/90 dark:bg-slate-900/90 backdrop-blur shadow-sm border-0 font-medium">
                            {deal.source || 'Bazoš.sk'}
                        </Badge>
                    </div>
                </div>

                <div className="p-5 flex-1 flex flex-col">
                    <div className="flex justify-between items-start mb-3 gap-2">
                        <h3 className="font-bold text-lg text-slate-900 dark:text-white leading-tight line-clamp-2" title={deal.title}>
                            {deal.title}
                        </h3>
                    </div>

                    <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-4">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{timeAgo}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4 py-3 border-y border-slate-100 dark:border-slate-800">
                        <div>
                            <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-0.5">Cena</p>
                            <p className="text-xl font-extrabold text-slate-900 dark:text-white">
                                {Number(deal.price).toLocaleString()} <span className="text-sm font-normal text-slate-500">€</span>
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-0.5">Trhová</p>
                            <p className="text-base font-semibold text-slate-500 dark:text-slate-400 decoration-slate-300 line-through">
                                {deal.market_value ? Number(deal.market_value).toLocaleString() : 'N/A'} €
                            </p>
                        </div>
                    </div>

                    <div
                        className={`rounded-xl p-3 mb-5 text-sm border ${isGoodDeal
                            ? 'bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-100 dark:border-emerald-900/30'
                            : 'bg-slate-50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700'
                            }`}
                    >
                        <div className="flex justify-between items-center mb-1.5">
                            <span
                                className={`font-bold flex items-center gap-1.5 ${isGoodDeal ? 'text-emerald-700 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-400'
                                    }`}
                            >
                                {isGoodDeal ? <TrendingUp size={16} /> : <ShieldAlert size={16} />}
                                {deal.verdict || 'RIZIKO'}
                            </span>
                            {deal.profit && (
                                <Badge variant={isGoodDeal ? 'success' : 'default'} className="px-1.5 py-0 text-[10px]">
                                    {deal.profit > 0 ? '+' : ''}{Number(deal.profit).toLocaleString()} €
                                </Badge>
                            )}
                        </div>
                        <p
                            className={`text-xs leading-relaxed line-clamp-2 ${isGoodDeal ? 'text-emerald-800/80 dark:text-emerald-200/60' : 'text-slate-500 dark:text-slate-400'
                                }`}
                        >
                            {deal.reason || 'Analýza prebieha...'}
                        </p>
                    </div>

                    <div className="mt-auto flex gap-3">
                        <Button
                            onClick={() => onOpenDetail(deal)}
                            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/20"
                            size="default"
                        >
                            Parametre
                        </Button>
                        <Button
                            variant="outline"
                            size="icon"
                            className="border-slate-200 dark:border-slate-700"
                            onClick={() => window.open(deal.link || '#', '_blank')}
                            title="Otvoriť inzerát"
                        >
                            <ArrowUpRight size={18} className="text-slate-400 dark:text-slate-300" />
                        </Button>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
});

DealCard.displayName = 'DealCard';

export default DealCard;
