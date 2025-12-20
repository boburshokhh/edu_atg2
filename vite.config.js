import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

// Простая функция для загрузки env файла
function loadKeyValueEnvFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) return {}
    const content = fs.readFileSync(filePath, 'utf-8')
    const out = {}
    for (const line of content.split(/\r?\n/)) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith('#')) continue
      const idx = trimmed.indexOf('=')
      if (idx === -1) continue
      const key = trimmed.slice(0, idx).trim()
      const value = trimmed.slice(idx + 1).trim()
      if (key) out[key] = value
    }
    return out
  } catch {
    return {}
  }
}

export default defineConfig(() => {
  // Загружаем только необходимые переменные из frontend.env
  const env = loadKeyValueEnvFile(resolve(__dirname, 'frontend.env'))
  
  // Настройки бэкенда
  const apiTarget = env.VITE_API_TARGET || 'http://localhost:8000'
  const minioTarget = env.VITE_MINIO_TARGET || 'http://192.168.32.100:9000'

  return {
    // Переменные окружения для клиента
    define: {
      'import.meta.env.VITE_API_TARGET': JSON.stringify(apiTarget),
      'import.meta.env.VITE_MINIO_TARGET': JSON.stringify(minioTarget),
      'import.meta.env.VITE_MINIO_ENDPOINT': JSON.stringify(env.VITE_MINIO_ENDPOINT || minioTarget),
      'import.meta.env.VITE_MINIO_BUCKET': JSON.stringify(env.VITE_MINIO_BUCKET || 'atgedu'),
      'import.meta.env.VITE_MINIO_ACCESS_KEY': JSON.stringify(env.VITE_MINIO_ACCESS_KEY || ''),
      'import.meta.env.VITE_MINIO_SECRET_KEY': JSON.stringify(env.VITE_MINIO_SECRET_KEY || ''),
      'import.meta.env.VITE_LDAP_ENABLED': JSON.stringify(env.VITE_LDAP_ENABLED || 'false'),
    },
    
    plugins: [
      vue({
        script: {
          defineModel: true,
          propsDestructure: true
        }
      }),
    ],
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    
    server: {
      port: 3000,
      open: true,
      proxy: {
        // Proxy для MinIO (файлы)
        '/api/minio': {
          target: minioTarget,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/minio/, ''),
        },
        // Proxy для Django API (все остальные запросы)
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    
    // Оптимизация зависимостей
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'element-plus',
        '@element-plus/icons-vue',
        'axios',
        'dayjs'
      ],
      exclude: ['pdfjs-dist/build/pdf.worker.min.js'],
    },
    
    // Настройки esbuild
    esbuild: {
      drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
      legalComments: 'none',
      keepNames: true,
    },
    
    build: {
      outDir: 'dist',
      sourcemap: false,
      minify: 'esbuild',
      target: 'es2015',
      cssCodeSplit: true,
      chunkSizeWarningLimit: 1000,
      
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Vue core
            if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
              return 'vue-core'
            }
            // Router & State
            if (id.includes('vue-router') || id.includes('pinia')) {
              return 'router-store'
            }
            // Element Plus
            if (id.includes('node_modules/element-plus')) {
              return 'element-plus'
            }
            // Icons
            if (id.includes('@element-plus/icons-vue') || id.includes('@heroicons')) {
              return 'icons'
            }
            // Video players
            if (id.includes('plyr') || id.includes('video.js') || id.includes('hls.js')) {
              return 'video-player'
            }
            // PDF
            if (id.includes('pdfjs-dist') || id.includes('vue-pdf-embed')) {
              return 'pdf-viewer'
            }
            // Остальные зависимости
            if (id.includes('node_modules')) {
              return 'vendor'
            }
          },
          
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const extType = info[info.length - 1]
            
            // PDF worker в отдельную папку
            if (assetInfo.name.includes('pdf.worker')) {
              return `assets/workers/[name][extname]`
            }
            
            if (/\.(png|jpe?g|svg|gif|webp|avif)$/i.test(assetInfo.name)) {
              return `assets/images/[name]-[hash][extname]`
            }
            
            if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
              return `assets/fonts/[name]-[hash][extname]`
            }
            
            if (/\.css$/i.test(assetInfo.name)) {
              return `assets/css/[name]-[hash][extname]`
            }
            
            return `assets/[ext]/[name]-[hash][extname]`
          },
        },
      },
      
      assetsInlineLimit: 4096,
      reportCompressedSize: false,
    },
    
    performance: {
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    },
    
    worker: {
      format: 'es',
      rollupOptions: {
        output: {
          format: 'es',
        },
      },
    },
  }
})
