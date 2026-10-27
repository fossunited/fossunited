import frappeUIPreset, { content as frappeUIContent } from 'frappe-ui/tailwind'

export default {
  // frappe-ui's preset selector
  darkMode: ['selector', '[data-theme="dark"]'],

  presets: [frappeUIPreset],
  // Tailwind v3 does not merge a preset's `content`, so frappe-ui exports its
  // own source globs for us to spread in.
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}', ...frappeUIContent],
  theme: {
    extend: {
      fontFamily: {
        fff: ['"FFF Forward"', 'sans-serif'],
      },
      // Previously this block also defined a custom `colors` map (`bg-base`,
      // `text-ink-1`, `bg-status-*`, etc.) bridging to `var(--color-*)` CSS
      // vars for dark-mode support, from before frappe-ui's own preset had a
      // full semantic token system. None of those vars were ever defined and
      // nothing in src/ used the resulting classes. frappe-ui v1's preset now
      // ships the real thing (ink-gray-*, surface-gray-*, outline-gray-* etc,
      // all flipping on [data-theme="dark"]), so it was removed rather than
      // carried forward.
      // TODO: replace espresso with jeswin's v3 color palette in stage 2.
    },
  },
  // @tailwindcss/forms and @tailwindcss/typography are registered by the
  // frappe-ui preset itself (and are only transitive deps here), so they are
  // not listed again.
}
