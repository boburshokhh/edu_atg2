import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// Максимально простой Vite config:
// - простой proxy для dev (чтобы /api работало локально)
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET || 'http://localhost:8000'
  const minioTarget = env.VITE_MINIO_TARGET || env.VITE_MINIO_ENDPOINT || 'http://localhost:9000'

  return {
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
          target: minioTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/minio/, ''),
        },
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})
