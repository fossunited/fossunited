import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'

const appName = path.basename(path.resolve('..'))
const outDir = `../${appName}/public/dashboard`

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      // unused here, and its esbuild plugin crashes Vite 8 (rolldown) dep pre-bundling
      codeLanguages: false,
      // frappe-ui's buildConfig plugin requires indexHtmlPath in production
      buildConfig: {
        outDir,
        indexHtmlPath: `../${appName}/www/dashboard.html`,
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir,
    emptyOutDir: true,
  },
  optimizeDeps: {
    include: ['engine.io-client', 'highlight.js/lib/core'],
  },
})
