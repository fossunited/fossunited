import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true,
    }),
    vue(),
    VitePWA({
      workbox: {
        maximumFileSizeToCacheInBytes: 5 * 1024 ** 2, // 5MB ; default 2MB
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve('..'))}/public/dashboard`,
    emptyOutDir: true,
    target: 'es2015',
  },
  optimizeDeps: {
    include: [
      'frappe-ui > feather-icons',
      'showdown',
      'engine.io-client',
      'highlight.js/lib/core',
    ],
  },
})
