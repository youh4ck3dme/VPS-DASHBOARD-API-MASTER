import React, { useRef, useState, useEffect } from 'react';

const ParallaxLogo = ({ className = "" }) => {
    const svgRef = useRef(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [isHovered, setIsHovered] = useState(false);

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isHovered || !svgRef.current) return;

            const rect = svgRef.current.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            setMousePos({ x, y });
        };

        const handleMouseLeave = () => {
            setIsHovered(false);
            setMousePos({ x: 0, y: 0 }); // Reset position
        };

        if (svgRef.current) {
            svgRef.current.addEventListener('mousemove', handleMouseMove);
            svgRef.current.addEventListener('mouseleave', handleMouseLeave);
            svgRef.current.addEventListener('mouseenter', () => setIsHovered(true));
        }

        return () => {
            if (svgRef.current) {
                svgRef.current.removeEventListener('mousemove', handleMouseMove);
                svgRef.current.removeEventListener('mouseleave', handleMouseLeave);
                svgRef.current.removeEventListener('mouseenter', () => setIsHovered(true));
            }
            // Fallback for global mouse move if needed, but local is better for a logo
        };
    }, [isHovered]);

    // Parallax calculations (dampening factors)
    const bgX = mousePos.x * 10;
    const bgY = mousePos.y * 10;

    const midX = mousePos.x * 20;
    const midY = mousePos.y * 20;

    const fgX = mousePos.x * 40;
    const fgY = mousePos.y * 40;

    return (
        <div
            className={`relative cursor-pointer group ${className}`}
            style={{ perspective: '1000px' }}
            ref={svgRef}
        >
            <svg
                width="240"
                height="60"
                viewBox="0 0 240 60"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="overflow-visible transition-transform duration-200 ease-out"
            >
                <defs>
                    <linearGradient id="chromeGradient" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor="#e0e7ff" />
                        <stop offset="50%" stopColor="#6366f1" />
                        <stop offset="100%" stopColor="#4338ca" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Layer 1: Background Elements (Slowest) */}
                <g
                    style={{ transform: `translate(${-bgX}px, ${-bgY}px)` }}
                    className="transition-transform duration-100 ease-out opacity-20 dark:opacity-10"
                >
                    <path d="M20 30 H220" stroke="currentColor" strokeWidth="1" strokeDasharray="4 4" className="text-gray-400" />
                    <path d="M30 15 L210 15" stroke="currentColor" strokeWidth="0.5" className="text-gray-300" />
                    <path d="M30 45 L210 45" stroke="currentColor" strokeWidth="0.5" className="text-gray-300" />
                </g>

                {/* Layer 2: Middle Elements (Car Silhouette / Abstract Shape) */}
                <g
                    style={{ transform: `translate(${-midX}px, ${-midY}px)` }}
                    className="transition-transform duration-100 ease-out text-indigo-500"
                >
                    {/* Abstract Speedometer / Car Hood curve */}
                    <path
                        d="M45 40 Q 55 35, 65 40 T 85 40"
                        stroke="url(#chromeGradient)"
                        strokeWidth="3"
                        strokeLinecap="round"
                        fill="none"
                        filter="url(#glow)"
                    />
                    <circle cx="50" cy="38" r="12" stroke="currentColor" strokeWidth="2" className="opacity-80" />
                    <path d="M50 38 L58 32" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </g>

                {/* Layer 3: Foreground Text (Fastest) */}
                <g
                    style={{ transform: `translate(${-fgX}px, ${-fgY}px)` }}
                    className="transition-transform duration-100 ease-out"
                >
                    <text
                        x="75"
                        y="38"
                        fontFamily="system-ui, -apple-system, sans-serif"
                        fontWeight="900"
                        fontSize="24"
                        className="fill-gray-900 dark:fill-white"
                        style={{ textShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                    >
                        CarScraper
                    </text>
                    <text
                        x="205"
                        y="38"
                        fontFamily="system-ui, -apple-system, sans-serif"
                        fontWeight="900"
                        fontSize="24"
                        className="fill-indigo-600 dark:fill-indigo-400"
                        style={{ textShadow: '0 0 20px rgba(99, 102, 241, 0.5)' }}
                    >
                        Pro
                    </text>

                    {/* Small accent dot */}
                    <circle cx="200" cy="22" r="3" fill="#ef4444" className="animate-pulse" />
                </g>
            </svg>
        </div>
    );
};

export default ParallaxLogo;
