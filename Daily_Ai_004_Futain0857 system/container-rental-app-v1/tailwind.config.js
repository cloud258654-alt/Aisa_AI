/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: {
            950: '#021341',
            900: '#091945',
            800: '#101e45',
          },
          slate: {
            700: '#333d57',
          },
          gold: {
            600: '#81765f',
            500: '#9b9074',
            300: '#c0b19b',
          }
        },
        surface: {
          page: '#f3f6fa',
          card: '#ffffff',
          muted: '#eef2f7',
        },
        border: {
          default: '#d9e1ec',
        },
        text: {
          primary: '#172033',
          secondary: '#667085',
          ondark: '#ffffff',
        },
        status: {
          success: '#15803d',
          warning: '#b7791f',
          danger: '#b42318',
          info: '#2563eb',
        }
      }
    },
  },
  plugins: [],
}
