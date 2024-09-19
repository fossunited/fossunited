import globals from "globals";
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";

export default [
  { files: ["**/*.{js,mjs,cjs,vue}"] },
  { languageOptions: { globals: { ...globals.browser, ...globals.node } } },
  { env: { browser: true, node: true, es2022: true } },
  pluginJs.configs.recommended,
  ...pluginVue.configs["flat/essential"],
];
