/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Colores principales de AccountIA
        'azul-principal': '#0D47A1',
        'azul-claro': '#E3F2FD',
        'verde-exito': '#2E7D32',
        'rojo-error': '#C62828',
        'amarillo-advertencia': '#FF8F00',
        
        // Paleta de grises
        'gris-900': '#212121',
        'gris-700': '#616161',
        'gris-300': '#E0E0E0',
        'gris-100': '#F5F5F5',
        'gris-50': '#FAFAFA',
        
        // Alias para compatibilidad con Tailwind estándar
        'blue': {
          50: '#E3F2FD',
          600: '#0D47A1',
          700: '#0D47A1',
        },
        'green': {
          50: '#E8F5E8',
          600: '#2E7D32',
          700: '#2E7D32',
        },
        'red': {
          600: '#C62828',
          700: '#C62828',
        },
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'titulo-principal': ['2.25rem', { lineHeight: '2.5rem', fontWeight: '700' }],
        'titulo-seccion': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],
        'subtitulo': ['1.125rem', { lineHeight: '1.75rem', fontWeight: '600' }],
        'cuerpo': ['1rem', { lineHeight: '1.5rem', fontWeight: '400' }],
        'texto-pequeno': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '400' }],
      },
      borderRadius: {
        'accountia': '8px',
      },
      boxShadow: {
        'accountia': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'accountia-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    // Plugins removidos temporalmente para simplificar el setup
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
}
