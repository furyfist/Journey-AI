/** @type {import('tailwindcss').Config} */
// import typography from '@tailwindcss/typography';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2C3E50',
          light: '#34495E',
          dark: '#1A252F'
        },
        secondary: {
          DEFAULT: '#3498DB',
          light: '#5DADE2',
          dark: '#2874A6'
        },
        accent: {
          DEFAULT: '#E67E22',
          light: '#F39C12',
          dark: '#D35400'
        },
        neutral: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          800: '#1E293B',
          900: '#0F172A'
        },
        cream: {
          50: '#FDFBF7',
          100: '#F9F6F0',
          200: '#F5EFE5',
          300: '#EBE3D5',
          400: '#E0D5C3',
        },
        sage: {
          50: '#F2F5F3',
          100: '#E6EDE9',
          500: '#7C9A8F',
          600: '#5F8276',
          700: '#496961',
        },
        teal: {
          500: '#2A9D8F',
          600: '#238477',
          700: '#1C6960',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Montserrat', 'sans-serif'],
      },
      animation: {
        'gradient-x': 'gradient-x 15s ease infinite',
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'float-slower': 'float 10s ease-in-out infinite',
        blob: "blob 7s infinite",
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        blob: {
          "0%": {
            transform: "translate(0px, 0px) scale(1)",
          },
          "33%": {
            transform: "translate(30px, -50px) scale(1.1)",
          },
          "66%": {
            transform: "translate(-20px, 20px) scale(0.9)",
          },
          "100%": {
            transform: "translate(0px, 0px) scale(1)",
          },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#496961',
            a: {
              color: '#238477',
              '&:hover': {
                color: '#1C6960',
              },
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}