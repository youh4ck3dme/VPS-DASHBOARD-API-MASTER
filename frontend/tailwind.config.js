/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    screens: {
      'xs': '375px',      // iPhone SE
      'sm': '640px',      // Mobil landscape
      'md': '768px',      // Tablet portrait
      'lg': '1024px',     // Tablet landscape / Laptop
      'xl': '1280px',     // Desktop
      '2xl': '1536px',    // Large desktop
      '3xl': '1920px',    // FHD
      '4k': '2560px',     // 4K
    },
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '1.5rem',
        lg: '2rem',
        xl: '3rem',
        '2xl': '4rem',
      },
    },
    extend: {
      colors: {
        // Mapovanie Tailwind farieb na CSS variables
        primary: {
          500: 'rgb(var(--color-primary-500) / <alpha-value>)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      transitionTimingFunction: {
        'spring': 'var(--ease-spring)',
        'out-expo': 'var(--ease-out-expo)',
      }
    },
  },
  plugins: [],
}
