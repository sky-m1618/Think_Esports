import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/test_api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
