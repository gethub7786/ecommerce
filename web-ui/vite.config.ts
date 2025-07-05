import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/keystone': 'http://localhost:5000',
      '/catalog': 'http://localhost:5000',
      '/suppliers': 'http://localhost:5000',
      '/tasks': 'http://localhost:5000'
    }
  }
})
