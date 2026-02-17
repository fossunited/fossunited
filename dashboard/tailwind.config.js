import frappeUIPreset from 'frappe-ui/src/tailwind/preset'
import forms from '@tailwindcss/forms'
import typography from '@tailwindcss/typography'

export default {
  // frappe-ui's preset selector
  darkMode: ['selector', '[data-theme="dark"]'],

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
      // frappe-ui's plugin already registers all semantic color utilities:
      //   text-ink-gray-1..9, text-ink-green-*, text-ink-red-*, text-ink-blue-* etc.
      //   bg-surface-white, bg-surface-gray-1..7, bg-surface-cards/modal/menu-bar
      //   bg-surface-green-*, bg-surface-red-*, bg-surface-blue-* etc.
      //   border-outline-gray-1..5, border-outline-red/green/blue/amber etc.
      // All backed by CSS variables that flip on [data-theme="dark"].
      colors: {
        // ── frappe-ui ink-gray remapping ──────────────────────────────────────
        // frappe-ui's preset defines ink-gray-1 through ink-gray-9 as hardcoded
        // hex values. We override them here to point at our CSS variables so they
        // automatically flip in dark mode.
        // ink-gray-9 is the darkest (near-black in light mode → near-white in dark)
        'ink-gray': {
          1: 'var(--color-ink-6)', // lightest  #9CA3AF → gray-400
          2: 'var(--color-ink-6)',
          3: 'var(--color-ink-5)', // #6B7280 → gray-500
          4: 'var(--color-ink-5)',
          5: 'var(--color-ink-4)', // #4B5563 → gray-600
          6: 'var(--color-ink-4)',
          7: 'var(--color-ink-3)', // #374151 → gray-700
          8: 'var(--color-ink-2)', // #1F2937 → gray-800
          9: 'var(--color-ink-1)', // darkest  #111827 → gray-900 (was invisible in dark mode)
        },

        // ── Surfaces ──────────────────────────────────────────────────────────
        // bg-base          → page canvas
        // bg-surface       → cards, panels, inputs
        // bg-surface-alt   → subtle panels (event headers)
        // bg-raised        → list rows, sidebar bg
        // bg-overlay       → active nav item, toolbar buttons
        // bg-muted         → badges, tag backgrounds, dividers
        base: 'var(--color-base)',
        surface: 'var(--color-surface)',
        'surface-alt': 'var(--color-surface-alt)',
        raised: 'var(--color-raised)',
        overlay: 'var(--color-overlay)',
        muted: 'var(--color-muted)',

        // ── Borders ───────────────────────────────────────────────────────────
        // border-border     → default border (was gray-200/300)
        // border-border-mid → stronger border (was gray-400/500)
        border: 'var(--color-border)', // NOTE: extends, not replaces
        'border-mid': 'var(--color-border-mid)',

        // ── Ink (text + dark inverted surfaces) ───────────────────────────────
        // text-ink-1  → headings, primary text         (was gray-900 / black)
        // text-ink-2  → body strong                    (was gray-800)
        // text-ink-3  → body                           (was gray-700)
        // text-ink-4  → secondary / captions           (was gray-600)
        // text-ink-5  → placeholder                    (was gray-500)
        // text-ink-6  → disabled                       (was gray-400)
        //
        // Also used for dark inverted surfaces:
        // bg-ink-1 → dark sidebars/headers/badges      (was bg-gray-900 / bg-black)
        // bg-ink-2 → slightly lighter dark surface     (was bg-gray-800)
        ink: {
          1: 'var(--color-ink-1)',
          2: 'var(--color-ink-2)',
          3: 'var(--color-ink-3)',
          4: 'var(--color-ink-4)',
          5: 'var(--color-ink-5)',
          6: 'var(--color-ink-6)',
        },

        // ── On-ink ────────────────────────────────────────────────────────────
        // text-on-ink       → text/icons ON dark bg-ink-* surfaces (was text-white)
        // text-on-ink-muted → secondary text on dark bg            (was text-gray-300)
        // White in both light and dark mode — does NOT flip.
        'on-ink': 'var(--color-on-ink)',
        'on-ink-muted': 'var(--color-on-ink-muted)',

        // ── Status colors ─────────────────────────────────────────────────────
        // bg-status-success-bg  + text-status-success-txt  (was green-100 / green-800)
        // bg-status-error-bg    + text-status-error-txt    (was red-100   / red-800)
        // bg-status-warn-bg     + text-status-warn-txt     (was yellow-50 / yellow-700)
        // bg-status-info-bg     + text-status-info-txt     (was blue-50   / blue-800)
        // bg-status-orange-bg   + text-status-orange-txt   (was orange-50 / orange-600)
        // bg-status-amber-bg    + text-status-amber-txt    (was amber-50  / amber-700)
        // bg-status-purple-bg   + text-status-purple-txt   (was purple-100/ purple-900)
        status: {
          'success-bg': 'var(--color-status-success-bg)',
          'success-txt': 'var(--color-status-success-txt)',
          'success-mid': 'var(--color-status-success-mid)',
          'error-bg': 'var(--color-status-error-bg)',
          'error-txt': 'var(--color-status-error-txt)',
          'error-mid': 'var(--color-status-error-mid)',
          'warn-bg': 'var(--color-status-warn-bg)',
          'warn-txt': 'var(--color-status-warn-txt)',
          'info-bg': 'var(--color-status-info-bg)',
          'info-txt': 'var(--color-status-info-txt)',
          'info-mid': 'var(--color-status-info-mid)',
          'orange-bg': 'var(--color-status-orange-bg)',
          'orange-txt': 'var(--color-status-orange-txt)',
          'amber-bg': 'var(--color-status-amber-bg)',
          'amber-txt': 'var(--color-status-amber-txt)',
          'purple-bg': 'var(--color-status-purple-bg)',
          'purple-txt': 'var(--color-status-purple-txt)',
        },
      },
    },
  },
  plugins: [forms, typography],
}
