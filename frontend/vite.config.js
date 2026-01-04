import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:6002',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../static/carscraper',
    emptyOutDir: true
  }
})

