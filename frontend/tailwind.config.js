/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
    './src/app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          DEFAULT: '#0A0A0A',
          lighter: '#1A1A1A',
          light: '#2A2A2A',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#fff',
            a: {
              color: '#8B5CF6',
              '&:hover': {
                color: '#7C3AED',
              },
            },
            strong: {
              color: '#fff',
            },
            h1: {
              color: '#fff',
            },
            h2: {
              color: '#fff',
            },
            h3: {
              color: '#fff',
            },
            h4: {
              color: '#fff',
            },
            code: {
              color: '#fff',
            },
            pre: {
              color: '#fff',
              backgroundColor: '#1A1A1A',
            },
            blockquote: {
              color: '#fff',
            },
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} 