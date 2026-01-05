import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const Container = ({ className, children, ...props }) => {
    return (
        <div
            className={cn(
                'mx-auto w-full max-w-screen-2xl px-4 md:px-6 lg:px-8',
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};

export { Container };
