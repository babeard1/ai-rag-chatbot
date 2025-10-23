import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    // NOTE: Current bundle size (~536kB for main chunk) is fine for demo but...
     //
    // Future optimizations to consider:
    // 1. Code-splitting: Use dynamic import() for heavy components
    // 2. Manual chunking: Split MUI components into separate vendor chunk
    // 3. Tree-shaking: Audit and remove unused MUI components.
    // 
    // For production scale, implement build.rollupOptions.output.manualChunks
    // Reference: https://rollupjs.org/configuration-options/#output-manualchunks
    // 
   }
})