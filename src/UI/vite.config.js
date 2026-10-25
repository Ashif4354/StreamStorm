import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import pkg from './package.json'

process.env.VITE_APP_VERSION = pkg.version

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(pkg.version),
  },
  build: {
    sourcemap: true
  }
})
