// vite.config.js
import { defineConfig } from "file:///C:/Users/psdan/OneDrive/Desktop/study%20stuff/projects%20(competitions)/FOSS_united/fossunited/dashboard/node_modules/vite/dist/node/index.js";
import vue from "file:///C:/Users/psdan/OneDrive/Desktop/study%20stuff/projects%20(competitions)/FOSS_united/fossunited/dashboard/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
import frappeui from "file:///C:/Users/psdan/OneDrive/Desktop/study%20stuff/projects%20(competitions)/FOSS_united/fossunited/dashboard/node_modules/frappe-ui/vite/index.js";
var __vite_injected_original_dirname = "C:\\Users\\psdan\\OneDrive\\Desktop\\study stuff\\projects (competitions)\\FOSS_united\\fossunited\\dashboard";
var vite_config_default = defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true
    }),
    vue()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "src")
    }
  },
  build: {
    outDir: `../${path.basename(path.resolve(".."))}/public/dashboard`,
    emptyOutDir: true,
    target: "es2015"
  },
  optimizeDeps: {
    include: [
      "frappe-ui > feather-icons",
      "showdown",
      "engine.io-client",
      "highlight.js/lib/core"
    ]
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxwc2RhblxcXFxPbmVEcml2ZVxcXFxEZXNrdG9wXFxcXHN0dWR5IHN0dWZmXFxcXHByb2plY3RzIChjb21wZXRpdGlvbnMpXFxcXEZPU1NfdW5pdGVkXFxcXGZvc3N1bml0ZWRcXFxcZGFzaGJvYXJkXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxwc2RhblxcXFxPbmVEcml2ZVxcXFxEZXNrdG9wXFxcXHN0dWR5IHN0dWZmXFxcXHByb2plY3RzIChjb21wZXRpdGlvbnMpXFxcXEZPU1NfdW5pdGVkXFxcXGZvc3N1bml0ZWRcXFxcZGFzaGJvYXJkXFxcXHZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9Vc2Vycy9wc2Rhbi9PbmVEcml2ZS9EZXNrdG9wL3N0dWR5JTIwc3R1ZmYvcHJvamVjdHMlMjAoY29tcGV0aXRpb25zKS9GT1NTX3VuaXRlZC9mb3NzdW5pdGVkL2Rhc2hib2FyZC92aXRlLmNvbmZpZy5qc1wiO2ltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gJ3ZpdGUnXHJcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xyXG5pbXBvcnQgcGF0aCBmcm9tICdwYXRoJ1xyXG5pbXBvcnQgZnJhcHBldWkgZnJvbSAnZnJhcHBlLXVpL3ZpdGUnXHJcblxyXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xyXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xyXG4gIHBsdWdpbnM6IFtcclxuICAgIGZyYXBwZXVpKHtcclxuICAgICAgZnJhcHBlUHJveHk6IHRydWUsXHJcbiAgICAgIGx1Y2lkZUljb25zOiB0cnVlLFxyXG4gICAgfSksXHJcbiAgICB2dWUoKSxcclxuICBdLFxyXG4gIHJlc29sdmU6IHtcclxuICAgIGFsaWFzOiB7XHJcbiAgICAgICdAJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJ3NyYycpLFxyXG4gICAgfSxcclxuICB9LFxyXG4gIGJ1aWxkOiB7XHJcbiAgICBvdXREaXI6IGAuLi8ke3BhdGguYmFzZW5hbWUocGF0aC5yZXNvbHZlKCcuLicpKX0vcHVibGljL2Rhc2hib2FyZGAsXHJcbiAgICBlbXB0eU91dERpcjogdHJ1ZSxcclxuICAgIHRhcmdldDogJ2VzMjAxNScsXHJcbiAgfSxcclxuICBvcHRpbWl6ZURlcHM6IHtcclxuICAgIGluY2x1ZGU6IFtcclxuICAgICAgJ2ZyYXBwZS11aSA+IGZlYXRoZXItaWNvbnMnLFxyXG4gICAgICAnc2hvd2Rvd24nLFxyXG4gICAgICAnZW5naW5lLmlvLWNsaWVudCcsXHJcbiAgICAgICdoaWdobGlnaHQuanMvbGliL2NvcmUnLFxyXG4gICAgXSxcclxuICB9LFxyXG59KVxyXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQXNmLFNBQVMsb0JBQW9CO0FBQ25oQixPQUFPLFNBQVM7QUFDaEIsT0FBTyxVQUFVO0FBQ2pCLE9BQU8sY0FBYztBQUhyQixJQUFNLG1DQUFtQztBQU16QyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTO0FBQUEsSUFDUCxTQUFTO0FBQUEsTUFDUCxhQUFhO0FBQUEsTUFDYixhQUFhO0FBQUEsSUFDZixDQUFDO0FBQUEsSUFDRCxJQUFJO0FBQUEsRUFDTjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsS0FBSztBQUFBLElBQ3BDO0FBQUEsRUFDRjtBQUFBLEVBQ0EsT0FBTztBQUFBLElBQ0wsUUFBUSxNQUFNLEtBQUssU0FBUyxLQUFLLFFBQVEsSUFBSSxDQUFDLENBQUM7QUFBQSxJQUMvQyxhQUFhO0FBQUEsSUFDYixRQUFRO0FBQUEsRUFDVjtBQUFBLEVBQ0EsY0FBYztBQUFBLElBQ1osU0FBUztBQUFBLE1BQ1A7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
