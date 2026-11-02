/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'neo-bg': '#F7F4EB',
        'neo-surface': '#FFFFFF',
        'neo-surface-warm': '#FFFDF8',
        'neo-black': '#121212',
        'neo-border': '#121212',
        'neo-yellow': '#FFE600',
        'neo-yellow-hover': '#F5DC00',
        'neo-mint': '#2DD4BF',
        'neo-mint-hover': '#14B8A6',
        'neo-lime': '#CCFF00',
        'neo-indigo': '#6366F1',
        'neo-purple': '#8B5CF6',
        'neo-coral': '#FF6B4A',
        'neo-pink': '#FF66C4',
        'neo-muted': '#6B7280',
        'neo-gray-light': '#F3F4F6',
        'neo-gray': '#E5E7EB',
      },
      boxShadow: {
        'neo-sm': '2px 2px 0px 0px #121212',
        'neo': '4px 4px 0px 0px #121212',
        'neo-lg': '6px 6px 0px 0px #121212',
        'neo-xl': '8px 8px 0px 0px #121212',
        'neo-yellow': '4px 4px 0px 0px #FFE600',
        'neo-mint': '4px 4px 0px 0px #2DD4BF',
        'neo-coral': '4px 4px 0px 0px #FF6B4A',
      },
      borderWidth: {
        '2.5': '2.5px',
        '3': '3px',
      },
      fontFamily: {
        sans: ['"Space Grotesk"', '"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        'neo': '16px',
        'neo-sm': '8px',
        'neo-lg': '24px',
        'neo-xl': '32px',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
  ],
}
