// ESLint only checks Vue templates, which Oxlint cannot parse. All JS rules,
// including <script> blocks, run in Oxlint (.oxlintrc.json); eslint-plugin-oxlint
// turns off the ESLint rules Oxlint already covers.
import pluginVue from 'eslint-plugin-vue'
import prettierConfig from 'eslint-config-prettier'
import oxlint from 'eslint-plugin-oxlint'

export default [
  {
    ignores: [
      '**/node_modules/**',
      'fossunited/public/dist/**',
      'fossunited/public/dashboard/**',
      'fossunited/dev/**',
      'frappe_docker/**',
      'development/**',
    ],
  },
  ...pluginVue.configs['flat/recommended'],
  // Turns off eslint-plugin-vue's layout rules; Oxfmt owns formatting.
  prettierConfig,
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      // frappe-ui uses names such as "Input" and "Button" for its components.
      'vue/no-reserved-component-names': 'off',
      'vue/no-v-html': 'off',
    },
  },
  ...oxlint.buildFromOxlintConfigFile('./.oxlintrc.json'),
]
