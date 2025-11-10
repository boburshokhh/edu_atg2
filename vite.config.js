import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api/minio': {
        target: 'https://minio.dmed.gubkin.uz',
        changeOrigin: true,
        secure: true, // Для HTTPS
        rewrite: (path) => path.replace(/^\/api\/minio/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Добавляем необходимые заголовки для MinIO
            proxyReq.setHeader('Host', 'minio.dmed.gubkin.uz')
          })
        }
      }
    }
  },
  optimizeDeps: {
    include: ['pdfjs-dist'],
    exclude: ['pdfjs-dist/build/pdf.worker.min.js'],
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus', '@element-plus/icons-vue'],
        },
      },
    },
  },
  worker: {
    format: 'es',
  },
})
