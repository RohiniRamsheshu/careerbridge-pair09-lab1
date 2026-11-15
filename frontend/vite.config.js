import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@reduxjs/toolkit': fileURLToPath(new URL('./node_modules/@reduxjs/toolkit/dist/redux-toolkit.legacy-esm.js', import.meta.url)),
    },
  },
})
