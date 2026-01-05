import React, { memo } from 'react';
import { X, BarChart3, Database, ArrowUpRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

const DealDetailModal = memo(({ deal, onClose }) => {
    if (!deal) return null;

    const specs = deal.full_specs || {};
    const basic = specs.basic_info || {};
    const tech = specs.technical_details || {};
    // const condition = specs.condition || {}; // Unused for now
    const equipment = specs.equipment || {};

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6" onClick={onClose}>
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
                />

                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                    className="relative bg-white dark:bg-slate-900 w-full max-w-5xl max-h-[85vh] overflow-hidden rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col"
                >
                    {/* Header */}
                    <div className="sticky top-0 z-10 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
                        <div className="flex items-center gap-4 min-w-0">
                            <div className="bg-indigo-50 dark:bg-indigo-900/30 p-2.5 rounded-xl shrink-0">
                                <BarChart3 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <div className="min-w-0">
                                <h2 className="text-xl font-bold text-slate-900 dark:text-white truncate">
                                    {deal.title}
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400">ID: #{deal.id} • {deal.source}</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors shrink-0"
                        >
                            <X className="w-6 h-6 text-slate-500" />
                        </button>
                    </div>

                    <div className="overflow-y-auto p-0 flex-1">
                        <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
                            {/* Left Column: Image & Basic Info */}
                            <div className="space-y-8">
                                <div className="aspect-video w-full rounded-2xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-inner relative group">
                                    {deal.image_url ? (
                                        <img src={deal.image_url} alt={deal.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-slate-400">
                                            <Database size={48} />
                                        </div>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-2xl border border-slate-100 dark:border-slate-700/50">
                                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1 tracking-wider">Cena</span>
                                        <span className="text-3xl font-black text-indigo-600 dark:text-indigo-400 tracking-tight">{Number(deal.price).toLocaleString()} €</span>
                                    </div>
                                    <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-2xl border border-slate-100 dark:border-slate-700/50">
                                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1 tracking-wider">Nájazd</span>
                                        <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">{Number(deal.km || basic.km || 0).toLocaleString()} <span className="text-lg text-slate-500 font-medium">km</span></span>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
                                        Popis inzerátu
                                    </h3>
                                    <div className="p-5 bg-slate-50 dark:bg-slate-800/30 rounded-2xl text-sm text-slate-600 dark:text-slate-400 leading-relaxed border border-slate-100 dark:border-slate-800">
                                        {deal.description || "Predajca neuviedol žiadny popis."}
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Parameters */}
                            <div className="space-y-8">
                                <div className="bg-white dark:bg-slate-800/20 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                                    <div className="bg-slate-50 dark:bg-slate-800/80 px-5 py-3 border-b border-slate-200 dark:border-slate-700">
                                        <h3 className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Technické špecifikácie</h3>
                                    </div>
                                    <div className="divide-y divide-slate-100 dark:divide-slate-700/50">
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
                                            <div key={i} className="flex justify-between items-center px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                                                <span className="text-sm text-slate-500 font-medium">{p.label}</span>
                                                <span className="text-sm font-bold text-slate-900 dark:text-white">{p.val}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {equipment.other_features && equipment.other_features.length > 0 && (
                                    <div>
                                        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-4">Výbava</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {equipment.other_features.map((item, idx) => (
                                                <Badge key={idx} variant="default" className="bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700">
                                                    {item.trim()}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="pt-6">
                                    <Button
                                        onClick={() => window.open(deal.link, '_blank')}
                                        className="w-full h-14 text-base shadow-xl shadow-indigo-500/20"
                                        size="lg"
                                    >
                                        Otvoriť inzerát na {deal.source} <ArrowUpRight className="ml-2 w-5 h-5" />
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
});

DealDetailModal.displayName = 'DealDetailModal';

export default DealDetailModal;
