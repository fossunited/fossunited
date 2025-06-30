import frappeUIPreset from 'frappe-ui/src/tailwind/preset'
import forms from '@tailwindcss/forms'
import typography from '@tailwindcss/typography'

export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        fff: ['"FFF Forward"', 'sans-serif'],
      },
    },
  },
  plugins: [forms, typography],
}
