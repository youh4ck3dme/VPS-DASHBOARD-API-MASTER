import React, { useState } from 'react';

const REGIONS = [
    { id: 'BL', name: 'Bratislavský', color: '#6366f1', path: 'M30,120 L50,110 L60,125 L40,140 Z', cx: 45, cy: 125 },
    { id: 'TT', name: 'Trnavský', color: '#8b5cf6', path: 'M50,110 L90,90 L100,120 L60,125 Z', cx: 75, cy: 110 },
    { id: 'TN', name: 'Trenčiansky', color: '#ec4899', path: 'M90,90 L130,60 L140,100 L100,120 Z', cx: 115, cy: 90 },
    { id: 'NR', name: 'Nitriansky', color: '#14b8a6', path: 'M100,120 L140,100 L160,130 L110,145 Z', cx: 130, cy: 125 },
    { id: 'ZA', name: 'Žilinský', color: '#f59e0b', path: 'M130,60 L200,50 L210,90 L140,100 Z', cx: 170, cy: 75 },
    { id: 'BB', name: 'Banskobystrický', color: '#ef4444', path: 'M140,100 L210,90 L220,130 L160,130 Z', cx: 180, cy: 115 },
    { id: 'PO', name: 'Prešovský', color: '#3b82f6', path: 'M200,50 L320,50 L310,90 L210,90 Z', cx: 260, cy: 70 },
    { id: 'KE', name: 'Košický', color: '#10b981', path: 'M210,90 L310,90 L300,130 L220,130 Z', cx: 260, cy: 110 },
];

// Simplified stylized coordinates (NOT geographically accurate, but topologically topological-ish)
// A real map would look better, but without downloading a huge Path string, this stylized version is functional.
// Actually, let's try to make it look a BIT more like Slovakia. 
// Slovakia is elongated W-E.
// BL is small SW.
// ...
// Let's use a "Tech/Cyber" style map with Hexagons/Polygons that roughly approximate location.

const SlovakiaMap = ({ onRegionSelect, selectedRegion, deals = [] }) => {
    const [hoveredRegion, setHoveredRegion] = useState(null);

    // Calculate region counts
    const regionCounts = React.useMemo(() => {
        const counts = {};
        deals.forEach(deal => {
            if (deal.region) {
                counts[deal.region] = (counts[deal.region] || 0) + 1;
            }
        });
        return counts;
    }, [deals]);

    return (
        <div className="w-full max-w-4xl mx-auto p-4 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm relative overflow-hidden">
            <div className="absolute top-2 left-4 text-xs font-mono text-gray-500 uppercase tracking-widest">
                Interactive Map v2.0 - Realtime Data
            </div>

            <svg viewBox="0 0 350 160" className="w-full h-auto drop-shadow-xl filter">
                <defs>
                    <filter id="glow-map" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="3" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>

                {REGIONS.map((region) => {
                    const isSelected = selectedRegion === region.name;
                    const isHovered = hoveredRegion === region.id;
                    const count = regionCounts[region.name] || 0;

                    return (
                        <g
                            key={region.id}
                            onClick={() => onRegionSelect(isSelected ? null : region.name)}
                            onMouseEnter={() => setHoveredRegion(region.id)}
                            onMouseLeave={() => setHoveredRegion(null)}
                            className="cursor-pointer transition-all duration-300"
                            style={{ transformOrigin: 'center' }}
                        >
                            <path
                                d={region.path}
                                fill={isSelected ? region.color : (isHovered ? region.color : '#cbd5e1')}
                                className={`transition-colors duration-300 ease-out ${isSelected || isHovered ? 'opacity-100' : 'opacity-30 dark:opacity-20 hover:opacity-80'}`}
                                stroke="white"
                                strokeWidth={isSelected ? 3 : 1}
                                strokeLinejoin="round"
                            />

                            {/* Label */}
                            <text
                                x={region.cx}
                                y={region.cy - 2}
                                textAnchor="middle"
                                className={`text-[9px] font-bold pointer-events-none transition-all duration-300 ${isSelected || isHovered ? 'fill-white' : 'fill-gray-600 dark:fill-gray-400'}`}
                            >
                                {region.id}
                            </text>
                            {count > 0 && (
                                <text
                                    x={region.cx}
                                    y={region.cy + 8}
                                    textAnchor="middle"
                                    className={`text-[8px] font-medium pointer-events-none ${isSelected || isHovered ? 'fill-white' : 'fill-indigo-600 dark:fill-indigo-400'}`}
                                >
                                    ({count})
                                </text>
                            )}
                        </g>
                    );
                })}
            </svg>

            {/* Legend / Tooltip */}
            <div className="absolute bottom-4 right-4 text-right">
                <div className="text-sm font-bold text-gray-900 dark:text-white">
                    {REGIONS.find(r => r.name === selectedRegion)?.name || REGIONS.find(r => r.id === hoveredRegion)?.name || "Vyberte kraj"}
                    {(selectedRegion || hoveredRegion) && (
                        <span className="ml-2 text-indigo-600 dark:text-indigo-400">
                            ({regionCounts[selectedRegion || REGIONS.find(r => r.id === hoveredRegion)?.name] || 0} aut)
                        </span>
                    )}
                </div>
                <div className="text-xs text-gray-500">
                    {selectedRegion ? 'Kliknutím zrušíte výber' : 'Kliknite pre filtrovanie regiónu'}
                </div>
            </div>
        </div>
    );
};

export default SlovakiaMap;
