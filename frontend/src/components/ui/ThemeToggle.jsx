import React, { memo, useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

// ------------------ 🚗 Car Icon SVG ------------------
const CarIcon = memo(({ className }) => (
    <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        className={className}
    >
        <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"
        />
    </svg>
));

const ThemeToggle = memo(({ dark, setDark, size = "default", className }) => {
    const [mounted, setMounted] = useState(false);

    // Hydration mismatch fix
    useEffect(() => {
        setMounted(true);
    }, []);

    // Don't render anything until mounted to avoid hydration mismatch
    if (!mounted) {
        return (
            <div className={cn(
                "rounded-xl bg-slate-100 dark:bg-slate-800 animate-pulse",
                size === "lg" ? "w-12 h-12" : "w-10 h-10",
                className
            )} />
        );
    }

    const sizeClasses = size === "lg"
        ? "w-12 h-12 p-2.5"
        : "w-10 h-10 p-2.5";

    return (
        <button
            onClick={() => setDark(!dark)}
            aria-label={dark ? "Prepnúť na svetlý režim" : "Prepnúť na tmavý režim"}
            className={cn(
                sizeClasses,
                "relative overflow-hidden rounded-xl",
                "bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900",
                "border border-slate-200 dark:border-slate-700",
                "hover:border-indigo-300 dark:hover:border-indigo-600",
                "shadow-sm hover:shadow-md",
                "transition-all duration-300 ease-out group",
                className
            )}
        >
            {/* Car Icon with rotation */}
            <CarIcon
                className={cn(
                    "w-full h-full text-slate-600 dark:text-amber-400 transition-all duration-500 ease-out group-hover:scale-110",
                    dark ? "rotate-12 scale-110" : "rotate-0 scale-100"
                )}
            />

            {/* Glow effect on dark mode */}
            {dark && (
                <div className="absolute inset-0 rounded-xl bg-amber-400/20 animate-pulse pointer-events-none" />
            )}

            {/* Sun/Moon indicator */}
            <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-white dark:border-slate-900 shadow-sm flex items-center justify-center overflow-hidden">
                {dark
                    ? <div className="w-full h-full bg-slate-800 flex items-center justify-center"><Sun className="w-2.5 h-2.5 text-amber-400" /></div>
                    : <div className="w-full h-full bg-white flex items-center justify-center"><Moon className="w-2.5 h-2.5 text-indigo-600" /></div>
                }
            </span>
        </button>
    );
});

ThemeToggle.displayName = 'ThemeToggle';

export default ThemeToggle;
