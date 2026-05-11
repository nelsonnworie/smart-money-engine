import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // <-- DO YOU HAVE THIS?

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // <-- AND THIS?
  ],
})