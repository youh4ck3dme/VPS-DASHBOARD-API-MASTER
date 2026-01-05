import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const Card = forwardRef(({ className, glass = false, hoverEffect = false, children, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn(
                'rounded-2xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-950 dark:text-slate-50 shadow-sm',
                glass && 'bg-white/70 dark:bg-slate-900/70 backdrop-blur-md',
                hoverEffect && 'transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-indigo-500/30 dark:hover:border-indigo-500/30',
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
});

Card.displayName = 'Card';

export { Card };
