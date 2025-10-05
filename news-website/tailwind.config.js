module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        ink: '#111111',
        parchment: '#f7f5f2',
        accent: '#c53030'
      },
      fontFamily: {
        serif: ['var(--font-serif)', 'Georgia', 'serif'],
        sans: ['var(--font-sans)', 'Arial', 'sans-serif']
      },
      boxShadow: {
        subtle: '0 8px 24px rgba(17, 17, 17, 0.08)'
      }
    }
  },
  plugins: []
};
